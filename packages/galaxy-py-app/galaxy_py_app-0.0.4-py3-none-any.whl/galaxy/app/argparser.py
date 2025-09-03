#  Copyright (c) 2023 bastien.saltel
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import logging
from argparse import ArgumentParser
from argparse import RawTextHelpFormatter


class ArgParser(object):
    """
    classdocs
    """

    def __init__(self, exec_name) -> None:
        """
        Constructor
        """
        self.exec_name = os.path.basename(exec_name)
        self.short_desc = """
The application Galaxy
"""
        self.app_license = """{}
Copyright (c) 2023 bastien.saltel

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

USAGE :
""".format(self.short_desc)
        self._parser = ArgumentParser(prog=self.exec_name, description=self.app_license, formatter_class=RawTextHelpFormatter)
        self._parser.add_argument("-c", "--comp", dest="comp", help="set the composition file")
        self._parser.add_argument("-f", "--conf", dest="conf", help="set the configuration file")
        self._parser.add_argument("-V", "--version", action="version", version="{prog}s {version}".format(prog="%(prog)", version="1.0"), help="show version")

    def parse_args(self, params):
        try:
            args = self._parser.parse_args(params)
        except Exception as e:
            print("An error occurred while parsing the arguments : {}".format(str(e)))
            raise
        if not os.path.isfile(args.comp):
            print("The composition file '{}' does not exist".format(args.comp))
            self._parser.print_help()
            raise
        if not os.path.isfile(args.conf):
            print("The configuration file '{}' does not exist".format(args.comp))
            self._parser.print_help()
            raise
        return args
