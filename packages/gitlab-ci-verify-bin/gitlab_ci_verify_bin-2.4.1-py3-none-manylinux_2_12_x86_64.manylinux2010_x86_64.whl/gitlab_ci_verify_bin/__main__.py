import os, sys, subprocess
sys.exit(subprocess.call([
    os.path.join(os.path.dirname(__file__), "gitlab-ci-verify"),
    *sys.argv[1:]
]))
