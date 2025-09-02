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

from galaxy.error import constant,          \
                         code
from galaxy.error.error import BaseError


class IOException(BaseError):
    """
    classdocs
    """

    def __init__(self,
                 error_code: int,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None else constant.MSG_ERR_IO_DEFAULT
        super(IOException, self).__init__(error_code, message, internal)


class IOFileNotExistingError(IOException):
    """
    classdocs
    """

    def __init__(self,
                 file: str,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None else constant.MSG_ERR_IO_FILE_NOT_EXISTING.format(file)
        super(IOFileNotExistingError, self).__init__(code.CODE_ERR_IO_FILE_NOT_EXISTING, message, internal)


class IOFileWrongFormatOrMalformedError(IOException):
    """
    classdocs
    """

    def __init__(self,
                 file: str,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None else constant.MSG_ERR_IO_FILE_WRONG_FORMAT_OR_MALFORMED.format(file)
        super(IOFileWrongFormatOrMalformedError, self).__init__(code.CODE_ERR_IO_FILE_WRONG_FORMAT_OR_MALFORMED, message, internal)


class IOFormatNotSupportedError(IOException):
    """
    classdocs
    """

    def __init__(self,
                 extension: str,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None else constant.MSG_ERR_IO_FORMAT_NOT_SUPPORTED.format(extension)
        super(IOFormatNotSupportedError, self).__init__(code.CODE_ERR_IO_FORMAT_NOT_SUPPORTED, message, internal)
