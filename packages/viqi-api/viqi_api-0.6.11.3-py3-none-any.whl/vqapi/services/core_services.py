# import functools
import enum
import io
import logging
import os
import pickle
import posixpath
import shutil
import tempfile
from urllib.parse import quote as urlquote
from urllib.parse import unquote as urlunquote
from collections.abc import Collection

import requests
from bq.metadoc.formats import InvalidFormat, Metadoc

from vqapi.exception import (
    BQApiError,
    NoSuchPathError,
    RenderError,
    ResourceNotFoundError,
    code_to_exception,
)
from vqapi.util import is_uniq_code

from .base_proxy import (
    BaseServiceProxy,
    FuturizedServiceProxy,
    ResponseFile,
    ResponseFolder,
)

# from typing import Optional


# from botocore.credentials import RefreshableCredentials
# from botocore.session import get_session


log = logging.getLogger("vqapi.services")


#################################################
#  Blob storage level
#  (not all levels supported by all drivers)
#################################################


class StorageLevel(enum.IntEnum):
    unknown = -999
    # ProcessMemory = 0 # Unshared In memory, local fs
    # LocalFS  = 5

    DB = 10
    Shared = 20  # FS Shared, Redis, DB   ServiceShared
    ObjectStorage = 30
    ObjectStorageIA = 40
    Glacier = 50
    GlacierIA = 60
    GlacierDeep = 70

    def __str__(self):
        return self.name


################### Helpers ######################


def _prepare_mountpath(path: str) -> str:
    if path.startswith("store://"):
        path = path[len("store://") :]
        path = urlunquote(path)  # URLs have to be decoded
    return path.strip("/")


def _prepare_uniq(uniq_id: str) -> str:
    if not is_uniq_code(uniq_id):
        raise BQApiError(f'"{uniq_id}" is not a valid resource id')
    return id


def _prepare_uniq_or_alias_or_path(uniq_id: str) -> str:
    if uniq_id.startswith("store://"):
        uniq_id = uniq_id[len("store://") :]
        uniq_id = urlunquote(uniq_id)  # URLs have to be decoded
    return uniq_id.strip("/")


def _clean_doc(doc: Metadoc | str) -> Metadoc | str:
    if isinstance(doc, str) and ("uri" in doc or "_id" in doc):
        # doc has ids => strip them off
        try:
            doc = Metadoc.from_naturalxml(doc)
        except InvalidFormat:
            try:
                doc = Metadoc.from_json(doc)
            except InvalidFormat:
                pass
    if isinstance(doc, Metadoc):
        doc = doc.clean()
    return doc


####################################
## Admin


