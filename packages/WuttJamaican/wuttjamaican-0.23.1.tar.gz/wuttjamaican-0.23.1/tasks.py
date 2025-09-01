# -*- coding: utf-8; -*-
"""
Tasks for WuttJamaican
"""

import os
import shutil

from invoke import task


@task
def release(c, skip_tests=False):
    """
    Release a new version of WuttJamaican
    """
    if not skip_tests:
        c.run("pytest")

    # rebuild local tar.gz file for distribution
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("WuttJamaican.egg-info"):
        shutil.rmtree("WuttJamaican.egg-info")
    c.run("python -m build --sdist")

    # upload to PyPI
    c.run("twine upload dist/*")
