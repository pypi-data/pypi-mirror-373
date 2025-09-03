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

import csv
import aiocsv
from abc import abstractmethod

from galaxy.report.report import Parser


class CSVReader(Parser):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CSVReader, self).__init__()

    @abstractmethod
    def create_obj_from_line(self, line: str) -> object:
        raise NotImplementedError("Should implement create_obj_from_line()")

    def _parse(self, fd) -> list[object]:
        res = []
        lines = csv.reader(fd, delimiter=self.conf["delimiter"], quotechar=self.conf["quotechar"])
        for line in lines:
            res.append(self.create_obj_from_line(line))
        return res