class AdminProxy(FuturizedServiceProxy):
    """
    AdminProxy is the client-side proxy for admin service, or "admin".
    This service encompasses all administrative tasks, e.g. creating user accounts and logging in/out.

    Example:
        >>> admin = vqsession.service("admin")
    """

    service_name = "admin"

    def login_as(self, login_id: str, create: bool = False, logout: bool = True) -> "VQSession":  # noqa: F821
        """
        Create a new session for the user.

        Args:
            login_id: user_id or uniq of new user
            create: if True, create user if it does not exist

        Returns:
            a logged in VQSession
        """
        log.info("login_as %s", login_id)

        user_session = self.session.copy()
        admin = user_session.service("admin")
        params = {"create": str(create).lower(), "logout": str(logout).lower()}
        resp = admin.post(f"user/{login_id}/login", params=params)
        code_to_exception(resp)
        # For some reason our host admin cookie is kept but with an empty domain
        # This line removes it.
        user_session.c.cookies.clear(name="mex_session", domain="", path="/")
        user_session._load_services()  # Session copy leave services intact .. so we force refresh

        return user_session

    def login_create(self, login_id: str, logout=True) -> "VQSession":  # noqa: F821
        """
        Login as LOGIN_ID, create user if not already created.

        Args:
            login_id: should be a valid login id (email)

        Returns:
            a logged in VQSession
        """
        log.info("login_create %s", login_id)
        return self.login_as(login_id=login_id, create=True, logout=logout)

    def create_user(self, login_id: str, password: str, display_name: str = None) -> Metadoc:
        """
        Create a new user.

        Args:
            login_id: valid login id (email)
            password: login password
            display_name: user name shown on website

        Returns:
            user metadata doc
        """
        log.info("create %s", login_id)
        resp = self.post(
            "user", json={"user": {"password": password, "email": login_id, "display_name": display_name or login_id}}
        )
        code_to_exception(resp)
        return resp.doc()

    def fetch_user(self, login_id: str, view: str = "short") -> Metadoc:
        """
        Get user information.

        Args:
            login_id: valid login id (email)
            view: amount of detail to return ("short", "full", "deep")

        Returns:
            user metadata doc
        """
        resp = self.get(f"user/{login_id}", params={"view": view})
        code_to_exception(resp)
        return resp.doc()

    def delete_user(self, login_id: str):
        """
        Delete a user and all resources they own.

        Args:
            login_id: valid login id (email)
        """
        log.info("delete %s", login_id)
        resp = self.delete(f"user/{login_id}")
        code_to_exception(resp)
        return resp.doc()

    def modify_user(
        self, login_id: str, email: str = None, display_name: str = None, passwd: str = None, **kw
    ) -> Metadoc:
        """
        Change user information.

        Args:
            login_id: valid login id (email)
            email: new email
            display_name: new display name
            passwd: new password

        Returns:
            user metadata doc
        """
        user = Metadoc(tag="user")
        if email:
            user.add_tag("email", value=email)
        if display_name:
            user.add_tag("display_name", value=display_name)
        if passwd:
            user.add_tag("password", value=passwd)
        for k, v in kw.items():
            user.add_tag(k, value=v)
        resp = self.put(f"user/{login_id}", data=user)
        code_to_exception(resp)
        return resp.doc()

    def delete_user_resource(self, login_id: str):
        """
        Delete a user's resources (but keep user account).

        Args:
            login_id: valid login id (email)
        """
        resp = self.delete(f"user/{login_id}/image")
        code_to_exception(resp)
        return resp.doc()

    def sessions(self) -> Metadoc:
        """
        Get active sessions.

        Returns:
            doc with multiple children, one per session
        """
        resp = self.get("sessions")
        code_to_exception(resp)
        return resp.doc()

    def sessions_delete(self):
        """
        Delete all sessions.
        """
        resp = self.delete("sessions")
        code_to_exception(resp)
        return resp.doc()


####################################
## Auth


class AuthProxy(FuturizedServiceProxy):
    service_name = "auths"

    def login_providers(self, **kw):
        return self.get("login_providers", **kw)

    def credentials(self, **kw):
        return self.get("credentials", **kw)

    def get_session(self, **kw) -> dict:  # hides session
        """Return the users current session or empty dict"""
        return self._fetch_session()

    def get(self, path=None, params=None, render=None, **kw):
        res = super().get(path=path, params=params, render=render, **kw)
        return self._render_response(res, render)

    def login(self, user, pwd) -> dict:
        """Login as user
           will logout of any current session managed

        Returns:
           if successful
             a valid session with user, groups, expires, length  timeout, and the version of the server
           else
            and empty dict
        """
        self.logout()
        try:
            self.session.c.authenticate_basic(user, pwd)
            sess = self._fetch_session()
            if "user" in sess:
                return sess
            return {}
        finally:
            # Kill basic auth before leaving
            self.session.c.auth = None

    def logout(self):
        # let the server know we are done
        # resp = self.get("logout_handler")
        if self.session.c.cookies:
            try:
                self.get("logout_handler", timeout=30, allow_redirects=False)
            except BQApiError:
                log.warning("Server did not responde to logout")
            self.session.clear()

    def _fetch_session(self) -> dict:
        """Used to check that session is actuall active
        returns:
           user and group info
           { user: user-uniq, groups:
        """
        try:
            sess = self.get("session", render="doc")  # self.fetchxml (self.service_url("auth_service", 'session'))
            sess = sess.to_json()["session"]
            return sess
        except BQApiError:
            log.warning("session was not fetched from server")
            return {}

    def valid_user(self):
        """check if we have a valid user"""
        sess = self._fetch_session()
        if "user" in sess:
            return True
        return False


