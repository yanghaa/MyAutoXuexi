from subprocess import call
import pkg_resources

dists = [d for d in pkg_resources.working_set]
for dist in dists:
    call("pip install --upgrade " + dist.project_name, shell=True)
