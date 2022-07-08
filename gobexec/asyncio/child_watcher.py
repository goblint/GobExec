import os
import resource
from asyncio import ThreadedChildWatcher
from asyncio.log import logger
from asyncio.unix_events import _compute_returncode

# based on https://www.enricozini.org/blog/2019/debian/getting-rusage-of-child-processes-on-python-s-asyncio/
from typing import Dict


class RusageThreadedChildWatcher(ThreadedChildWatcher):
    rusages: Dict[int, resource.struct_rusage] = {}

    # copied from unix_events.ThreadedChildWatcher on Python 3.9.7
    def _do_waitpid(self, loop, expected_pid, callback, args):
        assert expected_pid > 0

        try:
            pid, status, rusage = os.wait4(expected_pid, 0)  # modified waitpid -> wait4
            self.rusages[expected_pid] = rusage
        except ChildProcessError:
            # The child process is already reaped
            # (may happen if waitpid() is called elsewhere).
            pid = expected_pid
            returncode = 255
            logger.warning(
                "Unknown child process pid %d, will report returncode 255",
                pid)
        else:
            returncode = _compute_returncode(status)
            if loop.get_debug():
                logger.debug('process %s exited with returncode %s',
                             expected_pid, returncode)

        if loop.is_closed():
            logger.warning("Loop %r that handles pid %r is closed", loop, pid)
        else:
            loop.call_soon_threadsafe(callback, pid, returncode, *args)

        self._threads.pop(expected_pid)