####################################
## Blobs
class BlobProxy(FuturizedServiceProxy):
    """
    BlobProxy is the client-side proxy for blob service, or "blobs".
    This service encompasses operations for creating, deleting and accessing binary files (e.g., raw image bytes).

    Example:
        >>> blobs = vqsession.service("blobs")
    """

    service_name = "blobs"

    def create_blob(self, path: str, blob: object):
        """Create binary resource at given path from the given object/file.

        Args:
            path: mountpath for new blob
            blob: object to store (if str, is assumed to be local filename)

        Raises:
            DuplicateFile: path already exists
            ResourceNotFoundError: path not valid
            IllegalOperation: blob creation not allowed at given path
            BQApiError: any other error

        Examples:
            >>> blob_service = vqsession.service("blobs")
            >>> blob_service.create_blob("store://mymount/my/path/name.jpg", "/tmp/image.jpg")
        """
        # prep inputs
        log.info("create %s", path)
        path = _prepare_mountpath(path)
        if isinstance(blob, io.IOBase) or (hasattr(blob, "read") and callable(blob.read)):
            # file like
            filedata = blob
        elif isinstance(blob, str) and os.path.exists(blob):
            # file path str
            filedata = open(blob, "rb")
        elif (
            isinstance(blob, dict | set | list | tuple | int | float | str)
            or (hasattr(blob, "to_csv") and callable(blob.to_csv))
            or (hasattr(blob, "dtype") and hasattr(blob, "shape") and callable(blob.dtype) and callable(blob.shape))
        ):
            # basic type or pandas dataframe or numpy array
            filedata = pickle.dumps(blob)
        else:
            raise BQApiError(
                "Unable to determine type of %s: must be basic type, numpy array, dataframe, or file", blob
            )

        try:
            res = self.post(urlquote(path), headers={"Content-Type": "application/octet-stream"}, data=filedata)

            # prep outputs
            code_to_exception(res)

        finally:
            if hasattr(filedata, "close"):
                filedata.close()

    def delete_blob(self, path: str):
        """Delete binary resource at given path.

        Args:
            path: mountpath for blob to delete

        Raises:
            ResourceNotFoundError: path not valid
            IllegalOperation: blob deletion not allowed (e.g., resource is registered or path is container)
            BQApiError: any other error

        Examples:
            >>> blob_service = vqsession.service("blobs")
            >>> blob_service.delete_blob("store://mymount/my/path/name.jpg")
        """
        # prep inputs
        log.info("delete %s", path)
        path = _prepare_mountpath(path)

        res = self.delete(urlquote(path))

        # prep outputs
        code_to_exception(res)

    def register(self, path: str = None, resource: Metadoc = None) -> Metadoc:
        """Register blob at a given mount path.

        Args:
            path: mountpath to blob
            resource: assign suggested type, permissions and metadata at registration time

        Returns:
            resource document

        Raises:
            AlreadyRegisteredError: blob already registered
            ResourceNotFoundError: path not valid
            IllegalOperation: blob registration not allowed at given path
            BQApiError: any other error

        Examples:
            >>> blob_service = vqsession.service("blobs")
            >>> blob_service.register(path="store://mymount/my/path/name.jpg")
            <Metadoc at 0x...>
        """
        # prep inputs
        log.info("register %s", path)
        path = _prepare_mountpath(path)

        res = self.post(posixpath.join("register", urlquote(path)), data=resource)

        # prep outputs
        code_to_exception(res)

        return res.doc()

    def unregister(self, path: str = None, resource: Metadoc = None) -> bool:
        """Unregister blob with given id.

        Args:
            path: mount-path of blob
            resource: resource to unregister

        Returns:
            True, if successfully unregistered

        Raises:
            ResourceNotFoundError: invalid mount-path or id
            NotRegisteredError: blob not registered

        Examples:
            >>> blob_service = vqsession.service("blobs")
            >>> blob_service.unregister(path="store://mymount/my/path/name.jpg")
            True
        """
        # prep inputs
        log.info("unregister %s", path)
        if path is None and resource is not None:
            path = resource.text.split(",", 1)[0]
        path = _prepare_mountpath(path)

        res = self.delete(posixpath.join("register", urlquote(path)))

        # prep outputs
        code_to_exception(res)

        return True

    def read_chunk(
        self,
        blob_id: str,
        content_selector: str = None,
        vts: str = None,
        as_stream: bool = False,
    ) -> ResponseFile | ResponseFolder | bytes:
        """Read chunk of resource specified by id.

        Args:
            blob_id: mount-path or uuid or alias of blob
            content_selector: blob-specific selector of subset to return (or all if None)
            vts: version timestamp to return (or latest if None)
            as_stream: return chunk as bytes stream (ResponseFile/ResponseFolder), otherwise return as localpath

        Returns:
            file obj or folder obj or blob byte array

        Raises:
            NoAuthorizationError: no access permission for blob
            ResourceNotFoundError: no blob with given id
            BQApiError: any other error

        Examples:
            >>> blob_service = vqsession.service("blobs")
            >>> with blob_service.read_chunk('00-123456789', as_stream=True) as fp:
            >>>    fo.read(1024)
        """
        # prep inputs
        blob_id = _prepare_uniq_or_alias_or_path(blob_id)

        headers = {}
        if content_selector is not None:
            headers["x-content-selector"] = content_selector
        if vts is not None:
            headers["x-vts"] = vts

        # count = 0
        # while True:
        #     #
        #     res = self.get(f"/{urlquote(blob_id)}", headers=headers, stream=as_stream)
        #     if res.status_code != http_code_blob_not_ready:
        #         break
        #     max_retries = res.headers.get("x-viqi-max-retries", 0)
        #     if max_retries > 0 and count > max_retries:
        #         break
        #     time.sleep(1)
        #     count += 1
        res = self.get(f"/{urlquote(blob_id)}", headers=headers, stream=as_stream)

        # prep outputs
        code_to_exception(res)

        if res.headers["content-type"] == "application/x-tar":
            # this is a tarfile of a folder structure
            res = ResponseFolder(res)
        else:
            # this is a single file
            res = ResponseFile(res)

        if as_stream:
            return res

        # caller wants local copy... this may be never used/needed...
        try:
            localpath = tempfile.mkdtemp()  # who deletes this?
            return res.copy_into(localpath, full_path=False)
        finally:
            res.close()


