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

MSG_ERR_DEFAULT = "An error occurred"

# Application Error Messages
MSG_ERR_APP_DEFAULT = "An applicative error occurred"
MSG_ERR_APP_COMP_ALREADY_REGISTERED = "The component definition {} is already registered"
MSG_ERR_APP_REFERENCE_NOT_FOUND = "The reference {} can not be found"
MSG_ERR_APP_SCOPE_NOT_SUPPORTED = "The scope {} defined for the component {} is not supported"
CODE_ERR_APP_ABSTRACT_COMP_CANNOT_BE_INSTANTIATED = "The component {} is abstract and can not be instantiated"

# System Error Codes
MSG_ERR_SYS_DEFAULT = "A system error occurred"

# Network Error Codes
MSG_ERR_NET_DEFAULT = "A network error occurred"
MSG_ERR_NET_MAX_RECONNECT_RETRIES = "Unable to connect to {}. The maximum number of attempts ({}) has been reached"
MSG_ERR_NET_DDOS_PROTECTION = ""
MSG_ERR_NET_REQUEST_TIMEOUT = ""
MSG_ERR_NET_PASSWORD_EXPIRED = "The password of the user {} has expired."
MSG_ERR_NET_HTTP_INTERNAL_SERVER_ERROR = "The HTTP server responded with the error status code {}"

# Command Error Codes
MSG_ERR_CMD_DEFAULT = "A command error occurred"
MSG_ERR_CMD_COMMAND_NOT_SUPPORTED = "The requested command {} is not supported"
MSG_ERR_CMD_INVALID_PARAMS = "The parameters of the requested command {} are not supported"
MSG_ERR_CMD_MANDATORY_PARAMS_MISSING = "Some mandatory parameters for the requested command {} are missing"
MSG_ERR_CMD_MANDATORY_PARAMS_MALFORMED = "The requested command {} is called with invalid parameters"
MSG_ERR_CMD_INVALID_PARAM = "The parameter {} of the requested command {} is invalid"
MSG_ERR_CMD_NOT_EXISTING_COMPONENT = "The component {} does not exist"
MSG_ERR_CMD_STATUS_NOT_SUPPORTED = "The status method is not supported by the component {}"
MSG_ERR_CMD_START_NOT_SUPPORTED = "The start method is not supported by the component {}"
MSG_ERR_CMD_STOP_NOT_SUPPORTED = "The stop method is not supported by the component {}"
MSG_ERR_CMD_CONNECT_NOT_SUPPORTED = "The connect method is not supported by the component {}"
MSG_ERR_CMD_CLOSE_NOT_SUPPORTED = "The close method is not supported by the component {}"
MSG_ERR_CMD_PAUSE_NOT_SUPPORTED = "The pause method is not supported by the component {}"
MSG_ERR_CMD_RESUME_NOT_SUPPORTED = "The resume method is not supported by the component {}"

# Service Error Codes
MSG_ERR_SERVICE_DEFAULT = "A service error occurred"

# Input-Output Error Code
MSG_ERR_IO_DEFAULT = "An Input-Output error occurred"
MSG_ERR_IO_FILE_NOT_EXISTING = "The file {} does not exist"
MSG_ERR_IO_FILE_WRONG_FORMAT_OR_MALFORMED = "The file {} includes an error"
MSG_ERR_IO_FORMAT_NOT_SUPPORTED = "The format {} is not supported"

# Database Error Codes
MSG_ERR_DB_DEFAULT = "A Database error occurred"
