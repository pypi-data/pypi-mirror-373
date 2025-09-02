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

from galaxy.error import constant


class BaseError(Exception):
    """
    classdocs
    """

    def __init__(self,
                 error_code: int = None,
                 message: str = None,
                 internal: Exception = None) -> None:
        self.message: str = message if message is not None else constant.MSG_ERR_DEFAULT
        super(BaseError, self).__init__(self.message)
        self.error_code: int = error_code
        self.internal: Exception = internal
