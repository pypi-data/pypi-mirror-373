from yxutil.os import mkdir, rmdir, have_file, if_file_in_directory, ln_file, get_file_name
from yxutil.config import RUN_DIR
import os
import uuid
import warnings


class JOB(object):
    def __init__(self, job_id=None, work_dir=None, clean=True, force=False):
        self.job_id = job_id
        self.clean = clean
        self.work_dir = work_dir
        self.force = force

    def build_env(self):
        # build work dir
        if self.work_dir:
            self.work_dir = os.path.abspath(self.work_dir)
        elif self.clean:
            self.work_dir = os.path.join(RUN_DIR, str(uuid.uuid4()))
            self.tmp_work_dir_flag = True
        else:
            self.work_dir = os.path.abspath(os.path.curdir)

        if self.force:
            if have_file(self.work_dir):
                warnings.warn(
                    "Work dir %s already exists, will be removed!" % self.work_dir)
                mkdir(self.work_dir)
        else:
            mkdir(self.work_dir, True)

    def clean_env(self):
        if self.clean:
            rmdir(self.work_dir)

    def file_attr_check(self, file_name, attr_name):
        setattr(self, attr_name, os.path.abspath(
            file_name) if file_name else None)

        if getattr(self, attr_name):
            if not if_file_in_directory(getattr(self, attr_name), self.work_dir):
                ln_file(getattr(self, attr_name), self.work_dir)
                setattr(self, attr_name, os.path.join(
                    self.work_dir, get_file_name(getattr(self, attr_name))))


if __name__ == '__main__':
    pass
