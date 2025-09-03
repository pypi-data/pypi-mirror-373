import asyncio
import pathlib

SIGNAL = None


async def select_new_session():
    """
    Async selector for Tmux sessions. Uses all producers: fd, zoxide, custom paths.
    """
    queue = asyncio.Queue()

    # create consumer task
    consumer = asyncio.create_task(fzf_consumer(queue))

    # create and execute producer tasks
    async with asyncio.TaskGroup() as group:
        group.create_task(fd_producer(queue))
        group.create_task(zoxide_producer(queue))
        group.create_task(custompath_producer(queue))

    # signal consumer to stop looking at the queue
    await queue.put(SIGNAL)
    await queue.join()

    # retrieve output
    return await consumer


async def select_existing_session():
    """
    Async selector for existing Tmux sessions.
    """
    queue = asyncio.Queue()

    # create consumer task
    consumer = asyncio.create_task(fzf_consumer(queue))

    # create and execute producer tasks
    async with asyncio.TaskGroup() as group:
        group.create_task(tmuxsessions_producer(queue))

    # signal consumer to stop looking at the queue
    await queue.put(SIGNAL)
    await queue.join()

    # retrieve output
    return await consumer


def minify_path(path: pathlib.Path) -> str:
    """Replace /home/$USER with ~ in a path"""

    home = pathlib.Path.home()
    if home in path.parents:
        item = f"~/{str(path.relative_to(home))}"
    else:
        item = str(path)
    return item


def session_name(session_path: pathlib.Path) -> str:
    """Sanitize `session_path` and create a session name using the basename"""
    # keep only basename
    name = session_path.name
    replace_dict = {".": "-", "/": "-", " ": "-"}
    for old, new in replace_dict.items():
        name = name.replace(old, new)

    return name
