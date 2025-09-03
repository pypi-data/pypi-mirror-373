import abc
import asyncio
import pathlib

from xum.config import config
from xum.utils import minify_path


class Producer(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    async def enqueue(self, queue):
        pass

    async def init(self):
        pass


class ProducerProcess(Producer):
    def __init__(self):
        self.args: list
        self.proc: asyncio.subprocess.Process

    async def init(self):
        self.proc = await asyncio.subprocess.create_subprocess_exec(
            *self.args, stdout=asyncio.subprocess.PIPE
        )

    async def enqueue(self, queue):
        # get paths from stdout
        assert self.proc.stdout
        async for line in self.proc.stdout:
            str_line = line.decode().strip()
            path = pathlib.Path(str_line).expanduser().absolute()
            await queue.put((path, minify_path(path)))


class Fd(ProducerProcess):
    def __init__(self):
        self.args = ["fd", "-t", "d", "-t", "l", "-d", "1"]
        for path in config.search_paths:
            self.args.extend(("--search-path", str(path)))


class Zoxide(ProducerProcess):
    def __init__(self):
        self.args = ["zoxide", "query", "--list"]


class CustomPaths(Producer):
    def __init__(self):
        pass

    async def enqueue(self, queue):
        for path in config.custom_paths:
            await queue.put((path, minify_path(path)))


class SearchPaths(Producer):
    def __init__(self):
        pass

    async def enqueue(self, queue):
        pass
