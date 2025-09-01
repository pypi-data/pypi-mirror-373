import os

HOME_DIR = os.path.expanduser("~")
RUN_DIR = "/run/user/%d/" % os.getuid()
