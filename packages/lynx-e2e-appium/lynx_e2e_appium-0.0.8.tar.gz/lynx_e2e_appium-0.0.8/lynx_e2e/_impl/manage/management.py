# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import os
import sys
import argparse
import inspect

from .case_runner import BasicTestRunner
from .loader import TestSuite
from ..exception import ManagementException


class ArgumentParser(object):
    """argument parser
    """
    USAGE = """Usage: %(ProgramName)s subcommand [options] [args]

Options:
  -h, --help            show this help message and exit

Type '%(ProgramName)s help <subcommand>' for help on a specific subcommand.

Available subcommands:

%(SubcmdList)s

"""

    def __init__(self, subcmd_classes):
        self.subcmd_classes = subcmd_classes
        self.prog = os.path.basename(sys.argv[0])

    def parse_args(self, args):
        """parse arguments
        """
        if len(args) < 1:
            sys.exit(1)

        subcmd = args[0]
        for it in self.subcmd_classes:
            if it.name == subcmd:
                subcmd_class = it
                parser = it.parser
                break
        else:
            raise Exception("invalid subcommand \"%s\"\n" % subcmd)

        ns = parser.parse_args(args[1:])
        subcmd = subcmd_class()
        subcmd.main_parser = self
        return subcmd, ns

    def get_subcommand(self, name):
        """get sub command
        """
        for it in self.subcmd_classes:
            if it.name == name:
                return it()


class Command(object):
    """a command
    """
    name = None
    parser = None

    def execute(self, args):
        raise NotImplementedError()

class RunTest(Command):
    """run testcases
    """
    name = 'runtest'
    parser = argparse.ArgumentParser("Run testcases")
    parser.add_argument("tests", metavar="TEST", nargs='*',
                        help="testcase set to executive, eg: zoo.xxx.HelloTest")
    parser.add_argument("--included-pattern", help="include test cases with specific name pattern , accept multiple options",
                        action="append", dest="included_patterns", metavar="INCLUDED_PATTERN")
    parser.add_argument("--excluded-pattern", help="exclude test cases with specific name pattern, accept multiple options",
                        action="append", dest="excluded_patterns", metavar="EXCLUDED_PATTERN")
    parser.add_argument("--owner", help="run test cases with specific owner, accept multiple options",
                        action="append", dest="owners", metavar="OWNER")

    parser.add_argument("--report-type", help="report type", default="stream")
    parser.add_argument(
        "--report-args", help="additional arguments for specific report", default="")
    parser.add_argument(
        "--runner-args", help="additional arguments for specific runner", default="")
    parser.add_argument(
        "--exit-gracefully",
        action="store_true",
        default=False,
        help="don't invoke sys.exit() to avoid throwing SystemExit")

    def execute(self, args):
        if not args.tests:
            sys.exit(1)

        args.working_dir = os.getcwd()
        prev_dir = os.getcwd()
        if not os.path.exists(args.working_dir):
            os.makedirs(args.working_dir)

        try:
            os.chdir(args.working_dir)

            test_suite = TestSuite(tests=args.tests,
                                   owners=args.owners,
                                   included_patterns=args.included_patterns,
                                   excluded_patterns=args.excluded_patterns)

            runner_type = BasicTestRunner
            runner = runner_type.parse_args([], None)
            runner.run_tests(test_suite)
        finally:
            os.chdir(prev_dir)


class ManagementTools(object):
    """management tools
    """

    def _load_cmds(self):
        """load all cmds
        """
        cmds = []
        cmds += self._load_cmd_from_module(sys.modules[__name__])
        return cmds

    def _load_cmd_from_module(self, mod):
        """load cmds from a single module
        """
        cmds = []
        for objname in dir(mod):
            obj = getattr(mod, objname)
            if not inspect.isclass(obj):
                continue
            if obj == Command:
                continue
            if issubclass(obj, Command):
                cmds.append(obj)

        cmds.sort(key=lambda x: x.name)
        return cmds

    def run(self):
        """execution entry
        """
        cmds = self._load_cmds()
        argparser = ArgumentParser(cmds)
        if len(sys.argv) > 1:
            subcmd, args = argparser.parse_args(sys.argv[1:])
            subcmd.execute(args)
        else:
            raise ManagementException("manage.py requires necessary input parameters!")
