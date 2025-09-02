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

from galaxy.error import constant,          \
                         code
from galaxy.error.error import BaseError


class NetworkError(BaseError):
    """
    classdocs
    """

    def __init__(self,
                 error_code: int,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None else constant.MSG_ERR_NET_DEFAULT
        super(NetworkError, self).__init__(error_code, message, internal)


class NetPasswordExpiredError(NetworkError):
    """
    classdocs
    """

    def __init__(self,
                 user_id: str,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None else constant.MSG_ERR_NET_PASSWORD_EXPIRED.format(user_id)
        super(NetPasswordExpiredError, self).__init__(code.CODE_ERR_NET_PASSWORD_EXPIRED, message, internal)


class NetHTTPInternalServerError(NetworkError):
    """
    classdocs
    """

    def __init__(self,
                 status: int,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None else constant.MSG_ERR_NET_HTTP_INTERNAL_SERVER_ERROR.format(status)
        super(NetHTTPInternalServerError, self).__init__(code.CODE_ERR_NET_HTTP_INTERNAL_SERVER_ERROR, message, internal)
