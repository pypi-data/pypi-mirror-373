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

from abc import ABC,                                    \
                abstractmethod
import asyncio
from typing import Callable,                            \
                   Any,                                 \
                   Awaitable

import tornado.ioloop
import uvloop
import selectors

from galaxy.utils.base import Component
from galaxy.service.service import LogService


class SelectorEventLoopPolicy(Component, asyncio.DefaultEventLoopPolicy):
    """
    classdocs
    """

    def __init__(self) -> None:
        Component.__init__(self)
        asyncio.DefaultEventLoopPolicy.__init__(self)

    def new_event_loop(self) -> asyncio.AbstractEventLoop:
        selector = selectors.SelectSelector()
        return asyncio.SelectorEventLoop(selector)


class EventLoop(Component, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self.log: LogService | None = None

    @abstractmethod
    def init(self) -> None:
        raise NotImplementedError("Should implement init()")

    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError("Should implement run()")

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError("Should implement stop()")

    @abstractmethod
    def run_async(self, fct: Callable[[Any, Any], Awaitable[Any]]) -> None:
        raise NotImplementedError("Should implement run_async()")


class AsyncioLoop(EventLoop):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(AsyncioLoop, self).__init__()
        self.loop: Any | None = None
        self.policy: asyncio.DefaultEventLoopPolicy | None = None
        asyncio.set_event_loop(self.loop)

    def init(self) -> None:
        self.init_loop()
        self.init_policy()
        self.loop.set_debug(True)
        self.log.logger.debug("The event loop {} is initialized".format(self))

    def init_loop(self) -> None:
        self.loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def init_policy(self) -> None:
        if self.policy is not None:
            asyncio.set_event_loop_policy(self.policy)

    def run(self) -> None:
        self.log.logger.debug("The event loop {} is running".format(self))
        try:
            self.loop.run_forever()
        finally:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()

    def stop(self) -> None:
        self.loop.close()
        self.log.logger.debug("The event loop {} is closed".format(self))

    def run_async(self, fct: Callable[[Any, Any], Awaitable[Any]]):
        self.loop.run_until_complete(fct)


class UVLoop(AsyncioLoop):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(AsyncioLoop, self).__init__()

    def init(self) -> None:
        self.loop: uvloop.Loop = uvloop.new_event_loop()
        asyncio.set_event_loop(self.loop)


class TornadoLoop(AsyncioLoop):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(TornadoLoop, self).__init__()
        self.ioloop: tornado.ioloop.IOLoop = tornado.ioloop.IOLoop.current()