####################################
## Datasets
class DatasetProxy(FuturizedServiceProxy):
    """
    DatasetProxy is the client-side proxy for dataset service, or "datasets".
    This service encompasses operations for creating, deleting and modifying datasets.

    Example:
        >>> datasets = vqsession.service("datasets")
    """

    service_name = "datasets"

    def create(self, dataset_name, member_list, **kw):
        """Create a dataset from a list of resource_uniq elements"""
        data = self.session.service("data_service")
        dataset = Metadoc(tag="dataset", name=dataset_name)
        for member_uniq in member_list:
            member = dataset.add_tag("value", type="object")
            member.text = member_uniq

        return data.post(data=dataset, render="doc")

    def append_member(self, dataset_uniq, resource_uniq, **kw):
        """Append an objects to dataset
        Args:
           resource_uniq: str or list
        """
        data = self.session.service("data_service")
        patch = Metadoc(tag="patch")
        if isinstance(resource_uniq, str):
            resource_uniq = [resource_uniq]
        for uniq in resource_uniq:
            member = Metadoc(tag="value", type="object", value=uniq)
            patch.add_tag(tag="add", sel=f"/{dataset_uniq}").add_child(member)
        data.patch(data=patch)

    def delete(self, dataset_uniq, members=False, **kw):
        data = self.session.service("data_service")
        if not members:
            data.delete(path=f"{dataset_uniq}")
            return
        dataset = data.fetch(docid=f"/{dataset_uniq}", view="deep")
        patch = Metadoc(tag="patch")
        for uniq in list(members):
            uris = dataset.path_query(f"value[@value='{uniq}']/@uri")
            for uri in uris:
                patch.add_tag(tag="remove", sel="/{uri}")
        data.patch(data=patch)

    def delete_member(self, dataset_uniq, resource_uniq, **kw):
        """Delete a member..
        @return new dataset if success or None
        """
        raise NotImplementedError
        # data = self.session.service("data_service")
        # dataset = data.fetch(dataset_uniq, params={"view": "full"}, render="doc")
        # members = dataset.path_query('value[text()="%s"]' % data.construct(resource_uniq))
        # for member in members:
        #     member.delete()
        # if len(members):
        #     return data.put(dataset_uniq, data=dataset, render="doc")
        # return None


