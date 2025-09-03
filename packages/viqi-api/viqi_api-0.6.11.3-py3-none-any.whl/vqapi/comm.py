###############################################################################
##  Bisquik                                                                  ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2007,2008,2009,2010,2011                                ##
##     by the Regents of the University of California                        ##
##                            All rights reserved                            ##
##                                                                           ##
## Redistribution and use in source and binary forms, with or without        ##
## modification, are permitted provided that the following conditions are    ##
## met:                                                                      ##
##                                                                           ##
##     1. Redistributions of source code must retain the above copyright     ##
##        notice, this list of conditions, and the following disclaimer.     ##
##                                                                           ##
##     2. Redistributions in binary form must reproduce the above copyright  ##
##        notice, this list of conditions, and the following disclaimer in   ##
##        the documentation and/or other materials provided with the         ##
##        distribution.                                                      ##
##                                                                           ##
##     3. All advertising materials mentioning features or use of this       ##
##        software must display the following acknowledgement: This product  ##
##        includes software developed by the Center for Bio-Image Informatics##
##        University of California at Santa Barbara, and its contributors.   ##
##                                                                           ##
##     4. Neither the name of the University nor the names of its            ##
##        contributors may be used to endorse or promote products derived    ##
##        from this software without specific prior written permission.      ##
##                                                                           ##
## THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS "AS IS" AND ANY ##
## EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED ##
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE, ARE   ##
## DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR  ##
## ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL    ##
## DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS   ##
## OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)     ##
## HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,       ##
## STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN  ##
## ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE           ##
## POSSIBILITY OF SUCH DAMAGE.                                               ##
##                                                                           ##
###############################################################################
"""
SYNOPSIS
========

DESCRIPTION
===========

"""

import itertools
import logging

# import urlparse
# import urllib
import os
import pickle
import posixpath
import urllib.parse
from collections import OrderedDict
from dataclasses import dataclass
from email.message import Message

import requests
from bq.metadoc.formats import InvalidFormat, Metadoc, anyxml_to_etree
from requests import Session
from requests.adapters import HTTPAdapter
from requests.auth import AuthBase, HTTPBasicAuth

# from requests.packages.urllib3.util.retry import Retry
from urllib3 import Retry
from urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool

from .bqclass import BQFactory, BQNode
from .exception import BQApiError, CommErrorFactory, RenderError
from .loggingpool import LoggingHTTPAdapter
from .services import BaseServiceProxy
from .services.factory import ServiceFactory
from .util import is_uniq_code

# from requests.adapters import HTTPAdapter # noqa


# from .RequestsMonkeyPatch import requests_patch#allows multipart form to accept unicode

# KGK deprecated CAS
# try:
#     from .casauth import caslogin
#     CAS_SUPPORT = True
# except ImportError:
#     CAS_SUPPORT = False


log = logging.getLogger("vqapi.comm")

# SERVICES = ['']


# realiably determine mimetype
# https://stackoverflow.com/questions/32330152/how-can-i-parse-the-value-of-content-type-from-an-http-header-response


# Patch Retry to ignore retry-after header for traefik 429 responses
# They are always 1s otherwise, leading to no load reduction and eventual reaching max retries.
# Instead, exponential backoff should be used.
class RetryIgnore429Header(Retry):
    def get_retry_after(self, response):
        if response.status == 429:
            return None
        return super().get_retry_after(response)


def parse_content_type(content_type: str) -> tuple[str, dict[str, str]]:
    _CONTENT_TYPE = "content-type"
    email = Message()
    email[_CONTENT_TYPE] = content_type
    params = email.get_params()
    # The first param is the mime-type the later ones are the attributes like "charset"
    return params[0][0], dict(params[1:])


def str_summary(s):
    """Utility for long string used in logging"""
    if s is None:
        return "Type None"
    if len(s) > 200:
        return f"length {len(s)}: {s[:100]}..{s[-100:]}"
    return s


def decodexml(self):
    """ """
    if not self.content:
        return None
    try:
        mimetype, options = parse_content_type(self.headers["content-type"])
        if mimetype in ("application/xml", "text/xml"):  # TODO: use inputters!!!!
            if self.text == str(None):
                # None was returned from a normally XML returning API fct
                # TODO: should not mark it as XML in the header
                return None
            if self.headers.get("x-viqi-content-type", "") == "application/xml+tag":
                return Metadoc.from_tagxml(self.text)
            else:
                return Metadoc.from_naturalxml(self.text)

        raise RenderError(f"xml render requested on {mimetype} content")
    except InvalidFormat as exc:
        log.error("XML expected: got content-type:%s body:%s", self.headers["content-type"], str_summary(self.text))
        raise RenderError("Bad xml content") from exc


class MexAuth(AuthBase):
    """
    Bisque's Mex Authentication
    """

    def __init__(self, token, user=None):
        """
        Sets a mex authentication for the requests

        @param token: Token for authenticating a mex. The token can contain the user name
        and a user name does not have to be provided.
        @param user: The user the mex is attached. (default: None)
        """
        if user is None:
            self.username = "Mex %s" % (token)
        elif user in token.split(":")[0]:  # check if token contains user
            self.username = "Mex %s" % (token)
        else:
            self.username = f"Mex {user}:{token}"

    def __call__(self, r):
        """
        Sets the authorization on the headers of the requests.
        @param r: the requests
        """
        r.headers["Authorization"] = self.username
        return r


