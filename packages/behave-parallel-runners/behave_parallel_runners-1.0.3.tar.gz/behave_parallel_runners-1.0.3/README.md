# behave-parallel-runners

## Объявление своего раннера

Рекомендуется запуск в несколько процессов, так как:

- При работе в потоках есть проблемы с Allure репортером.
- Для запуска субинтерпретаторов необходима версия python 3.14, что не поддерживается некоторыми зависимостями.

```python
from behave.configuration import Configuration
from behave.runner import ITestRunne

from behave_parallel_runners.runner import ParallelRunner
from behave_parallel_runners.workers import WorkerPoolExecutor
from behave_parallel_runners.workers.process import ProcessWorker
from behave_parallel_runners.tasks import FeatureTaskAllocator

class FeatureParallelRunner(ParallelRunner):
    def __init__(self, config: Configuration):
        super().__init__(
            config=config,
            task_allocator=FeatureTaskAllocator(config),
            worker_pool_executor=WorkerPoolExecutor(config, ProcessWorker),
        )

ITestRunner.register(FeatureParallelRunner)
```