################################################
# All API related exceptions
################################################

import json
import random
from importlib import import_module

#################################################
#  Not ready http codes
#################################################

# NOTE:
#  these codes should be the same since both represent that a background process has started
#  and will need to checked for completion or failure later.
#  Current client expect 321 for futures and waiting is handled by both python and js api
#  Is handled seperately as resourceview.js expects 202 and js api handles multiple requests to
#  wait for futures

http_code_future_not_ready = 321
http_code_blob_not_ready = 321

FUTURE_WAIT_CODES = frozenset([http_code_future_not_ready, http_code_blob_not_ready])

#################################################
#  Generic Exceptions
#################################################

# BQException (request etc from BQCommError) -> BQApiError (anything service, related request/response)
#                                            -> other (anything internal)

# TODO: store request details in future db etc?


class BQException(Exception):
    """
    BQException
    """

    def __init__(self, *args, **kw):  # allow named args
        if kw:
            super().__init__(*args, kw)
        else:
            super().__init__(*args)

    http_code = 500  # should be overwritten to indicate corresponding code
    empty_body = False


class BQApiError(BQException):
    """Exception in API usage"""

    def __init__(self, msg="", response=None, json=None):
        """
        @param: status - error code
        @param: headers - dictionary of response headers
        @param: content - body of the response (default: None)
        """
        super().__init__(
            msg, response, json
        )  # this ensures argument are stored in args .. (so can be passed during serialization)
        # print 'Status: %s'%status
        # print 'Headers: %s'%headers

        if json:
            self.json = json

        if isinstance(response, str):
            self.args = (response,)
        elif hasattr(response, "url"):
            self.response_url = response.url
            self.response_code = response.status_code
            self.response_headers = response.headers.copy()
            try:
                content = response.content
                if content is not None and len(content) > 64:
                    content = f"{content[:64]}...{content[-64:]}"
            except RuntimeError:
                # If content was consumed then just drop the whole thing (see requests/models.py)
                content = "Content unavailable: previously consumed"
            self.args = (content,)

    def __repr__(self):
        return f"{self.__class__.__name__}({super().__str__()})"

    def __str__(self):
        msg = f"{self.__class__.__name__}:{self.args[0]}"
        if hasattr(self, "json"):
            msg += ":" + str(self.json)
        if not hasattr(self, "response_url"):
            return msg
        else:
            return f"{self.response_url}, status={self.response_code}, headers={self.response_headers}, {msg}"

    def get_msg(self):
        return str(self.args[0])


class IllegalOperation(BQApiError):
    """Illegal Operation"""

    http_code = 400


class BQAuthError(BQApiError):
    http_code = 401

    def __repr__(self):
        return "BQAuthError({}, status={}, req headers={}){}".format(
            self.response_url, self.response_code, self.response_headers, self.content
        )


class ForbiddenError(BQApiError):
    http_code = 403


class NotFoundError(BQApiError):
    http_code = 404


class CommErrorFactory:
    @classmethod
    def make(cls, response):
        if response.status_code == 403:
            return BQAuthError(response)
        return BQApiError(response=response)


class BadMediaType(BQApiError):
    """bad media in http header"""

    http_code = 415


class ServiceError(BQApiError):
    """Any error during in a service"""

    http_code = 400


class NoAuthorizationError(BQApiError):
    """User is not authorized for action

    Pass a redirect url if can be resolved
    """

    http_code = (
        401  # TODO: SHOULD BE 403 because this is used for access forbidden; 401 is unauthorized (i.e., not logged in)
    )

    def __init__(self, msg=None, redirect_url=None):
        super().__init__(
            msg
        )  # the celery serializer gets confused by this (https://stackoverflow.com/questions/64370063/django-celery-getting-pickling-error-on-throwing-custom-exception)
        self.redirect_url = redirect_url
        # if msg is not None:
        #    super().__init__(msg)


class InvalidDocument(BQApiError):
    """Document does not match expected schema"""

    http_code = 400


class RenderError(BQApiError):
    """Document could not be rendered in requested format"""

    http_code = 400


#################################################
#  Future service exceptions
#################################################


class FutureNotFoundError(BQApiError):
    """Future not found"""

    http_code = 404


class FutureNotReadyError(BQApiError):
    """Future not ready"""

    http_code = http_code_future_not_ready

    def __init__(self, msg, future=None, retry_after: int | None = None, max_retries: int | None = None, location=None):
        """FutureError
        Args:
          future: a FutureResult
          retry_after: suggested retry
          max_retries: maxium attempts, 0 disables
          location: override retry location
        """
        super().__init__(msg)
        self.future = future
        self.retry_after = retry_after
        self.max_retries = max_retries
        self.location = location

    def __str__(self):
        return super().__str__() + f"({self.retry_after}, {self.max_retries}, {self.location})"


