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

from abc import ABC,                                            \
                abstractmethod
from transitions.core import Machine,                           \
                             EventData
from typing import Any,                                         \
                   TYPE_CHECKING
import pwd
import os
import traceback

from galaxy.app import constant
from galaxy.app.argparser import ArgParser
from galaxy.app.ioc.ioc import IOCManager
from galaxy.utils.base import Component,                        \
                              TimestampedState
from galaxy.kernel.kernel import Kernel,                        \
                                 GalaxyAsyncKernel
from galaxy.service.service import ServiceManager,              \
                                   ServiceAsyncManager,         \
                                   LogService,                  \
                                   LogAsyncService
from galaxy.error.error import BaseError
from galaxy.proc.proc import ProcessManager,                    \
                             ProcessAsyncManager

if TYPE_CHECKING:
    from galaxy.app.ioc.visitor import Visitor


class Application(Component, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        super(Application, self).__init__()
        self._machine: ApplicationStateMachine = ApplicationStateMachine(self)
        self.log: LogService | LogAsyncService | None = None

    @abstractmethod
    def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    def accept(self, visitor: "Visitor"):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<Application(id='{}')>".format(self.id)


class ApplicationState(TimestampedState):
    """
    classdocs
    """

    def __init__(self, name: str, app: Application) -> None:
        """
        Constructor
        """
        super(ApplicationState, self).__init__(name=name)
        self.app: Application = app


class ApplicationNewState(ApplicationState):
    """
    classdocs
    """

    def __init__(self, app: Application) -> None:
        """
        Constructor
        """
        super(ApplicationNewState, self).__init__(constant.STATE_NEW, app)


class ApplicationRunningState(ApplicationState):
    """
    classdocs
    """

    def __init__(self, app: Application) -> None:
        """
        Constructor
        """
        super(ApplicationRunningState, self).__init__(constant.STATE_RUNNING, app)

    def enter(self, event_data):
        # The logger is not already configured. It will be configured in the app._start()
        print("The application {} is booting".format(self.app))
        #self.app.log.logger.debug("The application {} is booting".format(self.app))
        self.app._start()
        self.app.log.logger.debug("The application {} is running".format(self.app))
        super(ApplicationRunningState, self).enter(event_data)


class ApplicationStoppedState(ApplicationState):
    """
    classdocs
    """

    def __init__(self, app: Application) -> None:
        """
        Constructor
        """
        super(ApplicationStoppedState, self).__init__(constant.STATE_STOPPED, app)

    def enter(self, event_data: EventData) -> None:
        self.app.log.logger.debug("The application {} is stopping".format(self.app))
        self.app._stop()
        self.app.log.logger.debug("The application {} is stopped".format(self.app))
        super(ApplicationStoppedState, self).enter(event_data)


class ApplicationShutdownState(ApplicationState):
    """
    classdocs
    """

    def __init__(self, app: Application) -> None:
        """
        Constructor
        """
        super(ApplicationShutdownState, self).__init__(constant.STATE_SHUTDOWN, app)


class ApplicationTimeoutState(ApplicationState):
    """
    classdocs
    """

    def __init__(self, app: Application) -> None:
        """
        Constructor
        """
        super(ApplicationTimeoutState, self).__init__(constant.STATE_TIMEOUT, app)


class ApplicationStateMachine(object):
    """
    classdocs
    """

    def __init__(self, app: Application) -> None:
        """
        Constructor
        """
        self._app: Application = app
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, ApplicationState] = {
                                                    constant.STATE_NEW: ApplicationNewState(self._app),
                                                    constant.STATE_RUNNING: ApplicationRunningState(self._app),
                                                    constant.STATE_STOPPED: ApplicationStoppedState(self._app),
                                                    constant.STATE_SHUTDOWN: ApplicationShutdownState(self._app),
                                                    constant.STATE_TIMEOUT: ApplicationTimeoutState(self._app)
                                                   }
        self._transitions: list[dict[str, str]] = [{
                                                    "trigger": "run",
                                                    "source": constant.STATE_NEW,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "stop",
                                                    "source": constant.STATE_RUNNING,
                                                    "dest": constant.STATE_STOPPED
                                                   },
                                                   {
                                                    "trigger": "run",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "shutdown",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_SHUTDOWN
                                                   }]

    def _init_machine(self) -> None:
        self.machine: Machine = Machine(model=self._app,
                                        states=[state for state in self.states.values()],
                                        transitions=self._transitions,
                                        initial=self.states[constant.STATE_NEW])