# class BQServer(CachedSession):
class BQServer(Session):
    """A reference to Bisque server
    Allow communucation with a bisque server

    A wrapper over requests.Session
    """

    def __init__(self):
        super().__init__()
        # Disable https session authentication..
        # self.verify = False
        self.root = None

    def authenticate_mex(self, token, user=None):
        """
        Sets mex authorization to the requests

        @param token: this can be a combination of both token and user or just the token
        @param user: the user attached to the mex

        """
        self.auth = MexAuth(token, user=user)

    def authenticate_basic(self, user, pwd):
        """
        Sets basic authorization along with the request

        @param user: The user for the requests.
        @param pwd: The password for the user.
        """
        self.auth = HTTPBasicAuth(user, pwd)

    def prepare_headers(self, user_headers):
        """ """
        headers = {}
        headers.update(self.auth)
        if user_headers:
            headers.update(user_headers)
        return headers

    def prepare_url(self, url, **params):
        """
        Prepares the url

        @param url: if the url is not provided with a root and a root has been provided to the session
        the root will be added to the url
        @param odict: ordered dictionary object, addes to the query in the order provided
        @param params: adds params to query potion of the url

        @return prepared url
        """
        u = urllib.parse.urlsplit(str(url))

        # root
        if u.scheme and u.netloc:
            scheme = u.scheme
            netloc = u.netloc
        elif self.root and u.netloc == "":
            # adds root request if no root is provided in the url
            r = urllib.parse.urlsplit(str(self.root))
            scheme = r.scheme
            netloc = r.netloc
        else:  # no root provided
            raise BQApiError("No root provided")

        # path
        if is_uniq_code(u.path.lstrip("/").split("/", 1)[0]):
            # path starts with uuid => assume data service url
            path = "/data_service/" + u.path.lstrip("/")
        else:
            path = u.path

        # query
        query = list(urllib.parse.parse_qsl(u.query, True))
        unordered_query = []
        ordered_query = []

        if "odict" in params:
            odict = params["odict"]
            del params["odict"]
            if odict and isinstance(odict, OrderedDict):
                while len(odict) > 0:
                    ordered_query.append(odict.popitem(False))

        if params:
            unordered_query = list(params.items())

        query = query + unordered_query + ordered_query
        query = urllib.parse.urlencode(query)

        return urllib.parse.urlunsplit([scheme, netloc, path, query, u.fragment])

    def request(self, method, url, **kw):
        # encode outgoing data as needed
        data = kw.pop("data", None)
        # if data is not None and not isinstance(data, (str, bytes)):
        if isinstance(data, Metadoc):
            # if data is Metadoc, encode as tagxml
            data = data.to_tagxml()
            kw.setdefault("headers", {})["Content-Type"] = "application/xml+tag"
        if data is not None and kw.get("headers", {}).get("Content-Type", None) in (
            "application/xml",
            "text/xml",
            "application/xml+tag",
        ):  # TODO: use formatters!!!
            # ensure xml transport data is properly encoded (requests does not accept unicode str)
            data = data.encode("utf-8")

        # call original request
        try:
            response = super().request(method, url, data=data, **kw)
        except requests.exceptions.ConnectionError:
            log.warning("Connection error: %s %s", method, url)
            raise
        except requests.exceptions.Timeout:
            log.warning("Timeout: %s %s", method, url)
            raise
        except requests.exceptions.RetryError:
            log.warning("Max retries: %s %s", method, url)
            raise
        except requests.exceptions.RequestException:
            log.exception("During: %s %s", method, url)
            raise

        # add on demand xml decoder fct
        setattr(response, "doc", decodexml.__get__(response, requests.Response))
        return response

    def webreq(self, method, url, headers=None, path=None, **params):
        """
        Makes a http GET to the url given

        @param url: the url that is fetched
        @param headers: headers provided for this specific fetch (default: None)
        @param path: the location to where the contents will be stored on the file system (default:None)
        if no path is provided the contents of the response will be returned
        @param timeout: (optional) How long to wait for the server to send data before giving up, as a float, or a (connect timeout, read timeout) tuple

        @return returns either the contents of the rests or the file name if a path is provided

        @exception: BQApiError if the requests returns an error code and message
        """
        log.debug("%s: %s req  header=%s", method, url, headers)
        timeout = params.get(
            "timeout",
        )
        try:
            r = self.request(
                method=method,
                url=url,
                headers=headers,
                stream=(path is not None),
                timeout=timeout,
            )

            r.raise_for_status()
        except requests.exceptions.HTTPError:
            log.exception("issue with %s", r)
            # raise BQApiError(r)
            raise CommErrorFactory.make(r)

        if path:
            with open(path, "wb") as f:
                # f.write(r.content) # write in chunks
                for block in r.iter_content(chunk_size=16 * 1024 * 1024):  # 16MB
                    f.write(block)
                f.flush()
            return f.name
        else:
            if r.doc() is not None:
                return r.doc().to_tagxml()  # for backward compat... callers expect xml string, not Metadoc right now
            else:
                return r.content

    def fetch(self, url, headers=None, path=None):
        return self.webreq(method="get", url=url, headers=headers, path=path)

    def push(
        self,
        url,
        content=None,
        files=None,
        headers=None,
        path=None,
        method="POST",
        boundary=None,
        timeout=None,
    ):
        """
        Makes a http request

        @param url: the url the request is made with
        @param content: an xml document that will be sent along with the url
        @param files: a dictonary with the format {filename: file handle or string}, sends as a multipart form
        @param headers: headers provided for this specific request (default: None)
        @param path: the location to where the contents will be stored on the file system (default:None)
        if no path is provided the contents of the response will be returned
        @param method: the method of the http request (HEAD,GET,POST,PUT,DELETE,...) (default: POST)

        @return returns either the contents of the rests or the file name if a path is provided

        @exception: BQApiError if the requests returns an error code and message
        """
        log.debug(f"POST {url} req {headers}")

        try:  # error checking
            r = self.request(method, url, data=content, headers=headers, files=files, timeout=timeout)
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            log.exception(f"In push request: {method} {url} {r.content}")
            # raise BQApiError(r)
            raise CommErrorFactory.make(r)

        if path:
            with open(path, "wb") as f:
                f.write(r.content)
            return f.name
        else:
            if r.doc() is not None:
                return r.doc().to_tagxml()  # for backward compat... callers expect xml string, not Metadoc right now
            else:
                return r.content

    def pool_info(self):
        """Return connection pool info as a dict"""
        infos = []
        for adapter_prefix, adapter in self.adapters.items():
            if isinstance(adapter, HTTPAdapter):
                pool_manager = adapter.poolmanager
                if hasattr(pool_manager, "pools"):
                    pools = pool_manager.pools
                    for key in pools.keys():
                        pool = pools[key]
                        print(f"  Pool for Host: {key.key_host}")
                        if isinstance(pool, (HTTPConnectionPool, HTTPSConnectionPool)):
                            infos.append(dict(host=key.key_host, max_size=pool.pool.maxsize, size=pool.pool.qsize()))
        return infos


