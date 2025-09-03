# import functools
import copy
import hashlib
import io
import logging
import os
import shutil
import tarfile
import tempfile
import time
import urllib
import urllib.parse
from typing import BinaryIO

import requests
from bq.metadoc.formats import Metadoc

from vqapi.exception import TransferError, code_to_exception, http_code_future_not_ready
from vqapi.util import custom_json_dumps, custom_json_loads

# from vqapi.util import is_uniq_code, normalize_unicode

log = logging.getLogger("vqapi.services")

CHUNK_SZ = 1 * 1024 * 1024  #  1 MB


def handle_file_response(response: requests.Response, fb: BinaryIO, chunk_sz: int = CHUNK_SZ):
    """Helper function for file transfers
     Args:
        response: a streaming response
        an open writable file
     usage:
       with service.some_method (..stream=True) as response, open (, "wb") as ) as fp:
            handle_file_response (response, fp)
    Returns:
      Bytes received
    Raises:
     TransferError
    """
    code_to_exception(response)

    # OK response download
    content_length = response.headers.get("content-length")
    content_md5 = response.headers.get("x-content-md5")
    content_length = content_length is not None and int(content_length)
    content_bytes = 0
    if content_md5 is not None:
        content_hasher = hashlib.md5()
        log.debug("x-content-md5: %s", content_md5)

    try:
        for block in response.iter_content(chunk_size=chunk_sz):  # 1MB
            content_bytes += len(block)
            if content_md5:
                content_hasher.update(block)
            fb.write(block)
        fb.flush()
    except requests.exceptions.RequestException as exc:
        log.error("Network issue %s during download to %s", exc, fb.name)
        raise
    except IOError as exc:
        log.error("File I/O issue %s during download to %s", exc, fb.name)
        raise

    if content_length is not None:
        # content-bytes can be > content-length when accept-encoding is a compressed type: gzip, deflate
        if content_bytes > content_length:
            # raise TransferError(f"Transfer sent extra data: {content_bytes-content_length} bytes ")
            log.info("Transfer sent extra data: %s bytes", content_bytes - content_length)
        if content_bytes < content_length:
            raise TransferError(f"Transfer missing data: {content_length-content_bytes} bytes ")
    if content_md5 is not None and content_md5 != content_hasher.hexdigest():
        raise TransferError("Transfer MD5 did not match")

    return content_bytes


class ResponseFile(io.IOBase):
    """
    IO byte stream to return single file responses. Can be used as context manager.
    """

    def __init__(self, response):
        if isinstance(response, str):
            # file path used by server blob service currently (maybe recode on server side)
            self.stream = open(response, "rb")
            self.response = None
            self.fpath = response
        else:
            response.raw.decode_content = True  # in case of compression
            self.stream = response.raw
            self.response = response
            self.fpath = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stream.close()

    def read(self, size: int = -1) -> bytes:
        """
        Read some bytes from stream.

        Args:
            size: number of bytes to read

        Returns:
            bytes read
        """
        return self.stream.read(size)

    def readall(self) -> bytes:
        """
        Read all bytes from stream.

        Returns:
            bytes read
        """
        return self.stream.read()

    def readinto(self, b):
        raise io.UnsupportedOperation("no readinto in reponse stream")

    def close(self):
        """
        Close stream.
        """
        if self.response is not None:
            self.response.close()
        if self.fpath is not None:
            self.stream.close()

    def write(self, b):
        raise io.UnsupportedOperation("no write in reponse stream")

    def copy_into(self, localpath: str, full_path: bool = True, chunk_sz: int = CHUNK_SZ) -> str:
        """
        Copy this file into localpath/ and return its path.

        Args:
            localpath: local path where to write bytes to (can be a directory)
            full_path: if True, localpath includes the filename; otherwise, localpath is a folder

        Returns:
            path of generated file
        """
        if self.fpath is not None:
            outname = os.path.join(localpath, os.path.basename(self.fpath))
            shutil.copyfile(self.fpath, outname)
            return outname

        try:
            if full_path:
                outname = localpath
                fp = open(localpath, "wb")
            else:
                fp = tempfile.NamedTemporaryFile(dir=localpath, delete=False)
            with self.response as rsp:
                handle_file_response(rsp, fp)

            return fp.name
        finally:
            fp.close()

    def force_to_filepath(self) -> str:
        """
        Force this file into a locally accessible file and return its path.

        Returns:
            path of generated file
        """
        if self.fpath is not None:
            return self.fpath

        with tempfile.NamedTemporaryFile(mode="w+b", prefix="viqicomm", delete=False) as fout:  # who deletes this?
            handle_file_response(self.response, fout)

        return fout.name


