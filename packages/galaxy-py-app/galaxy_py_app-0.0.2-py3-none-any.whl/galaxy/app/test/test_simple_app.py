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

import unittest
from unittest import TestCase

from galaxy.app.app import SimpleApplication,           \
                           GalaxyAsyncApplication


class TestSimpleApp(TestCase):

    #def test_launch_simple_app(self) -> None:
    #    app = SimpleApplication("conf/a4102a60-440d-4a89-9668-23c12c4edf66.yml")
    #    app.load_conf("conf/8405a659-359b-4902-886f-ac6984c63cd0.yml")
    #    app.run()
    #    self.assertEqual(True, True)

    def test_launch_simple_galaxy_app(self) -> None:
        app = GalaxyAsyncApplication("conf/878826a5-431d-4565-8633-3e60977b0236.yml")
        app.load_conf("conf/47161190-b4af-4d8e-afd7-7d30550d4b66.yml")
        app.run()
        self.assertEqual(True, True)

if __name__ == "__main__":
    unittest.main()
