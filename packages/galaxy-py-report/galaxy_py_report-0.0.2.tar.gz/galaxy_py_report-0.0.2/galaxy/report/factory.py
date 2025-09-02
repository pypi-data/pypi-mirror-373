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

from uuid import uuid4
import os
from os import path,                                        \
               stat,                                        \
               access
from pwd import getpwuid

from galaxy.data.model.file import FileLocation,            \
                                   File,                    \
                                   FileExtension,           \
                                   FileFormat
from galaxy.report.utils import get_creation_date


class FileFactory(object):
    """
    classdocs
    """

    @staticmethod
    def create_file_location(file_path: str) -> FileLocation:
        location = FileLocation(uuid4())
        location.path = file_path
        return location

    @staticmethod
    def create_file(file_path: str,
                    location: FileLocation,
                    extension: FileExtension,
                    format: FileFormat) -> File:
        file = File(uuid4())
        file.name = path.basename(file_path)
        file.path_id = location.id
        file.path = location
        file.extension_id = extension.id
        file.extension = extension
        file.format_id = format.id
        file.format = format
        file.create_date = get_creation_date(file_path)
        st = stat(file_path)
        file.create_by = getpwuid(st.st_uid).pw_name
        file.last_modif_date = st.st_mtime
        file.last_modif_by = getpwuid(st.st_uid).pw_name
        file.is_readable = access(file_path, os.R_OK)
        file.is_writeable = access(file_path, os.W_OK)
        file.is_executable = access(file_path, os.EX_OK)
        file.posix_permission = str(oct(st.st_mode)[-4:])
        return file