class GalaxyApplication(Application):
    """
    classdocs
    """

    def __init__(self, comp_file: str) -> None:
        super(GalaxyApplication, self).__init__()
        self.ioc: IOCManager = IOCManager(self)
        self.kernel: Kernel | None = None
        self.service: ServiceManager | None = None
        self.proc: ProcessManager | None = None

        try:
            self.ioc.load_comp(comp_file)
        except BaseError as e:
            msg = "{} : {}".format(e, e.internal) if e.internal is not None else str(e)
            print(msg)
        except Exception as e:
            print(e)

    def load_conf(self, conf_file: str) -> None:
        try:
            self.ioc.load_conf(conf_file)
        except BaseError as e:
            msg = "{} : {}".format(e, e.internal) if e.internal is not None else str(e)
            print(msg)
        except Exception as e:
            print(e)

    def _start(self) -> None:
        self.service.load_all()
        self.proc.load_all()
        self.kernel.load()
        self.service.start()
        self.proc.start()
        self.kernel.run()

    def _stop(self) -> None:
        self.proc.stop()
        self.service.stop()
        self.kernel.stop()

    def __repr__(self) -> str:
        return "<GalaxyApplication(id='{}')>".format(self.id)


def start_app(*params: Any):
    username = pwd.getpwuid(os.getuid()).pw_name
    print("Launching program {} by {}".format(params[0], username))
    try:
        parser = ArgParser(params[0])
        args = parser.parse_args(params[1:])
        app = GalaxyApplication(args.comp)
        app.load_conf(args.conf)
        app.run()
    except Exception as e:
        print("An error occurred : {}".format(str(e)))
    print("End execution of the program {}".format(params[0]))


class GalaxyAsyncApplication(Application):
    """
    classdocs
    """

    def __init__(self, comp_file: str) -> None:
        super(GalaxyAsyncApplication, self).__init__()
        self.ioc = IOCManager(self)
        self.kernel: GalaxyAsyncKernel | None = None
        self.service: ServiceAsyncManager | None = None
        self.proc: ProcessAsyncManager | None = None

        try:
            self.ioc.load_comp(comp_file)
        except BaseError as e:
            msg = "{} : {}".format(e, e.internal) if e.internal is not None else str(e)
            print(msg)
        except Exception as e:
            print(traceback.format_exc())
            print(e)

    def load_conf(self, conf_file: str) -> None:
        self.ioc.load_conf(conf_file)

    def _start(self) -> None:
        self.kernel.load()
        self.kernel.run_async(self.service.load_all())
        self.kernel.run_async(self.service.start())
        self.kernel.run_async(self.proc.load_all())
        self.kernel.run_async(self.proc.start())
        self.kernel.run()

    def _stop(self) -> None:
        self.kernel.run_async(self.proc.stop())
        self.kernel.run_async(self.service.stop())
        self.kernel.stop()

    def __repr__(self) -> str:
        return "<GalaxyApplication(id='{}')>".format(self.id)


def start_async_app(*params: Any):
    username = pwd.getpwuid(os.getuid()).pw_name
    try:
        parser = ArgParser(params[0])
        args = parser.parse_args(params[1:])
        print("Launching program {} by {}".format(params[0], username))
        app = GalaxyAsyncApplication(args.comp)
        app.load_conf(args.conf)
        app.run()
    except Exception as e:
        print(traceback.format_exc())
        print("An error occurred : {}".format(str(e)))
    print("End execution of the program {}".format(params[0]))


class SimpleApplication(Application):
    """
    classdocs
    """

    def __init__(self, comp_file: str) -> None:
        super(SimpleApplication, self).__init__()
        self.ioc = IOCManager(self)
        self.service = None
        try:
            self.ioc.load_comp(comp_file)
        except BaseError as e:
            msg = "{} : {}".format(e, e.internal) if e.internal is not None else str(e)
            print(msg)
        except Exception as e:
            print(e)

    def load_conf(self, conf_file: str) -> None:
        try:
            self.ioc.load_conf(conf_file)
        except BaseError as e:
            msg = "{} : {}".format(e, e.internal) if e.internal is not None else str(e)
            print(msg)
        except Exception as e:
            print(e)

    def _start(self) -> None:
        self.service.load_all()

    def _stop(self) -> None:
        self.service.stop()

    def __repr__(self) -> str:
        return "<SimpleApplication(id='{}')>".format(self.id)
