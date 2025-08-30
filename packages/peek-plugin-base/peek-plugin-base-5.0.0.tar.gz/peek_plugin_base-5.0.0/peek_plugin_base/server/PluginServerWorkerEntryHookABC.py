from abc import ABCMeta
from abc import abstractproperty


class PluginServerWorkerEntryHookABC(metaclass=ABCMeta):

    @abstractproperty
    def workerTaskImports(self) -> [str]:
        """Peek Worker Task Imports

        This property returns the absolute package paths to the modules with the
        tasks
        :Example: ["plugin_noop.worker.NoopWorkerTask"]

        :return: A list of package+module names that Peek should import.

        """
