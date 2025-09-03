#  Copyright (c) 2022 bastien.saltel
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
import asyncio
from unittest import TestCase

from galaxy.app.app import GalaxyApplication,               \
                           GalaxyAsyncApplication


class TestLaunch(TestCase):
    
    def test_launch_with_galaxy_async_kernel(self) -> None:
        app = GalaxyAsyncApplication("conf/c0ba5d81-97f2-445f-be51-cabcf7a825fd.yml")
        asyncio.run(app.load_conf("conf/57966f2b-f157-42a0-b85f-a66e086b90f2.yml"))
        asyncio.run(app.run())
        self.assertEqual(True, True)
    
    def test_launch_with_galaxy_kernel(self) -> None:
        app = GalaxyApplication("conf/2511dada-de54-457c-b88a-d1fa16c9d4f3.yml")
        app.load_conf("conf/f221ee90-be67-416d-813b-a51d3f1a95c2.yml")
        app.run()
        self.assertEqual(True, True)
    
    def test_launch_with_jupyter_kernel(self) -> None:
        app = GalaxyApplication("conf/ee19bcf6-2b60-41a0-b2ce-095f67a1ee5e.yml", with_blocking_client=True)
        app.load_conf("conf/bfe3e6f7-2518-482e-a9fb-cf987b3a92cf.yml")
        app.run()
        self.assertEqual(True, True)


if __name__ == "__main__":
    unittest.main()
