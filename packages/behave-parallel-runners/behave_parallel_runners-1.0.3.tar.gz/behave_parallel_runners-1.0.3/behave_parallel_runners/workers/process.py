import os
from typing import Optional
from multiprocessing import Process, JoinableQueue
from queue import Empty
from logging import getLogger

from behave.model import Feature
from behave.configuration import Configuration

from . import QUEUE_WAIT_TIMEOUT_IN_SEC, WORKER_TERMINATE_TIMEOUT_IN_SEC, Worker

log = getLogger(__name__)


class ProcessWorker(Worker):
    """Реализация воркера на основе отдельного процесса (multiprocessing).
    Основные функции:
    - Выполнение фичей в изолированном процессе
    - Использование очереди задач для управления выполнением
    - Поддержка дочерних процессов с возможностью завершения
    """

    _process: Process
    _task_queue: JoinableQueue

    def __init__(self, config: Configuration, index: int):
        """Инициализация воркера с новым процессом.
        Args:
            config: Конфигурация из Behave
            index: Индекс воркера
        """
        super().__init__(config, index)
        self._process = Process(
            target=self._process_loop,
            args=(os.environ.copy(),),
            name=str(self),
            daemon=True,
        )
        self._task_queue = JoinableQueue()
        self._process.start()

    def run_feature(self, feature: Optional[Feature]) -> None:
        """Добавляем фичу в очередь задач.
        Args:
            feature: Объект Feature для выполнения или None для завершения
        """
        if not self.is_alive():
            log.warning(
                f"{str(self)} не активен. Feature '{feature.name}' не будет выполнена"
            )
            return
        self._task_queue.put_nowait(feature)

    def done(self) -> bool:
        return self._task_queue._unfinished_tasks._semlock._is_zero()

    def is_alive(self) -> bool:
        return self._process.is_alive()

    def shutdown(self):
        """Завершение работы воркера.
        Отправляет сигнал завершения и ждёт окончания процесса с таймаутом.
        """
        log.debug(f"{str(self)}: запущено завершение работы")
        if self.is_alive():
            self._task_queue.put_nowait(None)  # Сигнал завершения
            self._process.join(timeout=WORKER_TERMINATE_TIMEOUT_IN_SEC)
            if self.is_alive():
                log.debug(f"{str(self)} все еще активен. Принудительное завершение...")
                self._process.terminate()
                self._process.join(timeout=WORKER_TERMINATE_TIMEOUT_IN_SEC)
        self._task_queue.close()
        log.debug(f"{str(self)}: завершение работы выполнено")

    def setup_runtime(self):
        """Доп настройка окружения в каждом процессе воркера (при необходимости)
        Поведение определяется в классе-наследнике"""
        pass

    def _process_loop(self, envs):
        """Основной цикл работы воркера.
        Инициализирует окружение и выполняет задачи из очереди.
        Args:
            envs: Переменные окружения родительского процесса
        """
        os.environ.update(envs)
        self.setup_runtime()
        self.runner.config.setup_formats()
        while True:
            try:
                feature = self._task_queue.get(timeout=QUEUE_WAIT_TIMEOUT_IN_SEC)

                self.runner.run_feature(feature)
                self._task_queue.task_done()

                if self.runner._is_finished:
                    break

            except Empty:
                continue
