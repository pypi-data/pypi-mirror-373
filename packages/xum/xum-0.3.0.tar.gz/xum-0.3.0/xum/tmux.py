import asyncio
import subprocess


class Tmux:
    def __init__(self):
        pass

    async def enqueue_sessions(self, queue: asyncio.Queue):
        args = ("tmux", "list-sessions", "-F", "#{session_name}")
        proc = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE
        )

        assert proc.stdout
        async for line in proc.stdout:
            await queue.put((line.decode().strip(), line.decode().strip()))

    def sessions(self):
        args = ("tmux", "list-sessions", "-F", "#{session_name}")
        proc = subprocess.Popen(args, stdout=asyncio.subprocess.PIPE)

        assert proc.stdout
        for line in proc.stdout:
            yield line.decode().strip()

    def create_session(self, name: str, basedir: str):
        args = ("tmux", "new-session", "-d", "-c", basedir, "-s", name)
        subprocess.call(args)

    def switch_client(self, name: str):
        args = ("tmux", "switch-client", "-t", name)
        subprocess.call(args)

    def attach_session(self, name: str):
        args = ("tmux", "a", "-t", name)
        subprocess.call(args)

    def kill_session(self, name: str):
        args = ("tmux", "kill-session", "-t", name)
        subprocess.call(args)
