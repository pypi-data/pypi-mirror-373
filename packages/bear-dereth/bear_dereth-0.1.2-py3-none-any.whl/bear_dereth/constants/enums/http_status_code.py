"""HTTP status codes."""

from bear_dereth.tools.rich_enums import IntValue as Value, RichIntEnum


class HTTPStatusCode(RichIntEnum):
    """An enumeration of common HTTP status codes."""

    # Informational responses
    CONTINUE = Value(100, "Continue")
    SWITCHING_PROTOCOLS = Value(101, "Switching Protocols")
    PROCESSING = Value(102, "Processing")

    # Success responses
    SERVER_OK = Value(200, "OK")
    CREATED = Value(201, "Created")
    ACCEPTED = Value(202, "Accepted")
    NON_AUTHORITATIVE_INFORMATION = Value(203, "Non-Authoritative Information")
    NO_CONTENT = Value(204, "No Content")
    RESET_CONTENT = Value(205, "Reset Content")
    PARTIAL_CONTENT = Value(206, "Partial Content")

    # Redirection messages
    MULTIPLE_CHOICES = Value(300, "Multiple Choices")
    MOVED_PERMANENTLY = Value(301, "Moved Permanently")
    FOUND = Value(302, "Found")
    SEE_OTHER = Value(303, "See Other")
    NOT_MODIFIED = Value(304, "Not Modified")
    TEMPORARY_REDIRECT = Value(307, "Temporary Redirect")
    PERMANENT_REDIRECT = Value(308, "Permanent Redirect")

    # Client error responses
    BAD_REQUEST = Value(400, "Bad Request")
    UNAUTHORIZED = Value(401, "Unauthorized")
    PAYMENT_REQUIRED = Value(402, "Payment Required")
    FORBIDDEN = Value(403, "Forbidden")
    PAGE_NOT_FOUND = Value(404, "Not Found")
    METHOD_NOT_ALLOWED = Value(405, "Method Not Allowed")
    CONFLICT = Value(409, "Conflict")
    GONE = Value(410, "Gone")
    LENGTH_REQUIRED = Value(411, "Length Required")
    PRECONDITION_FAILED = Value(412, "Precondition Failed")
    PAYLOAD_TOO_LARGE = Value(413, "Payload Too Large")
    URI_TOO_LONG = Value(414, "URI Too Long")
    UNSUPPORTED_MEDIA_TYPE = Value(415, "Unsupported Media Type")
    RANGE_NOT_SATISFIABLE = Value(416, "Range Not Satisfiable")
    EXPECTATION_FAILED = Value(417, "Expectation Failed")
    IM_A_TEAPOT = Value(418, "I'm a teapot")
    MISDIRECTED_REQUEST = Value(421, "Misdirected Request")
    UNPROCESSABLE_CONTENT = Value(422, "Unprocessable Content")
    UNAVAILABLE_FOR_LEGAL_REASONS = Value(451, "Unavailable For Legal Reasons")

    # Additional server error responses
    SERVER_ERROR = Value(500, "Internal Server Error")
    NOT_IMPLEMENTED = Value(501, "Not Implemented")
    BAD_GATEWAY = Value(502, "Bad Gateway")
    SERVICE_UNAVAILABLE = Value(503, "Service Unavailable")
    GATEWAY_TIMEOUT = Value(504, "Gateway Timeout")
    HTTP_VERSION_NOT_SUPPORTED = Value(505, "HTTP Version Not Supported")
    VARIANT_ALSO_NEGOTIATES = Value(506, "Variant Also Negotiates")
    INSUFFICIENT_STORAGE = Value(507, "Insufficient Storage")
    LOOP_DETECTED = Value(508, "Loop Detected")
    NOT_EXTENDED = Value(510, "Not Extended")
    NETWORK_AUTHENTICATION_REQUIRED = Value(511, "Network Authentication Required")


SERVER_ERROR = HTTPStatusCode.SERVER_ERROR
"""Internal Server Error"""
SERVER_OK = HTTPStatusCode.SERVER_OK
"""OK"""
PAGE_NOT_FOUND = HTTPStatusCode.PAGE_NOT_FOUND
"""Not Found"""
BAD_REQUEST = HTTPStatusCode.BAD_REQUEST
"""Bad Request"""
UNPROCESSABLE_CONTENT = HTTPStatusCode.UNPROCESSABLE_CONTENT
"""Unprocessable Content"""
UNAUTHORIZED = HTTPStatusCode.UNAUTHORIZED
"""Unauthorized"""
FORBIDDEN = HTTPStatusCode.FORBIDDEN
"""Forbidden"""
CONFLICT = HTTPStatusCode.CONFLICT
"""Conflict"""
METHOD_NOT_ALLOWED = HTTPStatusCode.METHOD_NOT_ALLOWED
"""Method Not Allowed"""