@dataclass(slots=True)
class _session_state:
    """Session state for session used by pickle for serializing session"""

    mex_cookie: str
    service_fields: dict
    session_fields: dict


class BQSession:
    """
    Top level Bisque communication object
    """

    def __init__(self, *, host=None):
        self.environ = dict(os.environ)
        self._reinitialize(host=host)

    def _reinitialize(self, host=None):
        self.c = BQServer()
        self.mex = None
        self.new = set()
        self.dirty = set()
        self.deleted = set()
        self.bisque_root = None
        self.c.root = None
        self.factory = BQFactory(self)
        self.dryrun = False  # Deprecated for removal
        self.delete_mex = None
        self.delete_build = None
        self.service_map = {}
        self.parse_args = None  # initilized by some cmd.py
        self.user = None
        if host is not None:
            self._setup_host(host)

    # Pickle protocol
    def __getstate__(self):
        ## Derived classes can safely override __getstate__
        ## adding elements to state.service_fields or state.session_fields that need to be preserved
        ## state = self.__getstate__()
        ## state.session_fields["myfield"] = self.somefield
        return _session_state(
            mex_cookie=self.c.cookies.get("mex_session"),
            service_fields={"root": self.c.root},
            session_fields={
                "bisque_root": self.bisque_root,
                "service_map": {str(key): str(val) for key, val in self.service_map.items()},
                "parse_args": self.parse_args,
                "environ": self.environ,
            },
        )

    def __setstate__(self, session_state):
        self.c = BQServer()
        for ckey, cval in session_state.service_fields.items():
            setattr(self.c, ckey, cval)
        self.c.cookies.update({"mex_session": session_state.mex_cookie})
        for skey, sval in session_state.session_fields.items():
            setattr(self, skey, sval)
        self._setup_adapters()

        # self.bisque_root = tple[0]
        # self.c = BQServer()
        # self.c.cookies.update({"mex_session": tple[1]})
        # self.c.root = self.bisque_root
        # self.service_map = tple[2]
        # self.parse_args = tple[3]
        # self.factory = BQFactory(self)
        self.delete_mex = None
        self.delete_build = None
        # # self._load_services()

    def copy(self):
        # Need to preserve the adapters as they
        # adapters = self.c.adapters
        newobj = pickle.loads(pickle.dumps(self))
        # newobj.c.adapters = adapters
        return newobj

    ############################
    # Establish a bisque session
    ############################
    def _create_mex(self, user, moduleuri):
        # for now, just create an empty mex doc...
        # TODO: fix this using new module/build/mex service
        url = self.service_url("data_service")
        try:
            # create temp build doc
            build = Metadoc(tag="build", name="temp")
            build_doc = self.postxml(url, build, method="POST")
            self.delete_build = url.rstrip("/") + "/" + build_doc.get("resource_uniq")
            # create temp mex doc pointing to temp build
            mex = Metadoc(tag="mex", name=f"temp:{moduleuri}", value="RUNNING")
            mex.add_tag("build", value=build_doc.get("resource_uniq"))
            self.mex = self.postxml(url, mex, method="POST", view="deep")
            self.delete_mex = url.rstrip("/") + "/" + self.mex.get("resource_uniq")
            # authenticate with temp mex
            mextoken = self.mex.get("resource_uniq")
            self.c.authenticate_mex(mextoken, user)
            return True
        except Exception:
            self._clean_mex()
            return False

        # mex = BQMex()
        # mex.name = moduleuri or 'script:%s' % " ".join (sys.argv)
        # mex.status = 'RUNNING'
        # self.mex = self.save(mex, url=self.service_url('module_service', 'mex'))
        # if self.mex:
        #     mextoken = self.mex.resource_uniq
        #     self.c.authenticate_mex(mextoken, user)
        #     # May not be needed
        #     for c in range (100):
        #         try:
        #             self.load(url = self.service_url('module_service', path = "/".join (['mex', mextoken])))
        #             return True
        #         except BQApiError:
        #             pass

        # TODO: FIX FOR 6... THIS IS BROKEN DUE TO CHANGE IN MODULE SERVICE
        #         module_service = self.service('module_service')
        #         module_name = "script:" + sys.argv[0]
        #         mex = etree.Element ('mex', name = module_name, value="RUNNING", type = moduleuri)
        #         mex_response = module_service.create_mex(mex)
        #         if mex_response.status_code == 200:
        #             self.mex = self.factory.from_etree(mex_response.xml())
        #             authorization = mex_response.headers.get('Authorization')
        #             auth_type, auth_token = authorization.split(' ')
        #             if auth_type.lower () == "mex":
        #                 self.c.authenticate_mex (auth_token)
        #                 return True
        #         return False

    def _clean_mex(self):
        # remove any temp mex and build docs
        # url = self.service_url("data_service")
        if self.delete_mex is not None:
            self.deletexml(self.delete_mex)
            self.delete_mex = None
        if self.delete_build is not None:
            self.deletexml(self.delete_build)
            self.delete_build = None

    def _check_session(self):
        """Used to check that session is actuall active"""
        auth = self.service("auth_service")
        try:
            r = auth.get("session", render="doc")  # self.fetchxml (self.service_url("auth_service", 'session'))
            users = r.findall("./user") if r else []
            return len(users) > 0
        except BQApiError:
            return False

    def _setup_adapters(
        self,
        retries=30,
        backoff_factor=1,
        status_forcelist=frozenset([413, 429, 502, 503, 504]),
    ):
        """Add requests/urrlib3 Adapters ..
           The core adapter adds client side retries for http response  code in state_forcelist
           Args:
             retries: Max number  of retries before giving up (throws exception urllib3.exceptions.MaxRetryError)
            backoff_factor: sleep for  {backoff factor} * (2 ** ({number of total retries} - 1)) on retry
            status_forcelist : http Status codes that  will retry

        urllib3  Retry.BACKOFF_MAX is set to 120 so 30 retries will be 3071 seconds before failure (50 min)
                 https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html
        """
        # This allows other adapter to not be overwritten by us
        if self.bisque_root in self.c.adapters:
            return

        retry = RetryIgnore429Header(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            backoff_jitter=0.5,
            status_forcelist=status_forcelist,
            respect_retry_after_header=True,
            allowed_methods=frozenset(
                {"DELETE", "GET", "HEAD", "OPTIONS", "PUT", "TRACE", "POST", "PATCH"}
            ),  # include POST and PATCH retries
            # (TODO: need to make sure all POST/PATCH requests use etag versioning)
        )
        retry.RETRY_AFTER_STATUS_CODES = frozenset([413, 429, 502, 503, 504])
        # pool_conectons : urrlib3 cached number of hosts
        # pool_maxsize : number of connection per host
        # pool_block : do not go past maxsize connections report error
        # adapter = HTTPAdapter(max_retries=retry, pool_connections=5, pool_maxsize=10, pool_block=False)
        adapter = LoggingHTTPAdapter(max_retries=retry, pool_connections=5, pool_maxsize=16, pool_block=True)
        self.c.mount(self.bisque_root, adapter)

    def _setup_host(self, host):
        """Initialize the session to send requests to a specific host"""
        self.bisque_root = host
        self.c.root = host
        self._setup_adapters()
        self._load_services()

    # def init(
    #     self,
    #     bisque_url,
    #     credentials=None,
    #     moduleuri=None,
    #     create_mex=False,
    #     enable_cache=False,
    # ):
    #     self.bisque_root = self.c.root = bisque_url
    #     self.setup_retry()
    #     self._load_services()
    #     if credentials:
    #         if credentials[0].lower() == "mex":
    #             return self.init_mex(bisque_url, credentials[1])
    #         auth_service = self.service("auth_service")
    #         logins = auth_service.login_providers()
    #         login_type = None
    #         if logins is not None and logins[0]:
    #             login_type = logins[0].path_query("./type")[0].get_value()
    #         if login_type == "cas":
    #             return self.init_cas(
    #                 credentials[0],
    #                 credentials[1],
    #                 bisque_root=bisque_url,
    #                 moduleuri=moduleuri,
    #                 create_mex=create_mex,
    #                 enable_cache=enable_cache,
    #             )
    #         return self.init_local(
    #             user=credentials[0],
    #             pwd=credentials[1],
    #             bisque_root=bisque_url,
    #             moduleuri=moduleuri,
    #             create_mex=create_mex,
    #             enable_cache=enable_cache,
    #         )
    #     return self

    def init_local(
        self,
        user,
        pwd,
        moduleuri=None,
        bisque_root=None,
        create_mex=True,
        as_user=None,
        enable_cache=False,
    ):
        if bisque_root:
            self._setup_host(bisque_root)

        # Switch user if needed
        user_session = {}
        if user is not None:
            user_session = self.login(user, pwd)

        session = self
        if as_user and "admin" in user_session.get("groups", ""):
            admin = self.service("admin")
            sess_alias = admin.login_as(as_user)
            auth = self.service("auths")
            user_session = auth.get_session()
            if not user_session:
                log.error("Session failed to be created.. please check credentials")
                return None
            sess_alias.user = as_user
            session = sess_alias

        session.mex = None
        session.cache_enable(enable_cache)

        if user is not None and create_mex and moduleuri:
            session._create_mex(user, moduleuri)

        session.c.auth = None
        # atexit.register(self.logout)

        return session

    def init_mex(self, mex_url, token, user=None, bisque_root=None, enable_cache=False):
        if bisque_root is None:
            # This assumes that bisque_root is http://host.org:port/
            # mex_tuple = list(urllib.parse.urlparse(mex_url))
            # mex_tuple[2:5] = "", "", ""
            # bisque_root = urllib.parse.urlunparse(mex_tuple)
            o = urllib.parse.urlparse(mex_url)
            bisque_root = o._replace(path="", params="", query="", fragment="").geturl()

        self._setup_host(bisque_root)
        self.c.authenticate_mex(token, user=user)
        self.mex = self.fetchxml(mex_url, view="deep")
        if self.mex is None:
            log.error("Invalid session authentication")
            self.c.auth = None
        self.cache_enable(enable_cache)
        return self

    def login(self, user, pwd):
        """Login as user and return a session with groups etc"""
        auth = self.service("auths")
        user_session = auth.login(user, pwd)
        if not user_session:  # is not None and not session._check_session():  # Forces cookie load
            log.error("Session failed to be created.. please check credentials")
            return None

        self.user = user_session["username"]
        return user_session

    def logout(self):
        """
        Close and logout current session.
        """
        auth = self.service("auths")
        return auth.logout()

    def cache_enable(self, enabled: bool = False):
        # This is an obfuscated variable .. see https://github.com/requests-cache/requests-cache/blob/main/requests_cache/session.py
        # self.c._disabled = not enabled
        pass

    def clear(self):
        "Remove cookies from this connection"
        self._reinitialize(self.c.root)

    def close(self):
        self._clean_mex()
        self.c.close()

    def parameter(self, name):
        if self.mex is None:
            return None
        res = self.mex.path_query("inputs//%s" % name)
        return res[0] if len(res) == 1 else (res if len(res) > 1 else None)

    def parameter_value(self, name=None, p=None):
        # """
        # Get value of mex input parameter with given name.
        # Returns single value, list of values, or a metadoc if complex value.
        # """
        if p is None:
            p = self.parameter(name)
        else:
            name = p[0].tag if isinstance(p, list) else p.tag

        if p is None:
            return None

        if isinstance(p, list):
            # multiple parameters with same name => list of parameters
            r = []
            for vv in p:
                r.append(vv.value)
            return r

        if len(p) == 0 or p.get("type", "").lower() in (
            "resource",
            "image",
            "table",
        ):  # TODO: define "leaf" more formally
            # this is a leaf => just return value
            return p.value

        values = p.path_query("./value")
        if len(values) >= 1:
            # has "value" children => return list of values
            r = []
            for vv in values:
                r.append(vv.value)
            return r

        # neither single value nor list of values => return subtree
        return p

    def parameters(self):
        p = {}
        if self.mex is None:
            return p
        inputs = self.mex.path_query("inputs//*")
        for i in inputs:
            p[i.tag] = self.parameter_value(p=i)
        return p

    def get_mex_inputs(self):
        # """
        # Get all input parameters in mex.
        #
        # @return: map parameter name -> {'type':..., 'value':..., ...} or [ map parameter name -> {'type':..., 'value':..., ...}, ... ] if blocked iter
        # """

        def _xml2dict(e):
            kids = {key: e.attrib[key] for key in e.attrib if key in ["type", "value"]}
            if e.text:
                kids["value"] = e.text
            for k, g in itertools.groupby(e, lambda x: x.tag):
                g = [_xml2dict(x) for x in g]
                kids[k] = g
            return kids

        def _get_mex_params(mextree):
            p = {}
            for inp in mextree.path_query("inputs/*"):
                p[inp.tag] = _xml2dict(inp)
            p["mex_url"] = {"value": self.c.prepare_url(mextree.get("uri"))}
            return p

        # assemble map param name -> param value
        if self.mex is None:
            return {}
        # check if outside is a block mex
        if self.mex.get("type") == "block":
            res = []
            for inner_mex in self.mex.path_query("./mex"):
                res.append(_get_mex_params(inner_mex))
        else:
            res = _get_mex_params(self.mex)
        return res

    def get_mex_outputs(self):
        # """
        # Get all outputs in mex.
        # """
        if self.mex is None:
            return {}
        # re-fetch mex to get outputs
        mex = self.fetchxml(self.mex.get("uri"), view="deep,clean")
        outp = mex.path_query("outputs")
        if not outp:
            return {}
        return outp[0].to_json()["outputs"] or {}

    def get_mex_execute_options(self):
        # """
        # Get execute options in mex.
        #
        # @return: map option name -> value
        # """
        p = {}
        if self.mex is None:
            return p
        for exop in self.mex.path_query("execute_options/*"):
            p[exop.tag] = exop.text
        return p

    def fetchxml(self, url, path=None, **params):
        # """
        # Fetch an xml object from the url
        #
        # @param: url - A url to fetch from
        # @param: path - a location on the file system were one wishes the response to be stored (default: None)
        # @param: odict - ordered dictionary of params will be added to url for when the order matters
        # @param: params - params will be added to url
        #
        # @return Metadoc
        # """
        url = self.c.prepare_url(url, **params)
        log.debug("fetchxml %s " % url)
        if path:
            return self.c.fetch(
                url,
                headers={
                    "Content-Type": "application/xml+tag",
                    "Accept": "application/xml+tag",
                },
                path=path,
            )
        else:
            r = self.c.fetch(
                url,
                headers={
                    "Content-Type": "application/xml+tag",
                    "Accept": "application/xml+tag",
                },
            )
            return Metadoc.from_tagxml(r)

    def postxml(self, url, xml, path=None, method="POST", **params):
        # """
        # Post xml allowed with files to bisque
        #
        # @param: url - the url to make to the request
        # @param: xml - an xml document that is post at the url location (accepts either string or Metadoc)
        # @param: path - a location on the file system were one wishes the response to be stored (default: None)
        # @param method - the method of the http request (HEAD,GET,POST,PUT,DELETE,...) (default: POST)
        # @param: odict - ordered dictionary of params will be added to url for when the order matters
        # @param: params - params will be added to url
        #
        # @return: Metadoc or path to the file were the response was stored
        # """

        if not isinstance(xml, (str, bytes)):
            xml = xml.to_tagxml()

        log.debug(f"postxml {url}  content {xml} ")

        url = self.c.prepare_url(url, **params)

        try:
            r = None
            if not getattr(self, "dryrun", False):
                r = self.c.push(
                    url,
                    content=xml,
                    method=method,
                    path=path,
                    headers={
                        "Content-Type": "application/xml+tag",
                        "Accept": "application/xml+tag",
                    },
                )
            if path is not None:
                return r
            return r and Metadoc.from_tagxml(r)
        except InvalidFormat as e:
            log.exception("Problem with post response %s", e)
            return r

    def deletexml(self, url):
        # "Delete a resource"
        url = self.c.prepare_url(url)
        r = self.c.webreq(method="delete", url=url)
        return r

    #     def fetchblob(self, url, path=None, **params):
    #         """
    #             Requests for a blob
    #
    #             @param: url - filename of the blob
    #             @param: path - a location on the file system were one wishes the response to be stored (default: None)
    #             @param: params -  params will be added to url query
    #
    #             @return: contents or filename
    #         """
    #         u = urllib.parse.urlsplit(str(url))
    #         if is_uniq_code(u.path.lstrip('/').split('/',1)[0]):
    #             # path starts with uuid => add blobs prefix
    #             new_u = list(u)
    #             new_u[2] = '/blobs/' + u.path.lstrip('/')
    #             url = urllib.parse.urlunsplit(new_u)
    #         url = self.c.prepare_url(url, **params)
    #         #return self.c.fetch(url, path=path )
    #         blob_service = self.service ("blobs")
    #         if path is not None:
    #             response = blob_service.fetch_file (path = url, localpath=path)
    #             return path
    #         else:
    #             response = blob_service.fetch  (path= url)
    #             return response.content

    #     def postblob(self, filename, xml=None, path=None, method="POST", **params):
    #         """
    #             Create Multipart Post with blob to blob service
    #
    #             @param filename: filename of the blob
    #             @param xml: xml to be posted along with the file
    #             @param params: params will be added to url query
    #             @return: a <resource type="uploaded" <image> uri="URI to BLOB" > </image>
    #         """
    #
    #         import_service = self.service ("import")
    #         if xml!=None:
    #             if not isinstance(xml, (str, bytes)):
    #                 xml = xml.to_tagxml()
    #         response = import_service.transfer (filename=filename, xml=xml)
    #         if response.status_code != requests.codes.ok: # pylint: disable=no-member
    #             #raise BQApiError(response)
    #             raise CommErrorFactory.make(response)
    #
    #         return response.content

    # import_service_url = self.service_url('import', path='transfer')
    # if import_service_url is None:
    #     raise BQApiError('Could not find import service to post blob.')
    # url = self.c.prepare_url(import_service_url, **params)
    # if xml!=None:
    #     if not isinstance(xml, (str, bytes)):
    #         xml = self.factory.to_string(xml)
    # fields = {}
    # if filename is not None:
    #     filename = normalize_unicode(filename)
    #     fields['file'] = (filename, open(filename, 'rb'), 'application/octet-stream')
    # if xml is not None:
    #     fields['file_resource'] = xml
    # if fields:
    #     # https://github.com/requests/toolbelt/issues/75
    #     m = MultipartEncoder(fields = fields )
    #     m._read = m.read
    #     m.read = lambda size: m._read (8129*1024) # 8MB
    #     return self.c.push(url,
    #                        content=m,
    #                        headers={'Accept': 'text/xml', 'Content-Type':m.content_type},
    #                        path=path, method=method)
    # raise BQApiError("improper parameters for postblob: must use paramater xml or filename or both ")

    def service_url(self, service_type, path="", query=None):
        service = self.service(service_type)
        return service.construct(path, query)
        # root = self.service_map.get(service_type, None)
        # if root is None:
        #    raise BQApiError('Not a service type')
        # if query:
        #    path = "{}?{}".format(path, urllib.parse.urlencode(query))
        # return urllib.parse.urljoin(str(root), str(path))

    def _load_services(self):
        self.service_map = {"services": posixpath.join(self.c.root, "services")}
        services = self.service("services")
        try:
            service_list = services.get(timeout=5).doc()
            smap = {}
            for service in service_list:
                smap[service.get("type")] = service.text
                new_name = ServiceFactory.RENAMED_SERVICES.get(service.get("type"))
                if new_name is not None:
                    smap[new_name] = service.text
            self.service_map = smap
        except BQApiError as ce:
            log.error(f"While loading services {ce}")
            raise
        except requests.exceptions.Timeout:
            log.error("Timeout fetching services.. system unavailable?")
            raise BQApiError("System unavailable")

    def service(self, service_name: str) -> BaseServiceProxy:
        """
        Return a sevice for this session.

        Args:
            service_name: name of the service (e.g., "mexes" or "mex_service")

        Returns:
            service proxy
        """
        if not self.service_map:
            self._load_services()
        if isinstance(self.service_map.get(service_name, ""), str):
            self.service_map[service_name] = ServiceFactory.make(self, service_name)
        return self.service_map[service_name]

    #############################
    # Classes and Type
    #############################
    def element(self, ty, **attrib):
        elem = Metadoc(tag=ty, **attrib)
        return elem

    def append(self, mex, tags=None, gobjects=None, children=None):
        tags = tags or []
        gobjects = gobjects or []
        children = children or []

        def append_mex(mex, type_tup):
            type_, elems = type_tup
            for tg in elems:
                if isinstance(tg, dict):
                    tg = Metadoc.from_json(tg)
                elif isinstance(tg, Metadoc):
                    pass
                elif isinstance(tg, BQNode):
                    tg = Metadoc(et=anyxml_to_etree(BQFactory.to_etree(tg)))
                else:
                    try:
                        tg = Metadoc(et=anyxml_to_etree(tg))
                    except Exception:
                        raise BQApiError("bad values in tag/gobject list %s" % tg)
                mex.append(tg)

        append_mex(mex, ("tag", tags))
        append_mex(mex, ("gobject", gobjects))
        for elem in children:
            append_mex(mex, elem)

    ##############################
    # Mex
    ##############################
    def update_mex(self, status, tags=None, gobjects=None, children=None, reload=False, merge=False):
        # """save an updated mex with the addition
        #
        # @param status:  The current status of the mex
        # @param tags: list of Metadoc|JSON dict objects (can be nested) of form { 'name': 'value', ... }
        # @param gobjects: list of Metadoc|JSON dict objects (can be nested) of form { 'name': 'value', ... }
        # @param children: list of tuple (type, obj array) i.e [('mex', [dict1, dict2, ...]), ('bla', [dict3, dict4, ...])]
        # @param reload:
        # @param merge: merge "outputs"/"inputs" section if needed
        # @return
        # """
        tags = tags or []
        gobjects = gobjects or []
        children = children or []

        attr_only = not any((tags, gobjects, children))

        # IF merge is requested, check if needed
        if merge and not attr_only:
            mex = self.fetchxml(
                self.mex.get_attr("uri"), view="deep"
            )  # get old version of MEX, so it can be merged if needed
            mex.text = status
            bq5_merge = False  # do the merge here
        else:
            mex = Metadoc(tag="mex", value=status, uri=self.mex.get_attr("uri"))
            bq5_merge = not attr_only  # True  # let the server merge (deprecated!)

        # self.mex.value = status
        def append_mex(mex, type_tup):
            (
                type_,
                elems,
            ) = type_tup  # why was this type_ needed? can't we just use JSON encoded fragments?
            for tg in elems:
                if isinstance(tg, dict):
                    tg = Metadoc.from_json(tg)
                elif isinstance(tg, Metadoc):  # pylint: disable=protected-access
                    pass
                else:
                    raise BQApiError("bad values in tag/gobject list %s" % tg)
                was_merged = False
                if merge and tg.tag in ["inputs", "outputs"]:
                    hits = mex.path_query("./%s" % tg.tag)
                    if hits:
                        assert len(hits) == 1
                        hits[0].extend(list(tg))
                        was_merged = True
                        log.debug("merged '%s' section in MEX", tg.tag)
                if not was_merged:
                    mex.append(tg)

        append_mex(mex, ("tag", tags))
        append_mex(mex, ("gobject", gobjects))
        for elem in children:
            append_mex(mex, elem)

        # mex = { 'mex' : { 'uri' : self.mex.uri,
        #                  'status' : status,
        #                  'tag' : tags,
        #                  'gobject': gobjects }}
        content = self.postxml(
            self.mex.get_attr("uri"),
            mex,
            view="deep" if reload else "short",
            bq5_merge=bq5_merge,
            method="PUT",
            attr_only="1" if attr_only else "0",
        )
        if reload and content is not None:
            self.mex = content
            return self.mex
        return None

    def finish_mex(self, status="FINISHED", tags=None, gobjects=None, children=None, msg=None):
        tags = tags or []
        gobjects = gobjects or []
        children = children or []

        if msg is not None:
            tags.append({"message": msg})
        try:
            # RETRIES for finish MEX?
            return self.update_mex(
                status,
                tags=tags,
                gobjects=gobjects,
                children=children,
                reload=False,
                merge=True,
            )
        except BQApiError as ce:
            log.error("Problem during finish mex %s", str(ce.response_headers))
            try:
                return self.update_mex(
                    status="FAILED",
                    tags=[{"error_message": "Error during saving (status %s)" % ce.response_code}],
                )
            except Exception:
                log.exception("Cannot finish/fail Mex ")

    def fail_mex(self, msg):
        if msg is not None:
            tags = [{"error_message": msg}]
        self.finish_mex(status="FAILED", tags=tags)

    def _begin_mex(self, moduleuri):
        # """create a mex on the server for this run"""
        pass

    ##############################
    # Module control
    ##############################
    def run_modules(self, module_list, pre_run=None, post_run=None, callback_fct=None):
        # """Run one or more modules in parallel.
        #
        #:param module_list: List of modules to run
        #:type  module_list: [ { moduleuri: ..., inputs: { param1:val1, param2:val2, ...}, parent_mex: ... }, {...}, ... ]
        #:param pre_run: module entrypoint to call before run (or None if no prerun)
        #:type pre_run: str
        #:param post_run: module entrypoint to call after run (or None if no postrun)
        #:type post_run: str
        #:param callback_fct: function to call on completion (None: block until completion)
        #:type  callback_fct: fct(mex_list=list(str))
        #:returns: list of mex URIs, one for each module
        #:rtype: list(str)
        # """
        # TODO: create MEX according to params and POST it to module_service
        pass

    #     ##############################
    #     # Resources
    #     ##############################
    #     def query(self, resource_type, **kw):
    #         """Query for a resource
    #         tag_query=None, tag_order=None, offset=None, limit=None
    #         """
    #         results = []
    #         queryurl = self.service_url ('data_service', path=resource_type, query=kw)
    #         items = self.fetchxml (queryurl)
    #         for item in items:
    #             results.append (item)
    #         return results
    #
    #
    def load(self, url, **params):
        """Load a bisque object"""
        # if view not in url:
        #    url = url + "?view=%s" % view
        try:
            xml = self.fetchxml(url, **params)
            if xml.tag == "response":
                xml = xml[0]
            bqo = self.factory.from_etree(xml.to_tagxml_etree())
            return bqo
        except BQApiError as ce:
            log.exception("communication issue while loading %s" % ce)
            return None

    #
    #     def delete(self, bqo, url=None, **kw):
    #         "Delete an object and all children"
    #         url = bqo.uri or url
    #         if url is not None:
    #             return self.deletexml(url)
    #
    #
    def save(self, bqo, url=None, **kw):
        try:
            # original = bqo

            # Find an object (or parent with a valild uri)
            url = url or bqo.uri
            if url is None:
                while url is None and bqo.parent:
                    bqo = bqo.parent
                    url = bqo.parent.uri
            if url is None:
                url = self.service_url("data_service")

            # TODO: remove hack: if url ends with '/tag' or '/gobject', assume we append new child, rather than overwriting
            if url.endswith("/tag") or url.endswith("/gobject"):
                method = "POST"
                url = url.rsplit("/", 1)[0]
            else:
                method = "PUT"

            xml = Metadoc(et=anyxml_to_etree(self.factory.to_etree(bqo)))
            xml = self.postxml(url, xml, method=method, **kw)
            return xml is not None and self.factory.from_etree(xml.to_tagxml_etree())

        except BQApiError as ce:
            log.exception("communication issue while saving %s", ce)
            return None


#
#     def saveblob(self, bqo, filename):
#         """Save a blob to the server and return metadata structure
#         """
#
#         try:
#             xml =  self.factory.to_etree(bqo)
#             xmlstr = self.postblob (filename=filename, xml= xml)
#             xmlet  = self.factory.string2etree (xmlstr)
#             if xmlet.tag == 'resource' and xmlet.get ('type') == 'uploaded':
#                 # return inside
#                 bqo =  self.factory.from_etree(xmlet[0])
#                 return bqo
#             return None
#         except BQApiError as ce:
#             log.exception('communication issue while saving %s' , filename)
#             return None
