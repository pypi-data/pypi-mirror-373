import os
import sys
import errno

from django.conf import settings
from django.core.files import locks


class FileLock:

    class LockFailedException(Exception):
        pass

    def __init__(self, cron_class, silent, *args, **kwargs):
        """
        This method inits the class.
        You should take care of getting all
        nessesary thing from input parameters here
        Base class processes
            * self.job_name
            * self.job_code
            * self.parallel
            * self.silent
        for you. The rest is backend-specific.
        """
        self.job_name = cron_class.code
        self.job_code = cron_class.code
        self.parallel = getattr(cron_class, 'ALLOW_PARALLEL_RUNS', False)
        self.silent = silent

    def lock(self):
        try:
            lock_name = self.get_lock_name()
            # need loop to avoid races on file unlinking
            while True:
                f = open(lock_name, 'wb+', 0)
                locks.lock(f, locks.LOCK_EX | locks.LOCK_NB)
                # Here is the Race:
                # Previous process "A" is still running. Process "B" opens
                # the file and then the process "A" finishes and deletes it.
                # "B" locks the deleted file (by fd it already have) and runs,
                # then the next process "C" creates _new_ file and locks it
                # successfully while "B" is still running.
                # We just need to check that "B" didn't lock a deleted file
                # to avoid any problems. If process "C" have locked
                # a new file wile "B" stats it then ok, let "B" quit and "C"
                # run. We can still meet an attacker that permanently
                # creates and deletes our file but we can't avoid problems
                # in that case.
                if os.path.isfile(lock_name):
                    st1 = os.fstat(f.fileno())
                    st2 = os.stat(lock_name)
                    if st1.st_ino == st2.st_ino:
                        f.write(bytes(str(os.getpid()).encode('utf-8')))
                        self.lockfile = f
                        return True
                # else:
                # retry. Don't unlink, next process might already use it.
                f.close()

        except IOError as e:
            if e.errno in (errno.EACCES, errno.EAGAIN):
                return False
            else:
                e = sys.exc_info()[1]
                raise e
        # TODO: perhaps on windows I need to catch different exception type

    def release(self):
        f = self.lockfile
        # unlink before release lock to avoid race
        # see comment in self.lock for description
        os.unlink(f.name)
        f.close()

    def get_lock_name(self):
        default_path = '/tmp'
        path = getattr(settings, 'DJANGO_CRON_LOCKFILE_PATH', default_path)
        if not os.path.isdir(path):
            # let it die if failed, can't run further anyway
            os.makedirs(path)

        filename = self.job_name + '.lock'
        return os.path.join(path, filename)

    def lock_failed_message(self):
        return "%s: lock found. Will try later." % self.job_name

    def __enter__(self):
        if self.parallel:
            return
        else:
            if not self.lock():
                raise self.LockFailedException(self.lock_failed_message())

    def __exit__(self, type, value, traceback):
        if not self.parallel:
            self.release()