class ConfigurationError(BQApiError):
    """Problem was found with the configuration"""

    http_code = 400


class InvalidQuery(BQApiError):
    """bad query/request structure"""

    http_code = 400


#################################################
#  Data/Index service exceptions
#################################################


class StoreError(BQApiError):
    """non specific store error (should not be used)"""


class TemporaryStoreError(StoreError):
    """an error that may be resolved by retrying the operation after short wait"""

    http_code = 503  # TODO: is this a good code? (currently expected in JS)


class StoreAbortError(StoreError):
    """specific abort condition (in case of web request)"""

    # TODO: can get rid of this?


class VersionMissing(StoreAbortError):
    """no version information provided"""

    http_code = 404


class VersionCheckFailed(StoreAbortError):
    """version precondition failed"""

    http_code = 412


class DocNotModified(StoreAbortError):
    """doc not modified; cached version ok"""

    http_code = 304
    empty_body = True


class DocNotFound(StoreAbortError):
    """doc with uniq not found"""

    http_code = 404


class ProtectedResourceType(StoreAbortError):
    """operation not allowed on that type"""

    http_code = 405


class DuplicateDoc(StoreAbortError):
    """duplicate doc insertion"""

    http_code = 409


class ReferentialIntegrityError(StoreAbortError):
    """operation would violate ref integrity"""

    http_code = 409


class DocAccessForbidden(StoreAbortError):
    """access to doc not permitted"""

    http_code = 403


class IndexNotFound(StoreError):
    """referenced index not found"""

    http_code = 404


#################################################
#  Mount/Directory/Blob service exceptions
#################################################


class DuplicateFile(BQApiError):
    "A duplicate file or resource detected"

    http_code = 409


class NoSuchFileError(BQApiError):
    """Requested files is not available at path"""

    http_code = 404


class BlobNotReadyError(FutureNotReadyError):
    """File is being transferred; try again later"""

    http_code = http_code_blob_not_ready  # expected by resourceview.js


class NotReadyError(BlobNotReadyError):
    "Deprecated"


class ResourceNotFoundError(BQApiError):
    """Raised when resource not found"""

    http_code = 404


class UnknownBlobType(BQApiError):
    """Raised when blob type mismatch"""

    http_code = 400


class DirNotFoundError(BQApiError):
    """Raised when dir not found"""

    http_code = 404


class BadDriverConfigError(BQApiError):
    """Raised when bad driver parameters encountered"""

    http_code = 400


class AlreadyRegisteredError(BQApiError):
    """Raised when file is already registered"""

    http_code = 409


class NotRegisteredError(BQApiError):
    """Raised when file is not registered"""

    http_code = 409


class MountError(BQApiError):
    """Some mount error"""

    http_code = 400


class MountNotFoundError(BQApiError):
    """Mount not found error"""

    http_code = 404


class NoSuchPathError(BQApiError):
    """Path not found"""

    http_code = 404


#################################################
#  Module/Build/Mex service exceptions
#################################################


class ModuleError(BQApiError):
    """Base Module error"""

    http_code = 400


class ModuleNotFoundError(BQApiError):
    """Module not found in system"""

    http_code = 404


class ModuleConflictError(BQApiError):
    """Module conflicts with existing module (e.g., same name but different I/O specs)"""

    http_code = 409


class BuildNotFoundError(BQApiError):
    """Build not found in system"""

    http_code = 404


class MexNotFoundError(BQApiError):
    """Mex not found in system"""

    http_code = 404


class AssociatedBuildNotFoundError(BQApiError):
    """Build associated with Mex not found"""

    http_code = 404


class AssociatedModuleNotFoundError(BQApiError):
    """Module associated with Mex not found"""

    http_code = 404


class ModMexParameterMismatch(BQApiError):
    """Mismatch in parameters between Mex and Module def"""

    http_code = 400


class MexValueError(BQApiError):
    """Bad/Illegal value in mex doc"""

    http_code = 400


#################################################
#  Image service exceptions
#################################################


class ImageServiceException(BQApiError):
    """Raised when any operation or decoder fails

    Attributes:
        code: Response error code, same as HTTP response code
        message: String explaining the exact reason for the failure
    """

    http_code = 400

    def __init__(self, code=400, message=None, msg=None):
        self.http_code = code
        super().__init__(msg=message or msg)


class ImageServiceFuture(FutureNotReadyError):
    """Raised when any operation timeout or is already locked

    Attributes:
        timeout_range: a range of seconds for a re-request: (1, 15)
    """

    def __init__(self, timeout_range=None, location="", msg=None, max_retries: int = 0):
        self.retry_after = random.randint(timeout_range[0], timeout_range[1])
        self.max_retries = max_retries
        self.location = location
        super().__init__(msg="image future")