####################################
## Mex
class MexProxy(FuturizedServiceProxy):
    """
    MexProxy is the client-side proxy for mex service, or "mexes".
    This service encompasses operations for starting and stopping module runs, and for getting run logs.

    Example:
        >>> mexes = vqsession.service("mexes")
    """

    service_name = "mexes"

    def get_all_mexes(self) -> Metadoc:
        """Get module execution (mex) documents for all running modules.

        Returns:
            mex document

        Raises:
            BQApiError: any other error

        Examples:
            >>> mex_service = vqsession.service("mexes")
            >>> mex_service.get_all_mexes()
            <Metadoc at 0x...>
        """
        res = self.get("")

        # prep outputs
        code_to_exception(res)

        return res.doc()

    def get_mex(self, mex_id: str) -> Metadoc:
        """Get module execution (mex) document for the execution specified.

        Args:
            mex_id: mex UUID

        Returns:
            mex document

        Raises:
            MexNotFoundError: if no mex with given id was found
            BQApiError: any other error

        Examples:
            >>> mex_service = vqsession.service("mexes")
            >>> mex_service.get_mex("00-123456789")
            <Metadoc at 0x...>
        """
        # prep inputs
        mex_id = _prepare_uniq(mex_id)

        res = self.get(f"/{mex_id}")

        # prep outputs
        code_to_exception(res)

        return res.doc()

    def get_mex_log(self, mex_id: str) -> Metadoc:
        """Get module execution (mex) log for the execution specified.

        Args:
            mex_id: mex UUID

        Returns:
            <log>logtext</log>

        Raises:
            MexNotFoundError: if no mex with given id was found

        Examples:
            >>> mex_service = vqsession.service("mexes")
            >>> mex_service.get_mex_log("00-123456789")
            2021-07-02 03:00:56,848 DEBUG [urllib3.connectionpool] (_new_conn) - Starting ne...
        """
        # prep inputs
        mex_id = _prepare_uniq(mex_id)

        res = self.get(f"/{mex_id}/log")

        # prep outputs
        code_to_exception(res)

        return res.doc()

    def request(self, path=None, params=None, method="get", render=None, **kw):
        # TODO: add real api fct
        res = super().request(path=path, params=params, method=method, render=render, **kw)
        return self._render_response(res, render)


####################################
## Expoert


class ExportProxy(FuturizedServiceProxy):
    ## service_name = "export"  # NOT Implemented

    valid_param = {"files", "datasets", "dirs", "urls", "users", "compression"}

    def fetch_export(self, **kw):
        params = {key: val for key, val in list(kw.items()) if key in self.valid_param and val is not None}
        response = self.fetch("stream", params=params, stream=kw.pop("stream", True))
        return response

    def fetch_export_local(self, localpath, stream=True, **kw):
        response = self.fetch_export(stream=stream, **kw)
        if response.status_code == requests.codes.ok:
            with open(localpath, "wb") as f:
                shutil.copyfileobj(response.raw, f)
        return response


####################################
## Meta/Data


class DataProxy(FuturizedServiceProxy):
    """
    DataProxy is the client-side proxy for data service, or "meta".
    This service encompasses operations for creating, deleting and modifying metadata documents, and for querying them.

    Example:
        >>> meta = vqsession.service("meta")
    """

    service_name = "meta"

    # TODO: add real API fcts
    def request(self, path=None, params=None, method="get", render="doc", view=None, **kw):
        if view is not None:
            if isinstance(view, list):
                view = ",".join(view)
            params = params or {}
            params["view"] = view

        res = super().request(path=path, params=params, method=method, render=render, **kw)

        # prep outputs
        code_to_exception(res)
        return self._render_response(res, render)

    def fetch(self, path=None, params=None, render="doc", **kw):
        return super().fetch(path=path, params=params, render=render, **kw)

    def get(self, path=None, params=None, render="doc", **kw):
        return super().get(path=path, params=params, render=render, **kw)

    def patch(self, path=None, params=None, render="doc", **kw):
        return super().patch(path=path, params=params, render=render, **kw)

    def post(self, path=None, params=None, render="doc", **kw):
        # POST expects clean doc (without URIs/IDs), so clean it before posting
        data = kw.get("data")
        if data:
            kw["data"] = _clean_doc(data)
        return super().post(path=path, params=params, render=render, **kw)

    def put(self, path=None, params=None, render="doc", **kw):
        return super().put(path=path, params=params, render=render, **kw)

    def delete(self, path=None, params=None, render=None, **kw):
        return super().delete(path=path, params=params, render=render, **kw)

    def set_attr(self, path, attribute, value):
        """Set an attribute on the resource (name, atime, etc)"""
        doc = Metadoc(tag="resource")
        doc.attrib[attribute] = str(value)
        res = self.put(path, data=doc, params={"attr_only": "true"})
        return res


