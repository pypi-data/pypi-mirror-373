import random
from typing import override

from amsatop._htop.htop import Htop
from amsatop._htop.process import Process, Type


class HtopMock(Htop):
    """
    Mock implementation of the Htop interface for testing or demonstration purposes.

    This class simulates process information by returning hardcoded `Process` instances.
    Each method (`get_processes`, `get_priorities`, `get_hup`) returns a random subset
    of predefined mock processes.

    Useful for testing code that depends on Htop without requiring access to the actual
    system process tree.
    """

    RETURN_PROCESSES = 5

    @override
    def get_processes(self) -> list[Process]:
        not_real_processes = [
            Process(pid=1, command="init", type=Type.TASK, priority=None),
            Process(pid=2, command="bash", type=Type.THREAD, priority=None),
            Process(pid=3, command="kworker", type=Type.KTHREAD, priority=None),
            Process(pid=4, command="python", type=Type.TASK, priority=None),
            Process(pid=5, command="top", type=Type.THREAD, priority=None),
            Process(pid=6, command="_htop", type=Type.TASK, priority=None),
            Process(pid=7, command="systemd", type=Type.KTHREAD, priority=None),
            Process(pid=8, command="tmux", type=Type.THREAD, priority=None),
            Process(pid=9, command="node", type=Type.TASK, priority=None),
            Process(pid=10, command="java", type=Type.KTHREAD, priority=None),
            Process(pid=11, command="emacs", type=Type.THREAD, priority=None),
            Process(pid=12, command="vim", type=Type.TASK, priority=None),
            Process(pid=13, command="zsh", type=Type.THREAD, priority=None),
            Process(pid=14, command="docker", type=Type.KTHREAD, priority=None),
        ]
        return random.sample(
            not_real_processes, min(self.RETURN_PROCESSES, len(not_real_processes))
        )

    @override
    def get_priorities(self) -> list[Process]:
        not_real_processes = [
            Process(pid=15, command="sshd", type=Type.TASK, priority=10),
            Process(pid=16, command="nginx", type=Type.THREAD, priority=5),
            Process(pid=17, command="postgres", type=Type.KTHREAD, priority=1),
            Process(pid=18, command="redis", type=Type.TASK, priority=7),
            Process(pid=19, command="chrome", type=Type.THREAD, priority=8),
            Process(pid=20, command="firefox", type=Type.TASK, priority=6),
            Process(pid=21, command="docker", type=Type.KTHREAD, priority=3),
            Process(pid=22, command="mysql", type=Type.TASK, priority=9),
            Process(pid=23, command="emacs", type=Type.THREAD, priority=4),
            Process(pid=24, command="vim", type=Type.TASK, priority=2),
            Process(pid=25, command="zsh", type=Type.THREAD, priority=5),
            Process(pid=26, command="python", type=Type.TASK, priority=7),
            Process(pid=27, command="java", type=Type.KTHREAD, priority=6),
        ]
        return random.sample(
            not_real_processes, min(self.RETURN_PROCESSES, len(not_real_processes))
        )

    @override
    def get_hup(self) -> list[Process]:
        not_real_processes = [
            Process(pid=28, command="sshd", type=Type.TASK, priority=10),
            Process(pid=29, command="nginx", type=Type.THREAD, priority=5),
            Process(pid=30, command="postgres", type=Type.KTHREAD, priority=1),
            Process(pid=31, command="redis", type=Type.TASK, priority=7),
            Process(pid=32, command="chrome", type=Type.THREAD, priority=8),
            Process(pid=33, command="firefox", type=Type.TASK, priority=6),
            Process(pid=34, command="docker", type=Type.KTHREAD, priority=3),
            Process(pid=35, command="mysql", type=Type.TASK, priority=9),
            Process(pid=36, command="emacs", type=Type.THREAD, priority=4),
            Process(pid=37, command="vim", type=Type.TASK, priority=2),
            Process(pid=38, command="zsh", type=Type.THREAD, priority=5),
            Process(pid=39, command="python", type=Type.TASK, priority=7),
            Process(pid=40, command="java", type=Type.KTHREAD, priority=6),
        ]
        return random.sample(
            not_real_processes, min(self.RETURN_PROCESSES, len(not_real_processes))
        )
