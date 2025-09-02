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

from PyPDF3 import PdfFileWriter
import pypdf
import mupdf
import pymupdf
import tabula
from abc import abstractmethod

from galaxy.report.report import Parser


class PyMuPDFParser(Parser):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(PyMuPDFParser, self).__init__()

    def _parse(self, fd) -> list[object]:
        res = []
        return res
