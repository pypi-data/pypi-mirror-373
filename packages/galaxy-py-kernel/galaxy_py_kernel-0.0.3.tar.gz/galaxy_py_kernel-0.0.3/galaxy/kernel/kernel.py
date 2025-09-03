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
import zmq
import sys
import time
from ipykernel.kernelbase import Kernel as KernelBase
from jupyter_client.session import Session
from tornado import ioloop
from typing import Callable,                                \
                   Any,                                     \
                   Awaitable

from galaxy.kernel import constant
from galaxy.utils.type import CompId
from galaxy.utils.base import Component,                    \
                              Configurable,                 \
                              TimestampedState
from galaxy.kernel.loop import EventLoop
from galaxy.service.service import LogService


class Kernel(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: KernelStateMachine = KernelStateMachine(self)
        self.log: LogService | None = None

    @abstractmethod
    def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    def reboot(self) -> None:
        self.stop()
        self.run()

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<Kernel(id='{}')>".format(self.id)


class KernelState(TimestampedState):
    """
    classdocs
    """

    def __init__(self, name: str, kernel: Kernel) -> None:
        """
        Constructor
        """
        super(KernelState, self).__init__(name=name)
        self.kernel: Kernel = kernel


class KernelNewState(KernelState):
    """
    classdocs
    """

    def __init__(self, kernel: Kernel) -> None:
        """
        Constructor
        """
        super(KernelNewState, self).__init__(constant.STATE_NEW, kernel)


class KernelInitiatedState(KernelState):
    """
    classdocs
    """

    def __init__(self, kernel: Kernel) -> None:
        """
        Constructor
        """
        super(KernelInitiatedState, self).__init__(constant.STATE_INIT, kernel)

    def enter(self, event_data: EventData) -> None:
        self.kernel.log.logger.debug("The kernel {} is loading".format(self.kernel))
        self.kernel._load()
        self.kernel.log.logger.debug("The kernel {} is loaded".format(self.kernel))
        super(KernelInitiatedState, self).enter(event_data)


class KernelRunningState(KernelState):
    """
    classdocs
    """

    def __init__(self, kernel: Kernel) -> None:
        """
        Constructor
        """
        super(KernelRunningState, self).__init__(constant.STATE_RUNNING, kernel)

    def enter(self, event_data: EventData) -> None:
        self.kernel.log.logger.debug("The kernel {} is booting".format(self.kernel))
        self.kernel._start()
        self.kernel.log.logger.debug("The kernel {} is running".format(self.kernel))
        super(KernelRunningState, self).enter(event_data)


class KernelStoppedState(KernelState):
    """
    classdocs
    """

    def __init__(self, kernel: Kernel) -> None:
        """
        Constructor
        """
        super(KernelStoppedState, self).__init__(constant.STATE_STOPPED, kernel)

    def enter(self, event_data: EventData) -> None:
        self.kernel.log.logger.debug("The kernel {} is stopping".format(self.kernel))
        self.kernel._stop()
        self.kernel.log.logger.debug("The kernel {} is stopped".format(self.kernel))
        super(KernelStoppedState, self).enter(event_data)


class KernelShutdownState(KernelState):
    """
    classdocs
    """

    def __init__(self, kernel: Kernel) -> None:
        """
        Constructor
        """
        super(KernelShutdownState, self).__init__(constant.STATE_SHUTDOWN, kernel)


class KernelTimeoutState(KernelState):
    """
    classdocs
    """

    def __init__(self, kernel: Kernel) -> None:
        """
        Constructor
        """
        super(KernelTimeoutState, self).__init__(constant.STATE_TIMEOUT, kernel)


class KernelStateMachine(object):
    """
    classdocs
    """

    def __init__(self, kernel: Kernel) -> None:
        """
        Constructor
        """
        self._kernel: Kernel = kernel
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, KernelState] = {
                                               constant.STATE_NEW: KernelNewState(self._kernel),
                                               constant.STATE_INIT: KernelInitiatedState(self._kernel),
                                               constant.STATE_RUNNING: KernelRunningState(self._kernel),
                                               constant.STATE_STOPPED: KernelStoppedState(self._kernel),
                                               constant.STATE_SHUTDOWN: KernelShutdownState(self._kernel),
                                               constant.STATE_TIMEOUT: KernelTimeoutState(self._kernel)
                                              }
        self._transitions: list[dict[str, str]] = [{
                                                    "trigger": "load",
                                                    "source": constant.STATE_NEW,
                                                    "dest": constant.STATE_INIT
                                                   },
                                                   {
                                                    "trigger": "run",
                                                    "source": constant.STATE_INIT,
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
        self.machine: Machine = Machine(model=self._kernel,
                                        states=[state for state in self.states.values()],
                                        transitions=self._transitions,
                                        initial=self.states[constant.STATE_NEW])


class GalaxyKernel(Kernel):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(GalaxyKernel, self).__init__()
    
    def _load(self) -> None:
        super(GalaxyKernel, self)._load()

    def _start(self) -> None:
        pass

    def _stop(self) -> None:
        pass


class GalaxyAsyncKernel(Kernel):
    """
    classdocs
    """
    
    def __init__(self) -> None:
        """
        Constructor
        """
        super(GalaxyAsyncKernel, self).__init__()
        self.loop: EventLoop | None = None

    def _load(self) -> None:
        super(GalaxyAsyncKernel, self)._load()
        self.loop.log = self.log
        self.loop.init()

    def _start(self) -> None:
        self.loop.run()

    def _stop(self) -> None:
        self.loop.stop()

    def run_async(self, fct: Callable[[Any, Any], Awaitable[Any]]) -> None:
        self.loop.run_async(fct)


class JupyterKernelMeta(type(Kernel), type(KernelBase)):
    pass


class JupyterKernel(Kernel, KernelBase, metaclass=JupyterKernelMeta):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Kernel.__init__(self)
        KernelBase.__init__(self)
        self.tmp_log = None
        self.context = None
        self.session = None
        self._init_info()

    def _init_info(self) -> None:
        self.protocol_version = "0.0.1"
        self.implementation = "ipython"
        self.implementation_version = "0.0.1"
        self.language_info = {
                              "name": "python",
                              "version": sys.version.split()[0],
                              "mimetype": "text/x-python",
                              "codemirror_mode": {
                                                  "name": "ipython",
                                                  "version": sys.version_info[0]
                                                 },
                              "pygments_lexer": "ipython3",
                              "nbconvert_exporter": "python",
                              "file_extension": ".py"
                             }
        banner_parts = [
                        "Python {}\n".format(sys.version.split("\n")[0]),
                        "Type 'copyright', 'credits' or 'license' for more information\n",
                        "IPython 0.0.1 -- An enhanced Interactive Python. Type '?' for help.\n"
                       ]
        self.banner = "".join(banner_parts)
        self.help_links = [{
                            "text": "Python Reference",
                            "url": "https://docs.python.org/{}.{}".format(sys.version_info[0], sys.version_info[1])
                           },
                           {
                            "text": "IPython Reference",
                             "url": "https://ipython.org/documentation.html"
                           },
                           {
                            "text": "NumPy Reference",
                            "url": "https://docs.scipy.org/doc/numpy/reference/"
                           },
                           {
                            "text": "SciPy Reference",
                            "url": "https://docs.scipy.org/doc/scipy/reference/"
                           },
                           {
                            "text": "Matplotlib Reference",
                            "url": "https://matplotlib.org/contents.html"
                           },
                           {
                            "text": "SymPy Reference",
                            "url": "http://docs.sympy.org/latest/index.html"
                           },
                           {
                            "text": "pandas Reference",
                            "url": "https://pandas.pydata.org/pandas-docs/stable/"
                           }]

    def _load(self) -> None:
        Kernel._load(self)
        for conn in self.conn.values():
            conn.load()
        self._create_session()
        self._inject_context()

    def _create_session(self) -> None:
        self.session = Session(parent=self)
        self.session.session = self.conf["session"]
        self.session.bsession = self.conf["session"].encode("utf-8")
        self.session.key = self.conf["key"].encode("utf-8")
        self.session.signature_scheme = self.conf["signature_scheme"]
        self.session.username = self.conf["username"]

    def _inject_context(self) -> None:
        self.context = zmq.Context()
        self.conn["shell"].context = self.context
        self.conn["stdin"].context = self.context
        self.conn["ctrl"].context = self.context
        self.conn["iopub"].context = self.context

    def _start(self) -> None:
        for conn in self.conn.values():
            conn.start()
        self._inject_kernel()
        KernelBase.start(self)

    def _inject_kernel(self) -> None:
        self.control_stream = self.conn["ctrl"].stream
        self.shell_streams = [self.conn["shell"].stream, self.conn["ctrl"].stream]
        self.iopub_thread = self.conn["iopub"].thread
        self.iopub_socket = self.conn["iopub"].socket
        self.stdin_socket = self.conn["stdin"].socket
        self.log = self.tmp_log.logger

    def do_execute(self,
                   code,
                   silent,
                   store_history: bool = True,
                   user_expressions = None,
                   allow_stdin: bool = False) -> None:

        reply_content = {}
        exec(code)
        reply_content['status'] = 'ok'
        reply_content['execution_count'] = 1
        reply_content['user_expressions'] = {}
        return reply_content

    def do_apply(self, content, bufs, msg_id, reply_metadata) -> None:
        pass

    def do_clear(self) -> None:
        pass

    def _stop(self) -> None:
        for conn in self.conn.values():
            conn.stop()
        self.context.term()

        # call sys.exit after a short delay
        loop = ioloop.IOLoop.current()
        loop.add_timeout(time.time() + 0.1, loop.stop)
