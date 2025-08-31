def addPeekWorkerTask(retries: int = 0):
    from peek_worker_service.peek_worker_task import peekWorkerTaskDecorator

    return peekWorkerTaskDecorator(retries=retries)
