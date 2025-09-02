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


class CommandError(BaseError):
    """
    classdocs
    """

    def __init__(self,
                 error_code: int,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None else constant.MSG_ERR_CMD_DEFAULT
        super(CommandError, self).__init__(error_code, message, internal)


class CmdCommandNotSupportedError(CommandError):
    """
    classdocs
    """

    def __init__(self,
                 cmd_name: str,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None else constant.MSG_ERR_CMD_COMMAND_NOT_SUPPORTED.format(cmd_name)
        super(CmdCommandNotSupportedError, self).__init__(code.CODE_ERR_CMD_COMMAND_NOT_SUPPORTED, message, internal)


class CmdInvalidParamsError(CommandError):
    """
    classdocs
    """

    def __init__(self,
                 cmd_name: str,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None else constant.MSG_ERR_CMD_INVALID_PARAMS.format(cmd_name)
        super(CmdInvalidParamsError, self).__init__(code.CODE_ERR_CMD_INVALID_PARAMS, message, internal)


class CmdMandatoryParamsMissingError(CommandError):
    """
    classdocs
    """

    def __init__(self,
                 cmd_name: str,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None else constant.MSG_ERR_CMD_MANDATORY_PARAMS_MISSING.format(cmd_name)
        super(CmdMandatoryParamsMissingError, self).__init__(code.CODE_ERR_CMD_MANDATORY_PARAMS_MISSING, message, internal)


class CmdMandatoryParamsMalformedError(CommandError):
    """
    classdocs
    """

    def __init__(self,
                 cmd_name: str,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None else constant.MSG_ERR_CMD_MANDATORY_PARAMS_MALFORMED.format(cmd_name)
        super(CmdMandatoryParamsMalformedError, self).__init__(code.MSG_ERR_CMD_MANDATORY_PARAMS_MALFORMED, message, internal)


class CmdInvalidParamError(CommandError):
    """
    classdocs
    """

    def __init__(self,
                 cmd_name: str,
                 param: str,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None else constant.MSG_ERR_CMD_INVALID_PARAM.format(cmd_name, param)
        super(CmdInvalidParamError, self).__init__(code.CODE_ERR_CMD_INVALID_PARAM, message, internal)


class CmdNotExistingComponentError(CommandError):
    """
    classdocs
    """

    def __init__(self,
                 cmd_name: str,
                 param: str,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None \
                  else "{} : {}".format(constant.MSG_ERR_CMD_INVALID_PARAM.format(cmd_name, param), constant.MSG_ERR_CMD_NOT_EXISTING_COMPONENT.format(param))
        super(CmdNotExistingComponentError, self).__init__(code.CODE_ERR_CMD_NOT_EXISTING_COMPONENT, message, internal)


class CmdStatusNotSupportedError(CommandError):
    """
    classdocs
    """

    def __init__(self,
                 cmd_name: str,
                 param: str,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None \
                  else "{} : {}".format(constant.MSG_ERR_CMD_INVALID_PARAM.format(cmd_name, param), constant.MSG_ERR_CMD_STATUS_NOT_SUPPORTED.format(param))
        super(CmdStatusNotSupportedError, self).__init__(code.CODE_ERR_CMD_STATUS_NOT_SUPPORTED, message, internal)


class CmdStartNotSupportedError(CommandError):
    """
    classdocs
    """

    def __init__(self,
                 cmd_name: str,
                 param: str,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None \
                  else "{} : {}".format(constant.MSG_ERR_CMD_INVALID_PARAM.format(cmd_name, param), constant.MSG_ERR_CMD_START_NOT_SUPPORTED.format(param))
        super(CmdStartNotSupportedError, self).__init__(code.CODE_ERR_CMD_START_NOT_SUPPORTED, message, internal)


class CmdStopNotSupportedError(CommandError):
    """
    classdocs
    """

    def __init__(self,
                 cmd_name: str,
                 param: str,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None \
                  else "{} : {}".format(constant.MSG_ERR_CMD_INVALID_PARAM.format(cmd_name, param), constant.MSG_ERR_CMD_STOP_NOT_SUPPORTED.format(param))
        super(CmdStopNotSupportedError, self).__init__(code.CODE_ERR_CMD_STOP_NOT_SUPPORTED, message, internal)


class CmdConnectNotSupportedError(CommandError):
    """
    classdocs
    """

    def __init__(self,
                 cmd_name: str,
                 param: str,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None \
                  else "{} : {}".format(constant.MSG_ERR_CMD_INVALID_PARAM.format(cmd_name, param), constant.MSG_ERR_CMD_CONNECT_NOT_SUPPORTED.format(param))
        super(CmdConnectNotSupportedError, self).__init__(code.CODE_ERR_CMD_CONNECT_NOT_SUPPORTED, message, internal)


class CmdCloseNotSupportedError(CommandError):
    """
    classdocs
    """

    def __init__(self,
                 cmd_name: str,
                 param: str,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None \
                  else "{} : {}".format(constant.MSG_ERR_CMD_INVALID_PARAM.format(cmd_name, param), constant.MSG_ERR_CMD_CLOSE_NOT_SUPPORTED.format(param))
        super(CmdCloseNotSupportedError, self).__init__(code.CODE_ERR_CMD_CLOSE_NOT_SUPPORTED, message, internal)


class CmdPauseNotSupportedError(CommandError):
    """
    classdocs
    """

    def __init__(self,
                 cmd_name: str,
                 param: str,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None \
                  else "{} : {}".format(constant.MSG_ERR_CMD_INVALID_PARAM.format(cmd_name, param), constant.MSG_ERR_CMD_PAUSE_NOT_SUPPORTED.format(param))
        super(CmdPauseNotSupportedError, self).__init__(code.CODE_ERR_CMD_PAUSE_NOT_SUPPORTED, message, internal)


class CmdResumeNotSupportedError(CommandError):
    """
    classdocs
    """

    def __init__(self,
                 cmd_name: str,
                 param: str,
                 message: str = None,
                 internal: Exception = None) -> None:
        message = message if message is not None \
                  else "{} : {}".format(constant.MSG_ERR_CMD_INVALID_PARAM.format(cmd_name, param), constant.MSG_ERR_CMD_RESUME_NOT_SUPPORTED.format(param))
        super(CmdResumeNotSupportedError, self).__init__(code.CODE_ERR_CMD_RESUME_NOT_SUPPORTED, message, internal)
