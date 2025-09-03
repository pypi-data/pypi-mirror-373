import argparse
import asyncio
import os
import pathlib

from xum import utils
from xum.fetchers import CustomPaths, Fd, Zoxide
from xum.fzf import Fzf
from xum.tmux import Tmux

APP_NAME = "xum"

zsh_cmp_strings = """
alias x="xum create"
function zle_xumcreate() {
    xum create
    return
}
function zle_xumswitch() {
    xum switch
    return
}

zle -N zle_xumcreate
zle -N zle_xumswitch
bindkey "^B" zle_xumcreate
bindkey "^F" zle_xumswitch
"""


def app():
    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        description="Manage Tmux sessions with fuzzy powers",
    )

    cmd = parser.add_subparsers(required=True)
    parser_create = cmd.add_parser("create", help="create a new session")
    parser_switch = cmd.add_parser("switch", help="switch to a session")
    parser_here = cmd.add_parser("here", help="create session in cwd")
    parser_close = cmd.add_parser("close", help="close sessions")
    parser_zsh = cmd.add_parser("zsh", help="output zsh setup")

    parser_create.set_defaults(func=lambda: asyncio.run(create()))
    parser_switch.set_defaults(func=lambda: asyncio.run(switch()))
    parser_here.set_defaults(func=here)
    parser_close.set_defaults(func=close)
    parser_zsh.set_defaults(func=zsh_completions)

    # setup completions
    zsh = parser.add_argument("--zsh", action="store_true")

    args = parser.parse_args()
    args.func()


async def create():
    # create a queue for passing entries
    queue = asyncio.Queue()

    # create consumer task
    fzf = Fzf()
    await fzf.init()
    consumer = asyncio.create_task(fzf.async_run(queue))

    # define producers
    producers = (Fd(), Zoxide(), CustomPaths())
    for p in producers:
        await p.init()

    # create and execute producer tasks
    async with asyncio.TaskGroup() as group:
        for p in producers:
            group.create_task(p.enqueue(queue))

    # signal consumer to stop looking at the queue
    await queue.put(fzf.STOP)
    await queue.join()

    # prompt for session with fzf
    if selected := await consumer:
        session_path = pathlib.Path(selected.strip()).expanduser().absolute()
        assert session_path.exists()
    else:
        return

    # sanitize session name
    session_name = utils.session_name(session_path)

    # create tmux interface
    tmux = Tmux()

    # check if session already exists
    if session_name not in tmux.sessions():
        assert session_path.is_absolute()
        tmux.create_session(session_name, basedir=str(session_path))

    # switch client or attach to new session
    if os.getenv("TMUX"):
        tmux.switch_client(session_name)
    else:
        tmux.attach_session(session_name)


async def switch():
    # connect to tmux server
    queue = asyncio.Queue()

    # create consumer task
    fzf = Fzf()
    await fzf.init()
    consumer = asyncio.create_task(fzf.async_run(queue))

    # create tmux interface
    tmux = Tmux()

    # create and execute producer tasks
    async with asyncio.TaskGroup() as group:
        group.create_task(tmux.enqueue_sessions(queue))

    # signal consumer to stop looking at the queue
    await queue.put(fzf.STOP)
    await queue.join()

    session_name = await consumer
    if not session_name:
        return

    # switch client or attach to new session
    if os.getenv("TMUX"):
        tmux.switch_client(session_name)
    else:
        tmux.attach_session(session_name)


def close():
    # connect to tmux server
    tmux = Tmux()

    # init fzf object
    fzf = Fzf()

    selected = fzf.run(tmux.sessions())

    for name in selected:
        print(f"XUM: quitting session '{name.strip()}'")
        assert name in tmux.sessions()
        tmux.kill_session(name.strip())


def here():
    # get tmux interface
    tmux = Tmux()

    session_path = pathlib.Path().absolute()
    assert session_path.exists()

    session_name = utils.session_name(session_path).strip()

    if session_name not in tmux.sessions():
        tmux.create_session(session_name, basedir=str(session_path))

    if os.getenv("TMUX"):
        tmux.switch_client(session_name)
    else:
        tmux.attach_session(session_name)


def zsh_completions():
    # output zsh completions
    print(zsh_cmp_strings)