class ResponseFolder:
    """
    Class to return folder structure. Can be used as context manager.
    """

    def __init__(self, response):
        if isinstance(response, str):
            # folder path
            self.stream = response
        else:
            # http response => interpret as tarfile
            # self.stream = tarfile.open(fileobj=response.raw, mode='r|')  # this does not work because tarfile needs seeks
            self.stream = tarfile.open(
                fileobj=io.BytesIO(response.content), mode="r|"
            )  # TODO: may lead to out of memory

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not isinstance(self.stream, str):
            self.stream.close()

    def copy_into(
        self,
        localpath: str,
        full_path: bool = True,  # pylint: disable=unused-argument
    ) -> str:
        """
        Copy this folder structure into localpath/ and return its path.

        Args:
            localpath: local path where to write bytes to
            full_path: ignored (just to mirror ResponseFile)

        Returns:
            path of generated file
        """
        if isinstance(self.stream, str):
            outname = os.path.join(localpath, os.path.basename(self.stream))
            shutil.copytree(self.stream, outname)
        else:
            self.stream.extractall(localpath)
            # localpath should now contain a single folder with subfolders/files
            outname = next(
                os.path.abspath(os.path.join(localpath, name))
                for name in os.listdir(localpath)
                if os.path.isdir(os.path.join(localpath, name))
            )
        return outname

    def force_to_filepath(self) -> str:
        """
        Force this folder structure into a locally accessible (tar) file and return its path.

        Returns:
            path of generated file
        """
        with tempfile.NamedTemporaryFile(
            mode="w+b", prefix="viqicomm", suffix=".tar", delete=False
        ) as fout:  # who deletes this?
            if isinstance(self.stream, str):
                # folder path => package it as single tar file
                with tarfile.open(fileobj=fout, mode="w") as tout:  # TODO: could compress here
                    tout.add(self.stream, os.path.basename(self.stream), recursive=True)
            else:
                # is alread tarfile obj => copy to actual file
                shutil.copyfileobj(self.stream.fileobj, fout)
        return fout.name


class FutureResponse:
    def __init__(self, status_code: int, doc: Metadoc):
        self.status_code = status_code
        self._doc = doc

    def doc(self):
        return self._doc

    @property
    def text(self):
        # TODO: hack... return json directly from future service instead one day
        return custom_json_dumps(self._doc.to_json())


####
#### KGK
#### Still working on filling this out
#### would be cool to have service definition language to make these.
#### TODO more service, renders etc.