####################################
## Dirs
class DirProxy(FuturizedServiceProxy):
    """
    DirProxy is the client-side proxy for data service, or "dirs".
    This service encompasses operations for creating and deleting containers/directories, listing directories,
    and searching in directories.

    Example:
        >>> dirs = vqsession.service("dirs")
    """

    service_name = "dirs"

    def create_container(self, path: str, name: str, container_type: str = "folder"):
        """Create new container with name at given path.

        Args:
            path: mountpath holding new container
            name: name of new container
            container_type: type of container to create (e.g., 'folder', 'zip', 'tablecontainer')

        Raises:
            NoSuchFileError: file at mount-path does not exist
            NoSuchPathError: mount-path does not exist

        Examples:
            >>> dir_service = vqsession.service("dirs")
            >>> dir_service.create_container("/mymount/my/path", "new_container", container_type="tablecontainer")
        """
        # prep inputs
        path = _prepare_mountpath(path)
        if name is None:
            name = os.path.basename(path)

        res = self.post(
            urlquote(path),
            data=Metadoc.from_naturalxml(f'<dir name="{name}" type="{container_type}" />'),
        )

        # prep outputs
        code_to_exception(res)

    def delete_path(self, path: str, force: bool = False):
        """Delete container at given path.

        Args:
            path: mount-path to delete
            force: if True, delete even if there are associated resources (which will leave resources without binaries);
                   to delete resources with binaries, use meta.delete

        Raises:
            NoSuchFileError: file at mount-path does not exist
            NoSuchPathError: mount-path does not exist
            IllegalOperation: attempt to delete root container

        Examples:
            >>> dir_service = vqsession.service("dirs")
            >>> dir_service.delete_container("/mymount/dir1/dir2")
        """
        # prep inputs
        path = _prepare_mountpath(path)

        res = self.delete(urlquote(path), params={"force": force})

        # prep outputs
        code_to_exception(res)

    # deprecated
    delete_container = delete_path

    def list_files(
        self,
        path: str,
        namespaces: Collection[str] | None = None,
        want_types: bool = False,
        patterns: list[str] = None,
        limit: int = 100,
        offset: int = 0,
        view=None,
        sort_order: list[tuple] = None,
    ) -> Metadoc:
        """List all entries (registered and unregistered, resources and containers) at the given path.

        Args:
            path: mount-path to list
            namespaces: namespaces for which to return metadata (e.g., ("details", "filesystem", "lustre", "resource_meta"))
            want_types: if True, include type guesses per entry (slow!)
            patterns: one or more wildcard patterns for filtering of entries (these are ORed)
            limit: max number of entries to return
            offset: starting entry number (for paging)
            sort_order: sorting order for entries (e.g., [('created', 'asc'), ('name', 'desc')])

        Returns:
            doc describing path and all selected entries as children

        Raises:
            NoSuchFileError: file at mount-path does not exist
            NoSuchPathError: mount-path does not exist
            IllegalOperation: mount does not exist

        Examples:
            >>> dir_service = vqsession.service("dirs")
            >>> str(dir_service.list_files("/mymount/dir1", limit=10))
            '<dir name="mymount" ...> <dir ... /> ... <image ... /> <resource ... /> </dir>'
        """
        # prep inputs
        params = {}
        if isinstance(view, str):
            view = view.split(",")
        if want_types:
            view.append("types")
        if view:
            params["view"] = ",".join(view)
        if patterns:
            params["patterns"] = ",".join(patterns)
        if sort_order:
            params["tag_order"] = ",".join(f"@{attr_name}:{attr_order}" for (attr_name, attr_order) in sort_order)
        if namespaces is not None:
            params["namespaces"] = ",".join(namespaces)
        params["limit"] = limit
        params["offset"] = offset

        res = self.get(urlquote(path), params=params)

        # prep outputs
        code_to_exception(res)

        return res.doc()

    def exists(self, path, **kw):
        """check if path exists"""
        try:
            res = self.request(urlquote(path), method="HEAD")
            if res.status_code == 200:
                return True
        except (ResourceNotFoundError, NoSuchPathError):
            pass
        return False

    def touch(self, path, __xattrs=None, **kw):
        """Set xattrs on path.
        DO NOT USE UNLESS YOU KNOW WHAT YOU ARE DOING!

        Args:
            path: mount-path to touch
            __xattrs: attributes to set (e.g., {"expanded": False})

        Raises:
            NoSuchFileError: file at mount-path does not exist
            NoSuchPathError: mount-path does not exist
            IllegalOperation: mount does not exist
        """
        # prep inputs
        xattrs = __xattrs or {}
        xattrs.update(kw)

        res = self.put(urlquote(path), params={key: str(val) for key, val in xattrs.items()})

        # prep outputs
        code_to_exception(res)

        return res

    def refresh(self, path, recursive: bool = False):
        """Force a refresh on path and all descendents.
        DO NOT USE UNLESS YOU KNOW WHAT YOU ARE DOING!

        Args:
            path: mount-path to refresh
            recursive: if True, also refresh all descendents

        Raises:
            NoSuchPathError: mount-path does not exist
            IllegalOperation: mount does not exist
        """
        # prep inputs
        path = _prepare_mountpath(path)

        if recursive:
            view = "deep,count"
        else:
            view = "count"

        res = self.get(urlquote(path), params={"refresh": "true", "view": view})

        # prep outputs
        code_to_exception(res)

        return res

    def info(self, path, **kw):
        """Return the info for the path
        Args:
            namespaces: list of namespaces fetched  (e.g., ("details", "filesystem", "lustre", "resource_meta"))
        """
        # prep inputs
        path = _prepare_mountpath(path)
        kw["children"] = "false"

        res = self.get(urlquote(path), params=kw)

        # prep outputs
        code_to_exception(res)

        return res.doc()

    def isdir(self, path):
        "Check if path is directory"
        return self.info(path).tag == "dir"

    def isfile(self, path):
        "Check if path is file"
        return self.info(path).tag == "file"

    def walk(self, path):
        """Return a generato similar to os.walk
        Returns:
          generator yielding  (root : str, [ dir entries:metadoc], [ file entries:metadoc ] )

        """
        try:
            entries = self.list_files(path)
        except OSError:
            # Handle cases where the directory might not be accessible
            return

        dirs = []
        files = []

        # Separate directories and files
        for entry in entries:
            if entry.tag == "dir":
                dirs.append(entry)
            else:
                files.append(entry)

                # Yield the current directory's information
        yield path, dirs, files

        # Recursively call custom_os_walk for each subdirectory
        for d in dirs:
            yield from self.walk(d.get("path"))


