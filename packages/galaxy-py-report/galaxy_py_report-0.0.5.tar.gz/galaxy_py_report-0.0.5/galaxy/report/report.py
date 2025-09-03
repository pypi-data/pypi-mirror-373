#  Copyright (c) 2024 bsaltel
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
from os import path,                                        \
               walk,                                        \
               access
from abc import ABC,                                        \
                abstractmethod
from tempfile import NamedTemporaryFile
import shutil
import asyncio
from transitions.core import Machine,                       \
                             EventData
from transitions.extensions.asyncio import AsyncMachine

from galaxy.utils.base import Component,                    \
                              TimestampedState,             \
                              TimestampedAsyncState,        \
                              Configurable
from galaxy.service.service import Manager,                 \
                                   AsyncManager,            \
                                   Service,                 \
                                   AsyncService,            \
                                   LogService,              \
                                   LogAsyncService
from galaxy.service import constant
from galaxy.service.service import ServiceManager
from galaxy.utils.type import CompId
from galaxy.data.model.file import File
from galaxy.report.factory import FileFactory


class Parser(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self.log: LogService | LogAsyncService | None = None

    @abstractmethod
    def _parse(self, fd) -> list[object]:
        raise NotImplementedError("Should implement _parse()")

    def parse(self, file_path: str) -> list[object]:
        with open(file_path, "rb") as fd:
            elts = self._parse(fd)
        return elts


class Generator(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self.log: LogService | LogAsyncService | None = None

    @abstractmethod
    def _generate(self, fd) -> list[object]:
        raise NotImplementedError("Should implement _generate()")

    def generate(self, file_path: str) -> list[object]:
        with open(file_path, "w") as fd:
            data = self._generate(fd)
        return data


class Importer(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: ImporterStateMachine = ImporterStateMachine(self)
        self.log: LogService | None = None

    @abstractmethod
    def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    @abstractmethod
    def import_report(self, file_path: str, tmp_file_path: str | None = None) -> None:
        raise NotImplementedError("Should implement import_report()")

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<Importer(id='{}')>".format(self.id)


class FileImporter(Importer, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(FileImporter, self).__init__()
        self.service: ServiceManager | None = None
        self.parser: Parser | None = None

    @abstractmethod
    def import_data(self, data: list[object]) -> None:
        raise NotImplementedError("Should implement import_data()")

    def _import_report(self, file: File, file_path: str) -> None:
        data = self.parser.parse(file_path)
        self.import_data(data)

    def import_report(self, file_path: str, tmp_file_path: str | None = None) -> None:
        location = FileFactory.create_file_location(file_path)
        file = FileFactory.create_file(file_path, location)
        self._import_report(tmp_file_path)
        self.service.db.daos["location"].insert(file)
        self.service.db.daos["file"].insert(file)

    def can_parse(self, file_path: str) -> bool:
        extension = file_path.split(".")[-1]
        return path.exists(file_path) and path.isfile(file_path) and access(file_path, os.R_OK)

    def __repr__(self) -> str:
        return "<FileImporter(id='{}')>".format(self.id)


class DirectoryImporter(Importer, ABC):
    """
        classdocs
        """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(DirectoryImporter, self).__init__()
        self.importer: FileImporter | None = None

    def _start(self) -> None:
        if not path.exists(self.conf["dir"]):
            self.log.logger.error("The directory {} does not exist".format(self.conf["dir"]))
            return None
        file_paths = [path.join(dirpath, f) for (dirpath, dirnames, filenames) in walk(self.conf["dir"]) for f in filenames]
        file_paths.sort(key=lambda x: path.getmtime(x), reverse=True)
        for file_path in file_paths:
            self.import_report(str(file_path))

    def _stop(self) -> None:
        pass

    def import_report(self, file_path: str, tmp_file_path: str | None = None) -> None:
        if self.importer.can_parse(file_path):
            tmp_file = NamedTemporaryFile(delete=True, prefix="__", suffix=".tmp")
            shutil.copy2(file_path, tmp_file.name)
            self.importer.import_report(file_path, tmp_file.name)

    def __repr__(self) -> str:
        return "<DirectoryImporter(id='{}')>".format(self.id)


class ImporterState(TimestampedState):
    """
    classdocs
    """

    def __init__(self, name: str, importer: Importer) -> None:
        """
        Constructor
        """
        super(ImporterState, self).__init__(name=name)
        self.importer: Importer = importer


class ImporterNewState(ImporterState):
    """
    classdocs
    """

    def __init__(self, importer: Importer) -> None:
        """
        Constructor
        """
        super(ImporterNewState, self).__init__(constant.STATE_NEW, importer)


class ImporterInitiatedState(ImporterState):
    """
    classdocs
    """

    def __init__(self, importer: Importer) -> None:
        """
        Constructor
        """
        super(ImporterInitiatedState, self).__init__(constant.STATE_INIT, importer)

    def enter(self, event_data: EventData) -> None:
        self.importer.log.logger.debug("The importer {} is loading".format(self.importer))
        self.importer._load()
        self.importer.log.logger.debug("The importer {} is loaded".format(self.importer))
        super(ImporterInitiatedState, self).enter(event_data)


class ImporterRunningState(ImporterState):
    """
    classdocs
    """

    def __init__(self, importer: Importer) -> None:
        """
        Constructor
        """
        super(ImporterRunningState, self).__init__(constant.STATE_RUNNING, importer)

    def enter(self, event_data: EventData) -> None:
        self.importer.log.logger.debug("The importer {} is starting".format(self.importer))
        self.importer._start()
        self.importer.log.logger.debug("The importer {} is running".format(self.importer))
        super(ImporterRunningState, self).enter(event_data)


class ImporterStoppedState(ImporterState):
    """
    classdocs
    """

    def __init__(self, importer: Importer) -> None:
        """
        Constructor
        """
        super(ImporterStoppedState, self).__init__(constant.STATE_STOPPED, importer)

    def enter(self, event_data: EventData) -> None:
        self.importer.log.logger.debug("The proc {} is stopping".format(self.importer))
        self.importer._stop()
        self.importer.log.logger.debug("The proc {} is stopped".format(self.importer))
        super(ImporterStoppedState, self).enter(event_data)


class ImporterPausedState(ImporterState):
    """
    classdocs
    """

    def __init__(self, importer: Importer) -> None:
        """
        Constructor
        """
        super(ImporterPausedState, self).__init__(constant.STATE_PAUSED, importer)

    async def enter(self, event_data: EventData) -> None:
        self.importer.log.logger.debug("The proc {} is pausing".format(self.importer))
        self.importer._pause()
        self.importer.log.logger.debug("The proc {} is paused".format(self.importer))
        super(ImporterPausedState, self).enter(event_data)


class ImporterShutdownState(ImporterState):
    """
    classdocs
    """

    def __init__(self, importer: Importer) -> None:
        """
        Constructor
        """
        super(ImporterShutdownState, self).__init__(constant.STATE_SHUTDOWN, importer)


class ImporterTimeoutState(ImporterState):
    """
    classdocs
    """

    def __init__(self, importer: Importer) -> None:
        """
        Constructor
        """
        super(ImporterTimeoutState, self).__init__(constant.STATE_TIMEOUT, importer)


class ImporterStateMachine(object):
    """
    classdocs
    """

    def __init__(self, importer: Importer) -> None:
        """
        Constructor
        """
        self._importer: Importer = importer
        self.enabled: bool = False
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, ImporterState] = {
                                                 constant.STATE_NEW: ImporterNewState(self._importer),
                                                 constant.STATE_INIT: ImporterInitiatedState(self._importer),
                                                 constant.STATE_RUNNING: ImporterRunningState(self._importer),
                                                 constant.STATE_STOPPED: ImporterStoppedState(self._importer),
                                                 constant.STATE_PAUSED: ImporterPausedState(self._importer),
                                                 constant.STATE_SHUTDOWN: ImporterShutdownState(self._importer),
                                                 constant.STATE_TIMEOUT: ImporterTimeoutState(self._importer)
                                                }
        self._transitions: list[dict[str, str]] = [{
                                                    "trigger": "load",
                                                    "source": constant.STATE_NEW,
                                                    "dest": constant.STATE_INIT
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_INIT,
                                                    "dest": constant.STATE_RUNNING,
                                                    "conditions": "is_enabled"
                                                   },
                                                   {
                                                    "trigger": "stop",
                                                    "source": constant.STATE_RUNNING,
                                                    "dest": constant.STATE_STOPPED
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "pause",
                                                    "source": constant.STATE_RUNNING,
                                                    "dest": constant.STATE_PAUSED
                                                   },
                                                   {
                                                    "trigger": "resume",
                                                    "source": constant.STATE_PAUSED,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "shutdown",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_SHUTDOWN
                                                   }]

    def _init_machine(self):
        self.machine: Machine = Machine(model=self._importer,
                                        states=[state for state in self.states.values()],
                                        transitions=self._transitions,
                                        initial=self.states[constant.STATE_NEW])


class AsyncImporter(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: ImporterStateMachine = ImporterStateMachine(self)
        self.log: LogAsyncService | None = None

    async def _load(self) -> None:
        super(AsyncImporter, self)._load()

    @abstractmethod
    async def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    async def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    @abstractmethod
    async def _pause(self) -> None:
        raise NotImplementedError("Should implement _pause()")

    async def restart(self) -> None:
        await self.stop()
        await self.start()

    def is_enabled(self) -> bool:
        return self.enabled

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<AsyncImporter(id='{}')>".format(self.id)


class ImporterAsyncState(TimestampedAsyncState):
    """
    classdocs
    """

    def __init__(self, name: str, importer: AsyncImporter) -> None:
        """
        Constructor
        """
        super(ImporterAsyncState, self).__init__(name=name)
        self.importer = importer


class ImporterNewAsyncState(ImporterAsyncState):
    """
    classdocs
    """

    def __init__(self, importer: AsyncImporter) -> None:
        """
        Constructor
        """
        super(ImporterNewAsyncState, self).__init__(constant.STATE_NEW, importer)


class ImporterInitiatedAsyncState(ImporterAsyncState):
    """
    classdocs
    """

    def __init__(self, importer: AsyncImporter) -> None:
        """
        Constructor
        """
        super(ImporterInitiatedAsyncState, self).__init__(constant.STATE_INIT, importer)

    async def enter(self, event_data: EventData) -> None:
        self.importer.log.logger.debug("The importer {} is loading".format(self.importer))
        await self.importer._load()
        self.importer.log.logger.debug("The importer {} is loaded".format(self.importer))
        await super(ImporterInitiatedAsyncState, self).enter(event_data)


class ImporterRunningAsyncState(ImporterAsyncState):
    """
    classdocs
    """

    def __init__(self, importer: AsyncImporter) -> None:
        """
        Constructor
        """
        super(ImporterRunningAsyncState, self).__init__(constant.STATE_RUNNING, importer)

    async def enter(self, event_data):
        self.importer.log.logger.debug("The importer {} is starting".format(self.importer))
        await self.importer._start()
        self.importer.log.logger.debug("The importer {} is running".format(self.importer))
        await super(ImporterRunningAsyncState, self).enter(event_data)


class ImporterStoppedAsyncState(ImporterAsyncState):
    """
    classdocs
    """

    def __init__(self, importer: AsyncImporter) -> None:
        """
        Constructor
        """
        super(ImporterStoppedAsyncState, self).__init__(constant.STATE_STOPPED, importer)

    async def enter(self, event_data: EventData) -> None:
        self.importer.log.logger.debug("The importer {} is stopping".format(self.importer))
        await self.importer._stop()
        self.importer.log.logger.debug("The importer {} is stopped".format(self.importer))
        await super(ImporterStoppedAsyncState, self).enter(event_data)


class ImporterPausedAsyncState(ImporterAsyncState):
    """
    classdocs
    """

    def __init__(self, importer: AsyncImporter) -> None:
        """
        Constructor
        """
        super(ImporterPausedAsyncState, self).__init__(constant.STATE_PAUSED, importer)

    async def enter(self, event_data: EventData) -> None:
        self.importer.log.logger.debug("The importer {} is pausing".format(self.importer))
        await self.importer._pause()
        self.importer.log.logger.debug("The importer {} is paused".format(self.importer))
        await super(ImporterPausedAsyncState, self).enter(event_data)


class ImporterShutdownAsyncState(ImporterAsyncState):
    """
    classdocs
    """

    def __init__(self, importer: AsyncImporter) -> None:
        """
        Constructor
        """
        super(ImporterShutdownAsyncState, self).__init__(constant.STATE_SHUTDOWN, importer)


class ImporterTimeoutAsyncState(ImporterAsyncState):
    """
    classdocs
    """

    def __init__(self, importer: AsyncImporter) -> None:
        """
        Constructor
        """
        super(ImporterTimeoutAsyncState, self).__init__(constant.STATE_TIMEOUT, importer)


class ImporterAsyncStateMachine(object):
    """
    classdocs
    """

    def __init__(self, importer: AsyncImporter) -> None:
        """
        Constructor
        """
        self._importer: AsyncImporter = importer
        self.enabled = False
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, ImporterAsyncState] = {
                                                      constant.STATE_NEW: ImporterNewAsyncState(self._importer),
                                                      constant.STATE_INIT: ImporterInitiatedAsyncState(self._importer),
                                                      constant.STATE_RUNNING: ImporterRunningAsyncState(self._importer),
                                                      constant.STATE_STOPPED: ImporterStoppedAsyncState(self._importer),
                                                      constant.STATE_SHUTDOWN: ImporterShutdownAsyncState(self._importer),
                                                      constant.STATE_TIMEOUT: ImporterTimeoutAsyncState(self._importer),
                                                      constant.STATE_PAUSED: ImporterPausedAsyncState(self._importer)
                                                     }
        self._transitions: list[dict[str, str]] = [{
                                                    "trigger": "load",
                                                    "source": constant.STATE_NEW,
                                                    "dest": constant.STATE_INIT
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_INIT,
                                                    "dest": constant.STATE_RUNNING,
                                                    "conditions": "is_enabled"
                                                   },
                                                   {
                                                    "trigger": "stop",
                                                    "source": constant.STATE_RUNNING,
                                                    "dest": constant.STATE_STOPPED
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "pause",
                                                    "source": constant.STATE_RUNNING,
                                                    "dest": constant.STATE_PAUSED
                                                   },
                                                   {
                                                    "trigger": "resume",
                                                    "source": constant.STATE_PAUSED,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "shutdown",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_SHUTDOWN
                                                   }]

    def _init_machine(self) -> None:
        self.machine: AsyncMachine = AsyncMachine(model=self._importer,
                                                  states=[state for state in self.states.values()],
                                                  transitions=self._transitions,
                                                  initial=self.states[constant.STATE_NEW])


class Downloader(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: DownloaderStateMachine = DownloaderStateMachine(self)
        self.log: LogService | None = None

    @abstractmethod
    def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    @abstractmethod
    def download(self, from_file: str, to_file: str | None = None) -> None:
        raise NotImplementedError("Should implement download()")

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<Downloader(id='{}')>".format(self.id)


class SFTPDownloader(Downloader, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SFTPDownloader, self).__init__()

    def __repr__(self) -> str:
        return "<SFTPDownloader(id='{}')>".format(self.id)


class DownloaderState(TimestampedState):
    """
    classdocs
    """

    def __init__(self, name: str, downloader: Downloader) -> None:
        """
        Constructor
        """
        super(DownloaderState, self).__init__(name=name)
        self.downloader: Downloader = downloader


class DownloaderNewState(DownloaderState):
    """
    classdocs
    """

    def __init__(self, downloader: Downloader) -> None:
        """
        Constructor
        """
        super(DownloaderNewState, self).__init__(constant.STATE_NEW, downloader)


class DownloaderInitiatedState(DownloaderState):
    """
    classdocs
    """

    def __init__(self, downloader: Downloader) -> None:
        """
        Constructor
        """
        super(DownloaderInitiatedState, self).__init__(constant.STATE_INIT, downloader)

    def enter(self, event_data: EventData) -> None:
        self.downloader.log.logger.debug("The downloader {} is loading".format(self.downloader))
        self.downloader._load()
        self.downloader.log.logger.debug("The downloader {} is loaded".format(self.downloader))
        super(DownloaderInitiatedState, self).enter(event_data)


class DownloaderRunningState(DownloaderState):
    """
    classdocs
    """

    def __init__(self, downloader: Downloader) -> None:
        """
        Constructor
        """
        super(DownloaderRunningState, self).__init__(constant.STATE_RUNNING, downloader)

    def enter(self, event_data: EventData) -> None:
        self.downloader.log.logger.debug("The downloader {} is starting".format(self.downloader))
        self.downloader._start()
        self.downloader.log.logger.debug("The downloader {} is running".format(self.downloader))
        super(DownloaderRunningState, self).enter(event_data)


class DownloaderStoppedState(DownloaderState):
    """
    classdocs
    """

    def __init__(self, downloader: Downloader) -> None:
        """
        Constructor
        """
        super(DownloaderStoppedState, self).__init__(constant.STATE_STOPPED, downloader)

    def enter(self, event_data: EventData) -> None:
        self.downloader.log.logger.debug("The proc {} is stopping".format(self.downloader))
        self.downloader._stop()
        self.downloader.log.logger.debug("The proc {} is stopped".format(self.downloader))
        super(DownloaderStoppedState, self).enter(event_data)


class DownloaderPausedState(DownloaderState):
    """
    classdocs
    """

    def __init__(self, downloader: Downloader) -> None:
        """
        Constructor
        """
        super(DownloaderPausedState, self).__init__(constant.STATE_PAUSED, downloader)

    async def enter(self, event_data: EventData) -> None:
        self.downloader.log.logger.debug("The proc {} is pausing".format(self.downloader))
        self.downloader._pause()
        self.downloader.log.logger.debug("The proc {} is paused".format(self.downloader))
        super(DownloaderPausedState, self).enter(event_data)


class DownloaderShutdownState(DownloaderState):
    """
    classdocs
    """

    def __init__(self, downloader: Downloader) -> None:
        """
        Constructor
        """
        super(DownloaderShutdownState, self).__init__(constant.STATE_SHUTDOWN, downloader)


class DownloaderTimeoutState(DownloaderState):
    """
    classdocs
    """

    def __init__(self, downloader: Downloader) -> None:
        """
        Constructor
        """
        super(DownloaderTimeoutState, self).__init__(constant.STATE_TIMEOUT, downloader)


class DownloaderStateMachine(object):
    """
    classdocs
    """

    def __init__(self, downloader: Downloader) -> None:
        """
        Constructor
        """
        self._downloader: Downloader = downloader
        self.enabled: bool = False
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, DownloaderState] = {
                                                 constant.STATE_NEW: DownloaderNewState(self._downloader),
                                                 constant.STATE_INIT: DownloaderInitiatedState(self._downloader),
                                                 constant.STATE_RUNNING: DownloaderRunningState(self._downloader),
                                                 constant.STATE_STOPPED: DownloaderStoppedState(self._downloader),
                                                 constant.STATE_PAUSED: DownloaderPausedState(self._downloader),
                                                 constant.STATE_SHUTDOWN: DownloaderShutdownState(self._downloader),
                                                 constant.STATE_TIMEOUT: DownloaderTimeoutState(self._downloader)
                                                }
        self._transitions: list[dict[str, str]] = [{
                                                    "trigger": "load",
                                                    "source": constant.STATE_NEW,
                                                    "dest": constant.STATE_INIT
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_INIT,
                                                    "dest": constant.STATE_RUNNING,
                                                    "conditions": "is_enabled"
                                                   },
                                                   {
                                                    "trigger": "stop",
                                                    "source": constant.STATE_RUNNING,
                                                    "dest": constant.STATE_STOPPED
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "pause",
                                                    "source": constant.STATE_RUNNING,
                                                    "dest": constant.STATE_PAUSED
                                                   },
                                                   {
                                                    "trigger": "resume",
                                                    "source": constant.STATE_PAUSED,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "shutdown",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_SHUTDOWN
                                                   }]

    def _init_machine(self):
        self.machine: Machine = Machine(model=self._downloader,
                                        states=[state for state in self.states.values()],
                                        transitions=self._transitions,
                                        initial=self.states[constant.STATE_NEW])


class AsyncDownloader(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: DownloaderStateMachine = DownloaderStateMachine(self)
        self.log: LogAsyncService | None = None

    async def _load(self) -> None:
        super(AsyncDownloader, self)._load()

    @abstractmethod
    async def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    async def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    @abstractmethod
    async def _pause(self) -> None:
        raise NotImplementedError("Should implement _pause()")

    async def restart(self) -> None:
        await self.stop()
        await self.start()

    def is_enabled(self) -> bool:
        return self.enabled

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<AsyncDownloader(id='{}')>".format(self.id)


class DownloaderAsyncState(TimestampedAsyncState):
    """
    classdocs
    """

    def __init__(self, name: str, downloader: AsyncDownloader) -> None:
        """
        Constructor
        """
        super(DownloaderAsyncState, self).__init__(name=name)
        self.downloader = downloader


class DownloaderNewAsyncState(DownloaderAsyncState):
    """
    classdocs
    """

    def __init__(self, downloader: AsyncDownloader) -> None:
        """
        Constructor
        """
        super(DownloaderNewAsyncState, self).__init__(constant.STATE_NEW, downloader)


class DownloaderInitiatedAsyncState(DownloaderAsyncState):
    """
    classdocs
    """

    def __init__(self, downloader: AsyncDownloader) -> None:
        """
        Constructor
        """
        super(DownloaderInitiatedAsyncState, self).__init__(constant.STATE_INIT, downloader)

    async def enter(self, event_data: EventData) -> None:
        self.downloader.log.logger.debug("The downloader {} is loading".format(self.downloader))
        await self.downloader._load()
        self.downloader.log.logger.debug("The downloader {} is loaded".format(self.downloader))
        await super(DownloaderInitiatedAsyncState, self).enter(event_data)


class DownloaderRunningAsyncState(DownloaderAsyncState):
    """
    classdocs
    """

    def __init__(self, downloader: AsyncDownloader) -> None:
        """
        Constructor
        """
        super(DownloaderRunningAsyncState, self).__init__(constant.STATE_RUNNING, downloader)

    async def enter(self, event_data):
        self.downloader.log.logger.debug("The downloader {} is starting".format(self.downloader))
        await self.downloader._start()
        self.downloader.log.logger.debug("The downloader {} is running".format(self.downloader))
        await super(DownloaderRunningAsyncState, self).enter(event_data)


class DownloaderStoppedAsyncState(DownloaderAsyncState):
    """
    classdocs
    """

    def __init__(self, downloader: AsyncDownloader) -> None:
        """
        Constructor
        """
        super(DownloaderStoppedAsyncState, self).__init__(constant.STATE_STOPPED, downloader)

    async def enter(self, event_data: EventData) -> None:
        self.downloader.log.logger.debug("The downloader {} is stopping".format(self.downloader))
        await self.downloader._stop()
        self.downloader.log.logger.debug("The downloader {} is stopped".format(self.downloader))
        await super(DownloaderStoppedAsyncState, self).enter(event_data)


class DownloaderPausedAsyncState(DownloaderAsyncState):
    """
    classdocs
    """

    def __init__(self, downloader: AsyncDownloader) -> None:
        """
        Constructor
        """
        super(DownloaderPausedAsyncState, self).__init__(constant.STATE_PAUSED, downloader)

    async def enter(self, event_data: EventData) -> None:
        self.downloader.log.logger.debug("The downloader {} is pausing".format(self.downloader))
        await self.downloader._pause()
        self.downloader.log.logger.debug("The downloader {} is paused".format(self.downloader))
        await super(DownloaderPausedAsyncState, self).enter(event_data)


class DownloaderShutdownAsyncState(DownloaderAsyncState):
    """
    classdocs
    """

    def __init__(self, downloader: AsyncDownloader) -> None:
        """
        Constructor
        """
        super(DownloaderShutdownAsyncState, self).__init__(constant.STATE_SHUTDOWN, downloader)


class DownloaderTimeoutAsyncState(DownloaderAsyncState):
    """
    classdocs
    """

    def __init__(self, downloader: AsyncDownloader) -> None:
        """
        Constructor
        """
        super(DownloaderTimeoutAsyncState, self).__init__(constant.STATE_TIMEOUT, downloader)


class DownloaderAsyncStateMachine(object):
    """
    classdocs
    """

    def __init__(self, downloader: AsyncDownloader) -> None:
        """
        Constructor
        """
        self._downloader: AsyncDownloader = downloader
        self.enabled = False
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, DownloaderAsyncState] = {
                                                      constant.STATE_NEW: DownloaderNewAsyncState(self._downloader),
                                                      constant.STATE_INIT: DownloaderInitiatedAsyncState(self._downloader),
                                                      constant.STATE_RUNNING: DownloaderRunningAsyncState(self._downloader),
                                                      constant.STATE_STOPPED: DownloaderStoppedAsyncState(self._downloader),
                                                      constant.STATE_SHUTDOWN: DownloaderShutdownAsyncState(self._downloader),
                                                      constant.STATE_TIMEOUT: DownloaderTimeoutAsyncState(self._downloader),
                                                      constant.STATE_PAUSED: DownloaderPausedAsyncState(self._downloader)
                                                     }
        self._transitions: list[dict[str, str]] = [{
                                                    "trigger": "load",
                                                    "source": constant.STATE_NEW,
                                                    "dest": constant.STATE_INIT
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_INIT,
                                                    "dest": constant.STATE_RUNNING,
                                                    "conditions": "is_enabled"
                                                   },
                                                   {
                                                    "trigger": "stop",
                                                    "source": constant.STATE_RUNNING,
                                                    "dest": constant.STATE_STOPPED
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "pause",
                                                    "source": constant.STATE_RUNNING,
                                                    "dest": constant.STATE_PAUSED
                                                   },
                                                   {
                                                    "trigger": "resume",
                                                    "source": constant.STATE_PAUSED,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "shutdown",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_SHUTDOWN
                                                   }]

    def _init_machine(self) -> None:
        self.machine: AsyncMachine = AsyncMachine(model=self._downloader,
                                                  states=[state for state in self.states.values()],
                                                  transitions=self._transitions,
                                                  initial=self.states[constant.STATE_NEW])

class Exporter(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: ExporterStateMachine = ExporterStateMachine(self)
        self.log: LogService | None = None

    @abstractmethod
    def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<Exporter(id='{}')>".format(self.id)


class ExporterState(TimestampedState):
    """
    classdocs
    """

    def __init__(self, name: str, exporter: Exporter) -> None:
        """
        Constructor
        """
        super(ExporterState, self).__init__(name=name)
        self.exporter: Exporter = exporter


class ExporterNewState(ExporterState):
    """
    classdocs
    """

    def __init__(self, exporter: Exporter) -> None:
        """
        Constructor
        """
        super(ExporterNewState, self).__init__(constant.STATE_NEW, exporter)


class ExporterInitiatedState(ExporterState):
    """
    classdocs
    """

    def __init__(self, exporter: Exporter) -> None:
        """
        Constructor
        """
        super(ExporterInitiatedState, self).__init__(constant.STATE_INIT, exporter)

    def enter(self, event_data: EventData) -> None:
        self.exporter.log.logger.debug("The exporter {} is loading".format(self.exporter))
        self.exporter._load()
        self.exporter.log.logger.debug("The exporter {} is loaded".format(self.exporter))
        super(ExporterInitiatedState, self).enter(event_data)


class ExporterRunningState(ExporterState):
    """
    classdocs
    """

    def __init__(self, exporter: Exporter) -> None:
        """
        Constructor
        """
        super(ExporterRunningState, self).__init__(constant.STATE_RUNNING, exporter)

    def enter(self, event_data: EventData) -> None:
        self.exporter.log.logger.debug("The exporter {} is starting".format(self.exporter))
        self.exporter._start()
        self.exporter.log.logger.debug("The exporter {} is running".format(self.exporter))
        super(ExporterRunningState, self).enter(event_data)


class ExporterStoppedState(ExporterState):
    """
    classdocs
    """

    def __init__(self, exporter: Exporter) -> None:
        """
        Constructor
        """
        super(ExporterStoppedState, self).__init__(constant.STATE_STOPPED, exporter)

    def enter(self, event_data: EventData) -> None:
        self.exporter.log.logger.debug("The proc {} is stopping".format(self.exporter))
        self.exporter._stop()
        self.exporter.log.logger.debug("The proc {} is stopped".format(self.exporter))
        super(ExporterStoppedState, self).enter(event_data)


class ExporterPausedState(ExporterState):
    """
    classdocs
    """

    def __init__(self, exporter: Exporter) -> None:
        """
        Constructor
        """
        super(ExporterPausedState, self).__init__(constant.STATE_PAUSED, exporter)

    async def enter(self, event_data: EventData) -> None:
        self.exporter.log.logger.debug("The proc {} is pausing".format(self.exporter))
        self.exporter._pause()
        self.exporter.log.logger.debug("The proc {} is paused".format(self.exporter))
        super(ExporterPausedState, self).enter(event_data)


class ExporterShutdownState(ExporterState):
    """
    classdocs
    """

    def __init__(self, exporter: Exporter) -> None:
        """
        Constructor
        """
        super(ExporterShutdownState, self).__init__(constant.STATE_SHUTDOWN, exporter)


class ExporterTimeoutState(ExporterState):
    """
    classdocs
    """

    def __init__(self, exporter: Exporter) -> None:
        """
        Constructor
        """
        super(ExporterTimeoutState, self).__init__(constant.STATE_TIMEOUT, exporter)


class ExporterStateMachine(object):
    """
    classdocs
    """

    def __init__(self, exporter: Exporter) -> None:
        """
        Constructor
        """
        self._exporter: Exporter = exporter
        self.enabled: bool = False
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, ExporterState] = {
                                                 constant.STATE_NEW: ExporterNewState(self._exporter),
                                                 constant.STATE_INIT: ExporterInitiatedState(self._exporter),
                                                 constant.STATE_RUNNING: ExporterRunningState(self._exporter),
                                                 constant.STATE_STOPPED: ExporterStoppedState(self._exporter),
                                                 constant.STATE_PAUSED: ExporterPausedState(self._exporter),
                                                 constant.STATE_SHUTDOWN: ExporterShutdownState(self._exporter),
                                                 constant.STATE_TIMEOUT: ExporterTimeoutState(self._exporter)
                                                }
        self._transitions: list[dict[str, str]] = [{
                                                    "trigger": "load",
                                                    "source": constant.STATE_NEW,
                                                    "dest": constant.STATE_INIT
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_INIT,
                                                    "dest": constant.STATE_RUNNING,
                                                    "conditions": "is_enabled"
                                                   },
                                                   {
                                                    "trigger": "stop",
                                                    "source": constant.STATE_RUNNING,
                                                    "dest": constant.STATE_STOPPED
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "pause",
                                                    "source": constant.STATE_RUNNING,
                                                    "dest": constant.STATE_PAUSED
                                                   },
                                                   {
                                                    "trigger": "resume",
                                                    "source": constant.STATE_PAUSED,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "shutdown",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_SHUTDOWN
                                                   }]

    def _init_machine(self):
        self.machine: Machine = Machine(model=self._exporter,
                                        states=[state for state in self.states.values()],
                                        transitions=self._transitions,
                                        initial=self.states[constant.STATE_NEW])


class AsyncExporter(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: ExporterStateMachine = ExporterStateMachine(self)
        self.log: LogAsyncService | None = None

    async def _load(self) -> None:
        super(AsyncExporter, self)._load()

    @abstractmethod
    async def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    async def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    @abstractmethod
    async def _pause(self) -> None:
        raise NotImplementedError("Should implement _pause()")

    async def restart(self) -> None:
        await self.stop()
        await self.start()

    def is_enabled(self) -> bool:
        return self.enabled

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<AsyncExporter(id='{}')>".format(self.id)


class ExporterAsyncState(TimestampedAsyncState):
    """
    classdocs
    """

    def __init__(self, name: str, exporter: AsyncExporter) -> None:
        """
        Constructor
        """
        super(ExporterAsyncState, self).__init__(name=name)
        self.exporter = exporter


class ExporterNewAsyncState(ExporterAsyncState):
    """
    classdocs
    """

    def __init__(self, exporter: AsyncExporter) -> None:
        """
        Constructor
        """
        super(ExporterNewAsyncState, self).__init__(constant.STATE_NEW, exporter)


class ExporterInitiatedAsyncState(ExporterAsyncState):
    """
    classdocs
    """

    def __init__(self, exporter: AsyncExporter) -> None:
        """
        Constructor
        """
        super(ExporterInitiatedAsyncState, self).__init__(constant.STATE_INIT, exporter)

    async def enter(self, event_data: EventData) -> None:
        self.exporter.log.logger.debug("The exporter {} is loading".format(self.exporter))
        await self.exporter._load()
        self.exporter.log.logger.debug("The exporter {} is loaded".format(self.exporter))
        await super(ExporterInitiatedAsyncState, self).enter(event_data)


class ExporterRunningAsyncState(ExporterAsyncState):
    """
    classdocs
    """

    def __init__(self, exporter: AsyncExporter) -> None:
        """
        Constructor
        """
        super(ExporterRunningAsyncState, self).__init__(constant.STATE_RUNNING, exporter)

    async def enter(self, event_data):
        self.exporter.log.logger.debug("The exporter {} is starting".format(self.exporter))
        await self.exporter._start()
        self.exporter.log.logger.debug("The exporter {} is running".format(self.exporter))
        await super(ExporterRunningAsyncState, self).enter(event_data)


class ExporterStoppedAsyncState(ExporterAsyncState):
    """
    classdocs
    """

    def __init__(self, exporter: AsyncExporter) -> None:
        """
        Constructor
        """
        super(ExporterStoppedAsyncState, self).__init__(constant.STATE_STOPPED, exporter)

    async def enter(self, event_data: EventData) -> None:
        self.exporter.log.logger.debug("The exporter {} is stopping".format(self.exporter))
        await self.exporter._stop()
        self.exporter.log.logger.debug("The exporter {} is stopped".format(self.exporter))
        await super(ExporterStoppedAsyncState, self).enter(event_data)


class ExporterPausedAsyncState(ExporterAsyncState):
    """
    classdocs
    """

    def __init__(self, exporter: AsyncExporter) -> None:
        """
        Constructor
        """
        super(ExporterPausedAsyncState, self).__init__(constant.STATE_PAUSED, exporter)

    async def enter(self, event_data: EventData) -> None:
        self.exporter.log.logger.debug("The exporter {} is pausing".format(self.exporter))
        await self.exporter._pause()
        self.exporter.log.logger.debug("The exporter {} is paused".format(self.exporter))
        await super(ExporterPausedAsyncState, self).enter(event_data)


class ExporterShutdownAsyncState(ExporterAsyncState):
    """
    classdocs
    """

    def __init__(self, exporter: AsyncExporter) -> None:
        """
        Constructor
        """
        super(ExporterShutdownAsyncState, self).__init__(constant.STATE_SHUTDOWN, exporter)


class ExporterTimeoutAsyncState(ExporterAsyncState):
    """
    classdocs
    """

    def __init__(self, exporter: AsyncExporter) -> None:
        """
        Constructor
        """
        super(ExporterTimeoutAsyncState, self).__init__(constant.STATE_TIMEOUT, exporter)


class ExporterAsyncStateMachine(object):
    """
    classdocs
    """

    def __init__(self, exporter: AsyncExporter) -> None:
        """
        Constructor
        """
        self._exporter: AsyncExporter = exporter
        self.enabled = False
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, ExporterAsyncState] = {
                                                      constant.STATE_NEW: ExporterNewAsyncState(self._exporter),
                                                      constant.STATE_INIT: ExporterInitiatedAsyncState(self._exporter),
                                                      constant.STATE_RUNNING: ExporterRunningAsyncState(self._exporter),
                                                      constant.STATE_STOPPED: ExporterStoppedAsyncState(self._exporter),
                                                      constant.STATE_SHUTDOWN: ExporterShutdownAsyncState(self._exporter),
                                                      constant.STATE_TIMEOUT: ExporterTimeoutAsyncState(self._exporter),
                                                      constant.STATE_PAUSED: ExporterPausedAsyncState(self._exporter)
                                                     }
        self._transitions: list[dict[str, str]] = [{
                                                    "trigger": "load",
                                                    "source": constant.STATE_NEW,
                                                    "dest": constant.STATE_INIT
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_INIT,
                                                    "dest": constant.STATE_RUNNING,
                                                    "conditions": "is_enabled"
                                                   },
                                                   {
                                                    "trigger": "stop",
                                                    "source": constant.STATE_RUNNING,
                                                    "dest": constant.STATE_STOPPED
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "pause",
                                                    "source": constant.STATE_RUNNING,
                                                    "dest": constant.STATE_PAUSED
                                                   },
                                                   {
                                                    "trigger": "resume",
                                                    "source": constant.STATE_PAUSED,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "shutdown",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_SHUTDOWN
                                                   }]

    def _init_machine(self) -> None:
        self.machine: AsyncMachine = AsyncMachine(model=self._exporter,
                                                  states=[state for state in self.states.values()],
                                                  transitions=self._transitions,
                                                  initial=self.states[constant.STATE_NEW])


class Uploader(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: UploaderStateMachine = UploaderStateMachine(self)
        self.log: LogService | None = None

    @abstractmethod
    def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<Uploader(id='{}')>".format(self.id)


class UploaderState(TimestampedState):
    """
    classdocs
    """

    def __init__(self, name: str, uploader: Uploader) -> None:
        """
        Constructor
        """
        super(UploaderState, self).__init__(name=name)
        self.uploader: Uploader = uploader


class UploaderNewState(UploaderState):
    """
    classdocs
    """

    def __init__(self, uploader: Uploader) -> None:
        """
        Constructor
        """
        super(UploaderNewState, self).__init__(constant.STATE_NEW, uploader)


class UploaderInitiatedState(UploaderState):
    """
    classdocs
    """

    def __init__(self, uploader: Uploader) -> None:
        """
        Constructor
        """
        super(UploaderInitiatedState, self).__init__(constant.STATE_INIT, uploader)

    def enter(self, event_data: EventData) -> None:
        self.uploader.log.logger.debug("The uploader {} is loading".format(self.uploader))
        self.uploader._load()
        self.uploader.log.logger.debug("The uploader {} is loaded".format(self.uploader))
        super(UploaderInitiatedState, self).enter(event_data)


class UploaderRunningState(UploaderState):
    """
    classdocs
    """

    def __init__(self, uploader: Uploader) -> None:
        """
        Constructor
        """
        super(UploaderRunningState, self).__init__(constant.STATE_RUNNING, uploader)

    def enter(self, event_data: EventData) -> None:
        self.uploader.log.logger.debug("The uploader {} is starting".format(self.uploader))
        self.uploader._start()
        self.uploader.log.logger.debug("The uploader {} is running".format(self.uploader))
        super(UploaderRunningState, self).enter(event_data)


class UploaderStoppedState(UploaderState):
    """
    classdocs
    """

    def __init__(self, uploader: Uploader) -> None:
        """
        Constructor
        """
        super(UploaderStoppedState, self).__init__(constant.STATE_STOPPED, uploader)

    def enter(self, event_data: EventData) -> None:
        self.uploader.log.logger.debug("The proc {} is stopping".format(self.uploader))
        self.uploader._stop()
        self.uploader.log.logger.debug("The proc {} is stopped".format(self.uploader))
        super(UploaderStoppedState, self).enter(event_data)


class UploaderPausedState(UploaderState):
    """
    classdocs
    """

    def __init__(self, uploader: Uploader) -> None:
        """
        Constructor
        """
        super(UploaderPausedState, self).__init__(constant.STATE_PAUSED, uploader)

    async def enter(self, event_data: EventData) -> None:
        self.uploader.log.logger.debug("The proc {} is pausing".format(self.uploader))
        self.uploader._pause()
        self.uploader.log.logger.debug("The proc {} is paused".format(self.uploader))
        super(UploaderPausedState, self).enter(event_data)


class UploaderShutdownState(UploaderState):
    """
    classdocs
    """

    def __init__(self, uploader: Uploader) -> None:
        """
        Constructor
        """
        super(UploaderShutdownState, self).__init__(constant.STATE_SHUTDOWN, uploader)


class UploaderTimeoutState(UploaderState):
    """
    classdocs
    """

    def __init__(self, uploader: Uploader) -> None:
        """
        Constructor
        """
        super(UploaderTimeoutState, self).__init__(constant.STATE_TIMEOUT, uploader)


class UploaderStateMachine(object):
    """
    classdocs
    """

    def __init__(self, uploader: Uploader) -> None:
        """
        Constructor
        """
        self._uploader: Uploader = uploader
        self.enabled: bool = False
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, UploaderState] = {
                                                 constant.STATE_NEW: UploaderNewState(self._uploader),
                                                 constant.STATE_INIT: UploaderInitiatedState(self._uploader),
                                                 constant.STATE_RUNNING: UploaderRunningState(self._uploader),
                                                 constant.STATE_STOPPED: UploaderStoppedState(self._uploader),
                                                 constant.STATE_PAUSED: UploaderPausedState(self._uploader),
                                                 constant.STATE_SHUTDOWN: UploaderShutdownState(self._uploader),
                                                 constant.STATE_TIMEOUT: UploaderTimeoutState(self._uploader)
                                                }
        self._transitions: list[dict[str, str]] = [{
                                                    "trigger": "load",
                                                    "source": constant.STATE_NEW,
                                                    "dest": constant.STATE_INIT
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_INIT,
                                                    "dest": constant.STATE_RUNNING,
                                                    "conditions": "is_enabled"
                                                   },
                                                   {
                                                    "trigger": "stop",
                                                    "source": constant.STATE_RUNNING,
                                                    "dest": constant.STATE_STOPPED
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "pause",
                                                    "source": constant.STATE_RUNNING,
                                                    "dest": constant.STATE_PAUSED
                                                   },
                                                   {
                                                    "trigger": "resume",
                                                    "source": constant.STATE_PAUSED,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "shutdown",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_SHUTDOWN
                                                   }]

    def _init_machine(self):
        self.machine: Machine = Machine(model=self._uploader,
                                        states=[state for state in self.states.values()],
                                        transitions=self._transitions,
                                        initial=self.states[constant.STATE_NEW])


class AsyncUploader(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: UploaderStateMachine = UploaderStateMachine(self)
        self.log: LogAsyncService | None = None

    async def _load(self) -> None:
        super(AsyncUploader, self)._load()

    @abstractmethod
    async def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    async def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    @abstractmethod
    async def _pause(self) -> None:
        raise NotImplementedError("Should implement _pause()")

    async def restart(self) -> None:
        await self.stop()
        await self.start()

    def is_enabled(self) -> bool:
        return self.enabled

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<AsyncUploader(id='{}')>".format(self.id)


class UploaderAsyncState(TimestampedAsyncState):
    """
    classdocs
    """

    def __init__(self, name: str, uploader: AsyncUploader) -> None:
        """
        Constructor
        """
        super(UploaderAsyncState, self).__init__(name=name)
        self.uploader = uploader


class UploaderNewAsyncState(UploaderAsyncState):
    """
    classdocs
    """

    def __init__(self, uploader: AsyncUploader) -> None:
        """
        Constructor
        """
        super(UploaderNewAsyncState, self).__init__(constant.STATE_NEW, uploader)


class UploaderInitiatedAsyncState(UploaderAsyncState):
    """
    classdocs
    """

    def __init__(self, uploader: AsyncUploader) -> None:
        """
        Constructor
        """
        super(UploaderInitiatedAsyncState, self).__init__(constant.STATE_INIT, uploader)

    async def enter(self, event_data: EventData) -> None:
        self.uploader.log.logger.debug("The uploader {} is loading".format(self.uploader))
        await self.uploader._load()
        self.uploader.log.logger.debug("The uploader {} is loaded".format(self.uploader))
        await super(UploaderInitiatedAsyncState, self).enter(event_data)


class UploaderRunningAsyncState(UploaderAsyncState):
    """
    classdocs
    """

    def __init__(self, uploader: AsyncUploader) -> None:
        """
        Constructor
        """
        super(UploaderRunningAsyncState, self).__init__(constant.STATE_RUNNING, uploader)

    async def enter(self, event_data):
        self.uploader.log.logger.debug("The uploader {} is starting".format(self.uploader))
        await self.uploader._start()
        self.uploader.log.logger.debug("The uploader {} is running".format(self.uploader))
        await super(UploaderRunningAsyncState, self).enter(event_data)


class UploaderStoppedAsyncState(UploaderAsyncState):
    """
    classdocs
    """

    def __init__(self, uploader: AsyncUploader) -> None:
        """
        Constructor
        """
        super(UploaderStoppedAsyncState, self).__init__(constant.STATE_STOPPED, uploader)

    async def enter(self, event_data: EventData) -> None:
        self.uploader.log.logger.debug("The uploader {} is stopping".format(self.uploader))
        await self.uploader._stop()
        self.uploader.log.logger.debug("The uploader {} is stopped".format(self.uploader))
        await super(UploaderStoppedAsyncState, self).enter(event_data)


class UploaderPausedAsyncState(UploaderAsyncState):
    """
    classdocs
    """

    def __init__(self, uploader: AsyncUploader) -> None:
        """
        Constructor
        """
        super(UploaderPausedAsyncState, self).__init__(constant.STATE_PAUSED, uploader)

    async def enter(self, event_data: EventData) -> None:
        self.uploader.log.logger.debug("The uploader {} is pausing".format(self.uploader))
        await self.uploader._pause()
        self.uploader.log.logger.debug("The uploader {} is paused".format(self.uploader))
        await super(UploaderPausedAsyncState, self).enter(event_data)


class UploaderShutdownAsyncState(UploaderAsyncState):
    """
    classdocs
    """

    def __init__(self, uploader: AsyncUploader) -> None:
        """
        Constructor
        """
        super(UploaderShutdownAsyncState, self).__init__(constant.STATE_SHUTDOWN, uploader)


class UploaderTimeoutAsyncState(UploaderAsyncState):
    """
    classdocs
    """

    def __init__(self, uploader: AsyncUploader) -> None:
        """
        Constructor
        """
        super(UploaderTimeoutAsyncState, self).__init__(constant.STATE_TIMEOUT, uploader)


class UploaderAsyncStateMachine(object):
    """
    classdocs
    """

    def __init__(self, uploader: AsyncUploader) -> None:
        """
        Constructor
        """
        self._uploader: AsyncUploader = uploader
        self.enabled = False
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, UploaderAsyncState] = {
                                                      constant.STATE_NEW: UploaderNewAsyncState(self._uploader),
                                                      constant.STATE_INIT: UploaderInitiatedAsyncState(self._uploader),
                                                      constant.STATE_RUNNING: UploaderRunningAsyncState(self._uploader),
                                                      constant.STATE_STOPPED: UploaderStoppedAsyncState(self._uploader),
                                                      constant.STATE_SHUTDOWN: UploaderShutdownAsyncState(self._uploader),
                                                      constant.STATE_TIMEOUT: UploaderTimeoutAsyncState(self._uploader),
                                                      constant.STATE_PAUSED: UploaderPausedAsyncState(self._uploader)
                                                     }
        self._transitions: list[dict[str, str]] = [{
                                                    "trigger": "load",
                                                    "source": constant.STATE_NEW,
                                                    "dest": constant.STATE_INIT
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_INIT,
                                                    "dest": constant.STATE_RUNNING,
                                                    "conditions": "is_enabled"
                                                   },
                                                   {
                                                    "trigger": "stop",
                                                    "source": constant.STATE_RUNNING,
                                                    "dest": constant.STATE_STOPPED
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "pause",
                                                    "source": constant.STATE_RUNNING,
                                                    "dest": constant.STATE_PAUSED
                                                   },
                                                   {
                                                    "trigger": "resume",
                                                    "source": constant.STATE_PAUSED,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "shutdown",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_SHUTDOWN
                                                   }]

    def _init_machine(self) -> None:
        self.machine: AsyncMachine = AsyncMachine(model=self._uploader,
                                                  states=[state for state in self.states.values()],
                                                  transitions=self._transitions,
                                                  initial=self.states[constant.STATE_NEW])

class ReportService(Service):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ReportService, self).__init__()
        self.importers: dict[CompId, Importer] = {}
        self.downloaders: dict[CompId, Downloader] = {}
        self.exporters: dict[CompId, Exporter] = {}
        self.uploaders: dict[CompId, Uploader] = {}

    def _load(self) -> None:
        super(ReportService, self)._load()

    def _start(self) -> None:
        super(ReportService, self)._start()

    def _stop(self) -> None:
        super(ReportService, self)._stop()

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<ReportService(id='{}')>".format(self.id)


class ReportAsyncService(AsyncService):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ReportAsyncService, self).__init__()
        self.importers: dict[CompId, AsyncImporter] = {}
        self.downloaders: dict[CompId, AsyncDownloader] = {}
        self.exporters: dict[CompId, AsyncExporter] = {}
        self.uploaders: dict[CompId, AsyncUploader] = {}
        self.loop = None

    async def _load(self) -> None:
        await super(ReportAsyncService, self)._load()

    async def _start(self) -> None:
        await super(ReportAsyncService, self)._start()

    async def _stop(self) -> None:
        await super(ReportAsyncService, self)._stop()

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<ReportAsyncService(id='{}')>".format(self.id)


class ReportManager(Manager):
    """
    classdocs
    """
    def __init__(self) -> None:
        """
        Constructor
        """
        super(ReportManager, self).__init__()

    def __repr__(self) -> str:
        return "<ReportManager(id='{}')>".format(self.id)


class ReportAsyncManager(AsyncManager):
    """
    classdocs
    """
    def __init__(self) -> None:
        """
        Constructor
        """
        super(ReportAsyncManager, self).__init__()

    def __repr__(self) -> str:
        return "<ReportAsyncManager(id='{}')>".format(self.id)