class BaseServiceProxy:
    # DEFAULT_TIMEOUT=None
    DEFAULT_TIMEOUT = 300  # 5 Min
    # Timout seconds (connect_timeout : max time to connect, request_time : max time to receive response)
    timeout = (50, DEFAULT_TIMEOUT)
    headers = None
    render = None

    def __init__(self, session, service_url):  # noqa
        self.session = session
        self.service_url = service_url  # if isinstance(service_url, str) else service_url.service_url

    def __str__(self):
        return self.service_url

    def construct(self, path, params=None):
        url = self.service_url
        if params:
            path = f"{path}?{urllib.parse.urlencode(params)}"
        if path:
            url = urllib.parse.urljoin(str(url), str(path))
        return url

    def __call__(self, timeout=DEFAULT_TIMEOUT, headers=None, render=None):
        """Allows service global overrides.. used for sub services

        Example:
           meta = session.service("meta")
           meta_fast = meta(timeout=1).get( "/00-XXX")

           meta_special = meta(headers  = { 'my-header' : 'my-value'} )
           meta_special.get( .. )

        """
        svc = copy.copy(self)
        svc.timeout = timeout
        svc.headers = headers
        svc.render = render
        return svc

    # =================== TODO: get rid of render param ============
    # =================== TODO: move parts of formats.py into api section =========================

    def request(
        self, path: str | None = None, params: dict | None = None, method: str = "get", render: str | None = None, **kw
    ):
        """
        Generic REST-type request to the service (should not be called, use service specific functions instead).

        Args:
            path: a path relative to service (maybe a string or list)
            params: a dictionary of value to encode as params
            method: request type (get, put, post, etc)
            render: 'doc'/'etree'/'xml' to request doc response, 'json' for JSON response

        Returns:
            a request.response (INDEPENDENT OF render!)
        """
        if isinstance(path, list):
            path = "/".join(path)

        if path and path[0] == "/":
            path = path[1:]
        if path:
            path = urllib.parse.urljoin(str(self.service_url), str(path))
        else:
            path = str(self.service_url)

        # no longer in session https://github.com/requests/requests/issues/3341
        timeout = kw.pop("timeout", self.timeout)
        headers = kw.pop("headers", self.headers or {})
        render = render or self.render
        data = kw.get("data")
        if isinstance(data, str):  # hacky way to guess content type
            data = data.lstrip()
            if data[0] == "<":
                headers["Content-Type"] = "text/xml"  # TODO: -------------- use formatters on kw['data']!!!!
            elif data[0] in ("{", "["):
                headers["Content-Type"] = "application/json"  # TODO: -------------- use formatters on kw['data']!!!!
        #         if render in ("xml", "etree", "doc"):
        #             headers["Accept"] = "text/xml"
        if render in ("json",):
            headers["Accept"] = "application/json"
        else:
            headers["Accept"] = "text/xml"  # default xml transmission
        # ignore any format request because it is handled via render and headers
        # not all params are dics, they may be a list of tuples for ordered params
        if params is not None and isinstance(params, dict):
            params.pop("format", None)

        response = self.session.c.request(
            url=path,
            params=params,
            method=method,
            timeout=timeout,
            headers=headers,
            **kw,
        )
        return response

    def fetch(self, path=None, params=None, render=None, **kw):
        return self.request(path=path, params=params, render=render, **kw)

    def get(self, path=None, params=None, render=None, **kw):
        return self.request(path=path, params=params, render=render, **kw)

    def post(self, path=None, params=None, render=None, **kw):
        return self.request(path=path, params=params, render=render, method="post", **kw)

    def put(self, path=None, params=None, render=None, **kw):
        return self.request(path=path, params=params, render=render, method="put", **kw)

    def patch(self, path=None, params=None, render=None, **kw):
        return self.request(path=path, params=params, render=render, method="patch", **kw)

    def delete(self, path=None, params=None, render=None, **kw):
        return self.request(path=path, params=params, render=render, method="delete", **kw)

    def fetch_file(self, path=None, params=None, render=None, localpath=None, **kw):
        with open(localpath, "wb") as fb:
            with self.fetch(path=path, params=params, render=render, stream=True, **kw) as response:
                handle_file_response(response, fb)
        return response