####################################
## Mounts
class MountsProxy(FuturizedServiceProxy):
    service_name = "mounts"


####################################
## Builds
class BuildsProxy(FuturizedServiceProxy):
    service_name = "builds"


####################################
## Future
class FutureProxy(FuturizedServiceProxy):
    """
    FutureProxy is the client-side proxy for future service, or "futures".
    This service encompasses operations for getting the state and result of futures.

    Example:
        >>> futures = vqsession.service("futures")
    """

    service_name = "futures"

    def get_state(self, future_id: str) -> str:
        """Get state of the future with the given id.

        Args:
            future_id: future UUID

        Returns:
            state of future (e.g., PENDING or FINISHED)

        Raises:
            FutureNotFoundError: if no future with given id was found
            BQApiError: any other error

        Examples:
            >>> future_service = vqsession.service("futures")
            >>> future_service.get_state("8196770f-ea2e-4bc6-b569-9e29fc031d46")
            'PENDING'
        """
        res = self.get(f"/{future_id}")

        # prep outputs
        code_to_exception(res)

        return res.doc().get("state")

    def get_result(self, future_id: str) -> Metadoc | requests.Response:
        """Get result of the future with the given id.

        Args:
            future_id: future UUID

        Returns:
            result of the future doc or a response if not a doc

        Raises:
            ValueError: result can not be rendered as doc
            FutureNotFoundError: if no future with given id was found
            FutureNotReadyError: if future result is not ready yet
            BQApiError: any other error
            Exception: any exception raised by the async task

        Examples:
            >>> future_service = vqsession.service("futures")
            >>> future_service.get_result("8196770f-ea2e-4bc6-b569-9e29fc031d46")
            <Metadoc at 0x...>
        """
        res = self.get(f"/{future_id}/result")

        # prep outputs
        code_to_exception(res)

        try:
            return res.doc()
        except RenderError:
            # Just return the response object
            return res

    def delete(self, future_id: str):
        """Delete future with the given id.

        Args:
            future_id: future UUID

        Raises:
            FutureNotFoundError: if no future with given id was found
            BQApiError: any other error

        Examples:
            >>> future_service = vqsession.service("futures")
            >>> future_service.delete("8196770f-ea2e-4bc6-b569-9e29fc031d46")
        """
        res = super().delete(f"/{future_id}")

        # prep outputs
        code_to_exception(res)

    def create_future(self, cmd: str, max_retries=None, retry_after=None, **kw) -> Metadoc:
        """create a future cmd(sleep, access_session) setting future options for testing

        Args:
          cmd : a python like call for supported tasks
                sleep(amount=10)
                access_session()
          max_retries: future's max_retries
          retry_after : future retry after
          **kw : options to be passesd to the future (queue, countdouwn, timeout, etc)
        """
        params = {"cmd": cmd, **kw}
        if max_retries is not None:
            params["max_retries"] = int(max_retries)
        if retry_after is not None:
            params["retry_after"] = int(retry_after)

        res = super().post("/", params=params)
        code_to_exception(res)
        return res.doc()


