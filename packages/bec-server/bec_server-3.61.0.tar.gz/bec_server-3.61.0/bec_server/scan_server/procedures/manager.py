from __future__ import annotations

import atexit
from concurrent import futures
from concurrent.futures import Future, ThreadPoolExecutor
from threading import RLock
from typing import Any, TypedDict

from pydantic import ValidationError

from bec_lib.endpoints import MessageEndpoints
from bec_lib.logger import bec_logger
from bec_lib.messages import ProcedureRequestMessage, RequestResponseMessage
from bec_lib.redis_connector import RedisConnector
from bec_server.scan_server.procedures.exceptions import WorkerAlreadyExists
from bec_server.scan_server.procedures.procedure_registry import PROCEDURE_LIST
from bec_server.scan_server.procedures.worker_base import ProcedureWorker
from bec_server.scan_server.scan_server import ScanServer

logger = bec_logger.logger

MAX_WORKERS = 10
queue_TIMEOUT_S = 10
MANAGER_SHUTDOWN_TIMEOUT_S = 2
DEFAULT_QUEUE = "primary"


class ProcedureWorkerEntry(TypedDict):
    worker: ProcedureWorker | None
    future: Future


class ProcedureManager:

    def __init__(self, parent: ScanServer, worker_type: type[ProcedureWorker]):
        """Watches the request queue and pushes to worker execution queues. Manages
        instantiating and cleaning up after workers.

        Args:
            parent (ScanServer): the scan server to get the Redis server address from.
            worker_type (type[ProcedureWorker]): which kind of worker to use."""

        self._parent = parent
        self.lock = RLock()
        self.active_workers: dict[str, ProcedureWorkerEntry] = {}
        self.executor = ThreadPoolExecutor(
            max_workers=MAX_WORKERS, thread_name_prefix="user_procedure_"
        )
        atexit.register(self.executor.shutdown)

        self._worker_cls = worker_type
        self._conn = RedisConnector([self._parent.bootstrap_server])
        self._reply_endpoint = MessageEndpoints.procedure_request_response()
        self._server = f"{self._conn.host}:{self._conn.port}"

        self._conn.register(MessageEndpoints.procedure_request(), None, self.process_queue_request)

    def _ack(self, accepted: bool, msg: str):
        logger.debug(f"procedure accepted: {accepted}, message: {msg}")
        self._conn.send(
            self._reply_endpoint, RequestResponseMessage(accepted=accepted, message=msg)
        )

    def _validate_request(self, msg: dict[str, Any]):
        try:
            message_obj = ProcedureRequestMessage.model_validate(msg)
            if message_obj.identifier not in PROCEDURE_LIST.keys():
                self._ack(
                    False,
                    f"Procedure {message_obj.identifier} not known to the server. Available: {list(PROCEDURE_LIST.keys())}",
                )
                return None
        except ValidationError as e:
            self._ack(False, f"{e}")
            return None
        return message_obj

    def process_queue_request(self, msg: dict[str, Any]):
        """Read a `ProcedureRequestMessage` and if it is valid, create a corresponding `ProcedureExecutionMessage`.
        If there is already a worker for the queue for that request message, add the execution message to that queue,
        otherwise create a new queue and a new worker.

        Args:
            msg (dict[str, Any]): dict corresponding to a ProcedureRequestMessage"""

        logger.debug(f"Procedure manager got request message {msg}")
        if (message_obj := self._validate_request(msg)) is None:
            return
        self._ack(True, f"Running procedure {message_obj.identifier}")
        queue = message_obj.queue or DEFAULT_QUEUE
        endpoint = MessageEndpoints.procedure_execution(queue)
        logger.debug(f"active workers: {self.active_workers}, worker requested: {queue}")
        self._conn.rpush(
            endpoint,
            endpoint.message_type(
                identifier=message_obj.identifier,
                queue=queue,
                args_kwargs=message_obj.args_kwargs or ((), {}),
            ),
        )
        with self.lock:
            if queue not in self.active_workers:
                new_worker = self.executor.submit(self.spawn, queue=queue)
                self.active_workers[queue] = {"worker": None, "future": new_worker}

    def spawn(self, queue: str):
        """Spawn a procedure worker future which listens to a given queue, i.e. procedure queue list in Redis.

        Args:
            queue (str): name of the queue to spawn a worker for"""

        if queue in self.active_workers and self.active_workers[queue]["worker"] is not None:
            raise WorkerAlreadyExists(
                f"Queue {queue} already has an active worker in {self.active_workers}!"
            )
        with self._worker_cls(self._server, queue) as worker:
            with self.lock:
                self.active_workers[queue]["worker"] = worker
            worker.work()
        with self.lock:
            logger.debug(f"cleaning up worker {queue}...")
            del self.active_workers[queue]

    def shutdown(self):
        """Shutdown the procedure manager. Unregisters from the request endpoint, cancel any
        procedure workers which haven't started, and abort any which have."""
        self._conn.unregister(
            MessageEndpoints.procedure_request(), None, self.process_queue_request
        )
        self._conn.shutdown()
        # cancel futures by hand to give us the opportunity to detatch them from redis if they have started
        for entry in self.active_workers.values():
            cancelled = entry["future"].cancel()
            if not cancelled:
                # unblock any waiting workers and let them shutdown
                if worker := entry["worker"]:
                    # redis unblock executor.client_id
                    worker.abort()
        futures.wait(
            (entry["future"] for entry in self.active_workers.values()),
            timeout=MANAGER_SHUTDOWN_TIMEOUT_S,
        )
        self.executor.shutdown()
