import threading
import weakref
from concurrent.futures import _base
from concurrent.futures.thread import ThreadPoolExecutor, _shutdown, _threads_queues


# This is a copy of the original _worker function from the concurrent.futures.thread module,
# with the addition of a 'finally' block to call the finalizer.
def _finalizing_worker(executor_reference, work_queue, initializer, initargs, finalizer, finalizer_args):
    """
    A custom worker function that adds a finalizer call to the original
    concurrent.futures.thread._worker.
    """
    if initializer is not None:
        try:
            initializer(*initargs)
        except BaseException:
            _base.LOGGER.critical("Exception in initializer:", exc_info=True)
            executor = executor_reference()
            if executor is not None:
                executor._initializer_failed()
            return
    try:
        while True:
            work_item = work_queue.get(block=True)
            if work_item is not None:
                work_item.run()
                # Delete references to object. See issue16284
                del work_item

                # attempt to increment idle count
                executor = executor_reference()
                if executor is not None:
                    executor._idle_semaphore.release()
                del executor
                continue

            executor = executor_reference()
            # Exit if:
            # - The interpreter is shutting down OR
            # - The executor that owns the worker has been collected OR
            # - The executor that owns the worker has been shutdown.
            if _shutdown or executor is None or executor._shutdown:
                # Flag the executor as shutting down as early as possible if it
                # is not gc-ed yet.
                if executor is not None:
                    executor._shutdown = True
                # Notice other workers
                work_queue.put(None)
                return
            del executor
    except BaseException:
        _base.LOGGER.critical("Exception in worker", exc_info=True)
    finally:
        if finalizer is not None:
            try:
                finalizer(*finalizer_args)
            except BaseException:
                _base.LOGGER.critical("Exception in finalizer:", exc_info=True)


class FinalizingThreadPoolExecutor(ThreadPoolExecutor):
    """
    A ThreadPoolExecutor that extends the standard library version to support
    a `finalizer` and `finalizer_args` for each worker thread.
    """

    def __init__(
        self, max_workers=None, thread_name_prefix="", initializer=None, initargs=(), finalizer=None, finalizer_args=()
    ):
        # Call the original __init__
        super().__init__(max_workers, thread_name_prefix, initializer, initargs)
        self._finalizer = finalizer
        self._finalizer_args = finalizer_args

    def _adjust_thread_count(self):
        # This method is an overridden version of the original.
        # The key change is that it targets our `_custom_worker`
        # and passes the finalizer arguments to it.

        # if idle threads are available, don't spin new threads
        if self._idle_semaphore.acquire(timeout=0):
            return

        # When the executor gets lost, the weakref callback will wake up
        # the worker threads.
        def weakref_cb(_, q=self._work_queue):
            q.put(None)

        num_threads = len(self._threads)
        if num_threads < self._max_workers:
            thread_name = "%s_%d" % (self._thread_name_prefix or self, num_threads)

            # *** The key change is here ***
            # We target `_custom_worker` instead of the original `_worker`
            # and pass the additional finalizer arguments.
            t = threading.Thread(
                name=thread_name,
                target=_finalizing_worker,
                args=(
                    weakref.ref(self, weakref_cb),
                    self._work_queue,
                    self._initializer,
                    self._initargs,
                    self._finalizer,
                    self._finalizer_args,
                ),
            )
            t.start()
            self._threads.add(t)
            _threads_queues[t] = self._work_queue


# # Example Usage:
# if __name__ == '__main__':
#     import time
#     # A thread-local object to demonstrate initializer/finalizer context
#     local_data = threading.local()
#     def initializer(thread_name):
#         local_data.name = thread_name
#         local_data.session_id = os.urandom(4).hex()
#         print(f"[{local_data.name}] Initialized session: {local_data.session_id}")
#     def finalizer():
#         print(f"[{local_data.name}] Finalizing session: {local_data.session_id}")
#         # Here you would put cleanup logic, like closing database connections or sessions
#         del local_data.name
#         del local_data.session_id

#     def worker_task(task_id):
#         # The worker can access the thread-local data set up by the initializer
#         print(f"[{local_data.name}] Running task {task_id} with session {local_data.session_id}")
#         time.sleep(0.5)
#         print(f"[{local_data.name}] Finished task {task_id}")
#     print("Starting CustomThreadPoolExecutor...")
#     # Use the custom executor
#     with CustomThreadPoolExecutor(
#         max_workers=2,
#         initializer=initializer,
#         initargs=(threading.current_thread().name,), # Note: this will be the main thread's name
#         finalizer=finalizer
#     ) as executor:
#         # Submit some tasks
#         for i in range(4):
#             executor.submit(worker_task, i)

#     print("Executor has shut down.")
