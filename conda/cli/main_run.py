# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from logging import getLogger
import os
from subprocess import Popen
import sys

from ..base.context import context
from ..utils import wrap_subprocess_call
from ..gateways.disk.delete import rm_rf
from ..common.compat import encode_environment


def execute(args, parser):
    on_win = sys.platform == "win32"

    call = args.executable_call
    cwd = args.cwd
    prefix = context.target_prefix or os.getenv("CONDA_PREFIX") or context.root_prefix

    script_caller, command_args = wrap_subprocess_call(on_win, context.root_prefix, prefix,
                                                       args.dev, args.debug_wrapper_scripts, call)
    env = encode_environment(os.environ.copy())
    process = Popen(command_args, universal_newlines=False,
                    env=env, cwd=cwd)
    process.wait()
    if process.returncode != 0:
        log = getLogger(__name__)
        log.error("Subprocess for 'conda run {}' command failed.  (See above for error)"
                  .format(call))
    if script_caller is not None:
        if 'CONDA_TEST_SAVE_TEMPS' not in os.environ:
            rm_rf(script_caller)
        else:
            log = getLogger(__name__)
            log.warning('CONDA_TEST_SAVE_TEMPS :: retaining main_run script_caller {}'.format(
                script_caller))
    return process.returncode