####################################
## Services


class ServicesProxy(BaseServiceProxy):
    service_name = "services"


####################################
## Preferences


class PreferenceProxy(BaseServiceProxy):
    service_name = "preference"

    def get_value(self, key):
        res = self.get(key)
        code_to_exception(res)
        return res.doc()


####################################
## Notify
class NotifyProxy(BaseServiceProxy):
    service_name = "notify"

    def send_email(
        self,
        recipients: str | list[str],
        subject: str,
        body: str,
        attachments: list[str] = None,
        sender=None,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        reply_to: str | None = None,
    ):
        """Send an email from viqi1.

        Args:
           recipients: list of emails
           subject:   subject of email
           body:       text  of email
           attachments:  list of viqi paths files to attach (must be on server)
           sender: overide the default sender (must be an email address  allowed by the system)
           cc: list of cc emails
           bcc: list of bcc emails
           reply_to: reply_to email

        Returns:
           a metadoc <result>[ok|fail]</result>

        """
        if isinstance(recipients, list):
            recipients = ",".join(recipients)
        params = {"recipients": recipients, "subject": subject}
        if sender:
            params["sender"] = sender
        if attachments:
            params["attachments"] = ",".join(attachments)
        if cc:
            params["cc"] = ",".join(cc)
        if bcc:
            params["bcc"] = ",".join(bcc)
        if reply_to:
            params["reply_to"] = reply_to

        res = super().post(
            "email",
            params=params,
            data=body,
            headers={"Content-Type": "text/plain"},
        )
        code_to_exception(res)
        return res.doc()

    def send_message(self, channel: str, message: str, attachments: list[str] = None):
        """Send a slack message from viqi1.

        Args:
           channel:   slack channel to send to
           message:  text of message to send
           attachments:  list of viqi paths files to attach (must be on server)

        Returns:
           a metadoc <result>[ok|fail]</result>
        """
        params = {"channel": channel, "message": message}
        if attachments:
            params["attachments"] = ",".join(attachments)

        res = super().post("message", params=params, headers={"Content-Type": "text/plain"})
        code_to_exception(res)
        return res.doc()


def test_module():
    from vqapi import VQSession

    session = VQSession().init_local("admin", "admin", "http://localhost:8080")
    admin = session.service("admin")
    data = session.service("data_service")
    # admin.user(uniq).login().fetch ()
    xml = data.get("user", params={"resource_name": "admin"}, render="doc")
    user_uniq = xml.find("user").get("resource_uniq")
    admin.fetch(f"/user/{user_uniq}/login")


if __name__ == "__main__":
    test_module()
