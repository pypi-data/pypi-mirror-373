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

from typing import Any

from galaxy.error import constant,          \
                         code
from galaxy.error.error import BaseError
from galaxy.utils.type import CompId


class ApplicationError(BaseError):
    """
    classdocs
    """

    def __init__(self,
                 error_code: int,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None else constant.MSG_ERR_APP_DEFAULT
        super(ApplicationError, self).__init__(error_code, message, internal)


class AppCompAlreadyRegisteredError(ApplicationError):
    """
    classdocs
    """

    def __init__(self,
                 comp_def: Any,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None else constant.MSG_ERR_APP_COMP_ALREADY_REGISTERED.format(comp_def)
        super(AppCompAlreadyRegisteredError, self).__init__(code.CODE_ERR_APP_COMP_ALREADY_REGISTERED, message, internal)


class AppReferenceNotFoundError(ApplicationError):
    """
    classdocs
    """

    def __init__(self,
                 id_: CompId,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None else constant.MSG_ERR_APP_REFERENCE_NOT_FOUND.format(id_)
        super(AppReferenceNotFoundError, self).__init__(code.CODE_ERR_APP_REFERENCE_NOT_FOUND, message, internal)


class AppScopeNotSupportedError(ApplicationError):
    """
    classdocs
    """

    def __init__(self,
                 comp_def: Any,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None else constant.MSG_ERR_APP_SCOPE_NOT_SUPPORTED.format(comp_def.scope, comp_def)
        super(AppScopeNotSupportedError, self).__init__(code.CODE_ERR_APP_SCOPE_NOT_SUPPORTED, message, internal)


class AppAbstractCompCannotBeInstantiatedError(ApplicationError):
    """
    classdocs
    """

    def __init__(self,
                 comp_def: Any,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None else constant.MSG_ERR_APP_ABSTRACT_COMP_CANNOT_BE_INSTANTIATED.format(comp_def)
        super(AppAbstractCompCannotBeInstantiatedError, self).__init__(code.CODE_ERR_APP_ABSTRACT_COMP_CANNOT_BE_INSTANTIATED, message, internal)
