import asyncio
import subprocess
from contextlib import redirect_stdout


class Fzf:
    def __init__(self, *opts):
        self.proc: asyncio.subprocess.Process
        self.args = ["fzf", "--tmux", *opts]
        self.STOP = None

    def run(self, choices):
        cmd = subprocess.Popen(
            self.args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
        )

        with redirect_stdout(cmd.stdin):
            for entry in choices:
                print(entry, flush=True)

        if cmd.stdin:
            cmd.stdin.close()

        if cmd.stdout:
            return cmd.stdout.read().strip().splitlines()

        return []

    async def init(self):
        self.proc = await asyncio.subprocess.create_subprocess_exec(
            *self.args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
        )

    async def async_run(self, queue: asyncio.Queue):
        pulled = set()
        assert self.proc.stdin
        while True:
            # get element from queue
            item = await queue.get()
            # break if stop signal
            if item is self.STOP:
                queue.task_done()
                break

            # unpack element as identifier and content
            identifier, content = item
            if identifier not in pulled:
                pulled.add(identifier)
                self.proc.stdin.write(f"{content}\n".encode())
                await self.proc.stdin.drain()

            queue.task_done()

        self.proc.stdin.write_eof()

        assert self.proc.stdout
        selected = await self.proc.stdout.readline()
        return selected.decode().strip()