#################################################
#  Table service exceptions
#################################################


class BadFormat(BQApiError):
    """resource is not in a recognized or allowed format needed for op"""

    http_code = 500


class EntityTooLargError(BQApiError):
    """The requested entity was too large"""

    http_code = 413


class TableServiceFuture(FutureNotReadyError):
    """Raised when any operation timeout or is already locked

    Attributes:
        timeout_range: a range of seconds for a re-request: (1, 15)
    """

    http_code = http_code_future_not_ready

    def __init__(self, timeout_range=None, location="", msg=None):
        self.retry_after = random.randint(timeout_range[0], timeout_range[1])
        self.location = location
        super().__init__(msg="Table access delayed. Come back later.")


#################################################
#  Import/Ingest service exceptions
#################################################


class IngestError(BQApiError):
    """Raised when issue with Ingest/Registration"""

    http_code = 400


class ExportError(BQApiError):
    """Raised when issue with Export"""

    http_code = 400


class TransferError(BQApiError):
    """Raised when issue when transferring"""

    http_code = 400


#################################################
#  Preference exceptions
#################################################


class PreferenceError(BQApiError):
    """Raised when issue with Export"""

    http_code = 400


class NotifyError(BQApiError):
    """Raised when issue with Notify"""

    http_code = 400


#################################################
#  Map between exception and http code
#################################################

# Conversion rules:
# -----------------
#
#   http body                      exception
#
#
# { "exception: "...",     <--      msg='{"message":"blabla", "key1":"xxx", "key2":"yyy"}', json=None, str='{"message":"blabla", "key1":"xxx", "key2":"yyy"}'
#   "message": "blabla",                           (legacy)
#   "key1": "xxx",
#   "key2": "yyy"
# }
#
#
# { "exception": "...",     <-->    msg="blabla", json=None, str="blabla"
#   "message": "blabla"
# }
#
#
# { "exception": "...",     <-->    msg="blabla", json={"message":"blabla", "key1":"xxx", "key2":"yyy"}, str="blabla"
#   "message": "blabla",
#   "key1": "xxx",
#   "key2": "yyy"
# }


def _recreate_exception(class_str: str, msg: str, exc_json: dict) -> Exception:
    try:
        module_path, class_name = class_str.rsplit(".", 1)
        module = import_module(module_path)
        return (
            getattr(module, class_name)(msg=msg, json=exc_json)
            if exc_json is not None
            else getattr(module, class_name)(msg=msg)
        )
    except (ImportError, AttributeError):
        raise ImportError(class_str)


# def exception_to_code(exc: Exception, response, future=None, log=None):
#     # add info to requests.response object based on given exception

#     if isinstance(exc, FutureNotReadyError) and future is not None:
#         # if this was a future not ready, indicate that in the headers and set up retry
#         response.headers["x-viqi-future"] = future.get_future_id()
#         response.location = f"/futures/{future.get_future_id()}/result"
#         response.headers["Retry-After"] = str(future.expected_duration())
#     if isinstance(exc, BQApiError):
#         response.headers["x-viqi-exception"] = f"{exc.__class__.__module__}.{exc.__class__.__qualname__}"
#     response.headers["Content-Type"] = "application/json"
#     if isinstance(exc, BQException):
#         response.status_code = exc.http_code
#         response.headers["x-viqi-exception-msg"] = getattr(exc, "content", "")
#     elif isinstance(exc, NotImplementedError):
#         response.status_code = 501
#     else:
#         response.status_code = 500
#         if log is not None:
#             log.exception('Unexpected exception "%s"', str(exc))
#     try:
#         msg = json.loads(str(exc))
#         # exc_msg = json_msg.get("message")
#         # exc_data = json_msg.get("data")
#     except Exception:
#         msg = {"message": str(exc)}
#     msg = getattr(exc, "json", msg)
#     response.text = json.dumps(
#         {
#             "exception": f"{exc.__class__.__module__}.{exc.__class__.__qualname__}",
#             **msg,
#         }
#     )
#     return response


def code_to_exception(response):
    # recreate exception based on given requests.response object
    code = response.status_code

    if code < 400:  #  and code != 202:
        # not an error
        return

    classname = response.headers.get("x-viqi-exception")

    if classname is None:
        body = response.text
        if not body:
            raise BQApiError(f"Error {code}")
        else:
            raise BQApiError(body)
    else:
        try:
            # HEAD does not return a body but can return an exception
            body = json.loads(response.text)
        except json.JSONDecodeError:
            body = {"message": response.text}

        exc_msg = body.get("message", "")
        if body.keys() > {"exception", "message"}:
            # has additional keys => store as json
            body.pop("exception", None)
            exc_json = body
        else:
            exc_json = None
        raise _recreate_exception(classname, exc_msg, exc_json)