class FuturizedServiceProxy(BaseServiceProxy):
    """Base Class for any service that may return a future.

    Handle waiting for futures
    """

    future_wait = True

    def __call__(self, future_wait=True):
        """Create a non-futurized version of a service
        Example:
          dirs = session.service("dirs")   # All calls will wait for futures
          refresh_future = dirs(future_wait=False).refresh(somepath) # return futures allowing client to track progress
        """
        svc = super().__call__()
        svc.future_wait = future_wait
        return svc

    def _wait_for_future(
        self, response: requests.Response, render: str | None, retry_time: int = 5, max_retries: int = 0
    ) -> requests.Response:
        """Wait for a future to be in finished or failed
        Args:
          wait retry_time before checking each future return
          Only allow max_retries (default: disabled)
            throws  requests.exceptions.RetryError if exhausts max_retries
        """
        future_service = self.session.service("futures")
        future_id = response.headers.get("x-viqi-future")
        try:
            future_state = "PENDING"
            retries = 0
            while True:
                future_state = response.doc().get("state")  # closes response
                if future_state in ("FINISHED", "FAILED"):
                    break
                if max_retries > 0 and retries > max_retries:
                    raise requests.exceptions.RetryError(response=response)
                time.sleep(retry_time)
                retries += 1
                log.debug("Future wait:%ss retry:%s", retry_time, retries)
                # Get the next future
                response = future_service.get(future_id, params={"retry": str(retries)}, future_wait=False)
            return future_service.get(f"{future_id}/result", render=render, future_wait=False)
        finally:  # because get_result could throw an exception!
            # try:
            #    future_service.delete(future_id)
            # except FutureNotFoundError:
            # already deleted
            pass

    def _reraise_exception(self, response):
        exc = response.headers.get("x-viqi-exception")
        if exc is not None:
            # exception was returned... re-raise it
            code_to_exception(response)

    def _ensure_future_result(self, response, method="get", render=None, **kw) -> requests.Response:
        """Handle Futures (and Image/Table Futures by waiting for completion"""
        fut = response.headers.get("x-viqi-future")
        retry_time = int(response.headers.get("Retry-After", 1))
        max_retries = int(response.headers.get("x-viqi-max-retries", 0))
        if fut is not None:
            # future was returned => wait for result
            res = self._wait_for_future(response, render, retry_time, max_retries)
            # replace the original future response with a new response with OK code and result doc
            # TODO: how to do this properly?
            # response = FutureResponse(200, res)
            # response = requests.models.Response()
            # response.headers = res.headers
            # response.text = res.text
            # response.status_code = 200
            return res
        #
        # Image/Table futures rely on retrying the original request
        retries = 0
        while response.status_code == http_code_future_not_ready:
            if max_retries > 0 and retries > max_retries:
                raise requests.exceptions.RetryError(response=response)
            time.sleep(retry_time)

            location = response.headers.get("Location", None) or response.url
            retry_url_toks = urllib.parse.urlparse(location)
            path_toks = retry_url_toks.path.strip("/").split("/")  # assume same service
            params = dict(urllib.parse.parse_qsl(retry_url_toks.query, keep_blank_values=True))
            params["retry"] = str(retries)
            log.debug("%s image/table/blob wait:%ss retry:%s", path_toks[0], retry_time, retries)
            response.close()  # Ensure we return connection to pool (if no content read)
            response = self.request(
                path="/".join(path_toks[1:]),
                params=params,
                method=method,
                render=render,
                future_wait=False,
                **kw,
            )
            retries += 1

        return response

    def _render_response(self, res: requests.Response, render: str | None = None) -> Metadoc | requests.Response | str:
        """Render results as requested
        Args:
          res: A Response object
          render: doc|json|None
        Returns:
          a metadoc or
        """

        try:
            if res is None:
                return res
            if render == "doc":
                return res.doc()
            elif render == "etree":
                log.warn("use of render=etree deprecated")
                return Metadoc.convert_back(res.doc())
            elif render == "json":
                return custom_json_loads(res.text)
            else:
                return res
        except Exception:
            log.exception("During render request '%s' to %s", res.text, render)
            raise

    def request(
        self,
        path: str = None,
        params: dict = None,
        method: str = "get",
        render: str = None,
        future_wait: bool | None = None,
        **kw,
    ):
        """
        Generic future-handling REST-type request to the service (should not be called, use service specific functions instead).

        Args:
            path: a path relative to service (maybe a string or list)
            params: a dictionary of value to encode as params
            method: request type (get, put, post, etc)
            render: 'doc'/'etree'/'xml' to request doc response, 'json' for JSON response
            future_wait: if true, wait for result in case future came back; if false, return even if future doc

        Returns:
            a request.response (INDEPENDENT OF render!)
        """
        # enable redirects again; futures use code 321 which is not affected by requests redirect handling
        #         kw["allow_redirects"] = kw.get(
        #             "allow_redirects", False
        #         )  # turn off redirects by default as it will interfere with future handling
        response = super().request(path=path, params=params, method=method, render=render, **kw)

        # handle two special cases: (1) exception came back, (2) future came back
        self._reraise_exception(response)

        if future_wait is None:
            future_wait = self.future_wait
        if future_wait:
            response = self._ensure_future_result(response, method=method, render=render, **kw)

        return response
