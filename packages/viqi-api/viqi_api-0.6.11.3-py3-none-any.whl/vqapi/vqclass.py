import copy
import inspect
import json
import logging
import sys
import time
from typing import Union

from bq.metadoc.formats import RESERVED_TAGNAMES, Metadoc, anyxml_to_etree

from vqapi.comm import BQSession
from vqapi.exception import BQApiError
from vqapi.vqquery import get_provenance, run_sparql_query, run_tag_query

log = logging.getLogger("vqapi.vqclass")


def get_header(res, name):
    return res.headers.get(name, "").lstrip("W/")[
        1:-1
    ]  # remove entity tag and quotes (why is this not done by pyramid?)


def _clean_uniq(uniq: str) -> str:
    if not (uniq.startswith("00-") or uniq.startswith("/00-")) or "/" in uniq.strip("/") or "@" in uniq:
        raise BQApiError(f"malformed resource id: {uniq}")
    return uniq.strip("/")


def _get_param_types(param, default="string"):
    param_type = param.get_attr("type", default)
    if param_type in ("resource", "document"):
        acc_types = param.path_query("./template/accepted_type")
        if len(acc_types) > 0:
            param_type = [acc_type.get_value() for acc_type in acc_types]
    if not isinstance(param_type, list):
        param_type = [param_type]
    return param_type


def _get_param_label(param):
    label = param.path_query("./template/label")
    if len(label) > 0:
        return label[0].get_value()
    else:
        return None


def _fetch_subdoc(sess: "VQSession", doc_id: str, node_id: str) -> Metadoc:
    meta = sess.service("meta")
    return meta.request(
        method="get",
        path=f"/{doc_id}@{node_id}",
        params={"view": "deep,clean"},
        render="doc",
    )


def _parse_sizeof(num: Union[int, float, str]) -> Union[int, float]:
    """
    Convert common memory sizes

    Args:
      num: a string size such as "1MB", "4kb", "3.2tb"

    Returns:
     an integer in bytes
    """
    # dicts are ordered so insert longest to shortest order for match
    units = {
        "kb": 1024,
        "mb": 1024**2,
        "gb": 1024**3,
        "tb": 1024**4,
        "pb": 1024**5,
        "b": 1,
    }
    if isinstance(num, str):
        for sz, mult in units.items():
            if num.lower().endswith(sz):
                return int(float(num[: -len(sz)]) * mult)
    try:
        return int(num)
    except ValueError:
        return float(num)


def _match_op(expr, value):
    if "*" in value:
        return f'{expr} ~ "{value}"'
    else:
        return f'{expr} = "{value}"'


def _nmatch_op(expr, value):
    if "*" in value:
        return f'NOT ({expr} ~ "{value}")'
    else:
        return f'{expr} != "{value}"'


def copy_as_not_impl(other_class):
    """
    Decorator that adds a method returning "Not Implemented" for each method in other_class
    that has not been defined in this class.
    """

    def wrapper(cls):
        def _notimpl(*args, **kwargs):
            raise NotImplementedError()

        for func in other_class.__dict__:
            if callable(getattr(other_class, func)) and func not in cls.__dict__:
                setattr(cls, func, _notimpl)
        return cls

    return wrapper


class VQCollection:
    """
    Collection of resources (typically result of a query).
    """

    def __init__(self, sess, from_query=None, from_tags=None):
        self._sess = sess
        self._from_query = (
            [from_query[0], from_query[1], "", from_query[2] if len(from_query) > 2 else {}]
            if from_query is not None
            else None
        )  # from_query = (sparql WHERE str, doc var)
        self._from_tags = (
            list(from_tags) if from_tags is not None else None
        )  # from_tags = ("resource type", {'tag_query':'...', 'tag_order':'...'})
        self.match_iter = None

    def order_by(self, order: list[tuple]) -> "VQCollection":
        """
        Order collection by one or more attributes.

        Params:
            order: list of (attribute name, ordering) tuples

        Returns:
            ordered collection

        Examples:
            >>> res = sess.select_from_tags("image", tag_query="plate:1234 AND @ts:>=2023-01-01").order_by(
            ...     [("@ts", "asc"), ("@name", "desc")]
            ... )
        """
        if self._from_query is not None:
            self._from_query[2] = "ORDER BY " + " ".join(
                [f"{attrorder}(?{self._from_query[1]}/{attrname})" for attrname, attrorder in order]
            )
        else:
            self._from_tags[1]["tag_order"] = ",".join([f"{attrname}:{attrorder}" for attrname, attrorder in order])
        return self

    def limit(self, limit: int) -> "VQCollection":
        """
        Only keep the first <limit> elements of the collection.

        Params:
            limit: number of elements to keep

        Returns:
            collection with only first <limit> elements

        Examples:
            >>> res = sess.select_from_tags("image", tag_query="plate:1234 AND @ts:>=2023-01-01").limit(10)
        """
        if self._from_query is not None:
            if limit is None:
                self._from_query[3].pop("limit", None)
            else:
                self._from_query[3]["limit"] = str(limit)
        else:
            if limit is None:
                self._from_tags[1].pop("limit", None)
            else:
                self._from_tags[1]["limit"] = str(limit)
        return self

    def offset(self, offset: int) -> "VQCollection":
        """
        Skip everything before <offset> in collection.

        Params:
            offset: offset of first element to keep

        Returns:
            collection without elements before <offset>

        Examples:
            >>> res = sess.select_from_tags("image", tag_query="plate:1234 AND @ts:>=2023-01-01").offset(10).limit(10)
        """
        if self._from_query is not None:
            self._from_query[3]["offset"] = str(offset)
        else:
            self._from_tags[1]["offset"] = str(offset)
        return self

    def __len__(self) -> int:
        """
        Get number of resources in collection.

        Returns:
            number of resources
        """
        if self._from_query is not None:
            query, doc_var, order_clause, kwargs = self._from_query
            matches = run_sparql_query(
                self._sess,
                f"SELECT COUNT(?{doc_var}/@resource_uniq) AS cnt WHERE {{ {query} }} {order_clause}",
                **kwargs,
            )
            try:
                return int(matches[0]["cnt"])
            except TypeError:
                return int(matches[0]["cnt"]["@value"])
        if self._from_tags is not None:
            rtype, kwargs = self._from_tags
            kwargs["view"] = "count"
            matches = run_tag_query(self._sess, rtype, **kwargs)
            return int(matches.path_query("/result/count/@value")[0])

    def __iter__(self):
        """
        Get iterator for this collection.

        Returns:
            iterator
        """
        return self

    def __next__(self):
        """
        Iterate over resources in collection.

        Returns:
            next item in collection
        """
        if self.match_iter is None:
            if self._from_query is not None:
                query, doc_var, order_clause, kwargs = self._from_query
                self.match_iter = iter(
                    run_sparql_query(
                        self._sess,
                        f"SELECT ?{doc_var}/@resource_uniq AS docid WHERE {{ {query} }} {order_clause}",
                        **kwargs,
                    )
                )
            if self._from_tags is not None:
                rtype, kwargs = self._from_tags
                kwargs["view"] = "short"
                self.match_iter = iter(run_tag_query(self._sess, rtype, **kwargs))

        try:
            if self._from_query is not None:
                return self._sess.load(next(self.match_iter)["docid"])
            if self._from_tags is not None:
                return self._sess.load(next(self.match_iter).get_docid())
        except StopIteration:
            raise StopIteration

    def delete(self):
        """
        Delete all resources in collection in a transaction.

        Raises:
            BQApiError: deletion failed
        """
        patchdoc = Metadoc(tag="patch")
        if self._from_query is not None:
            # TODO: should use update query here
            query, doc_var, order_clause, kwargs = self._from_query
            for match in run_sparql_query(
                self._sess, f"SELECT ?{doc_var}/@resource_uniq AS docid WHERE {{ {query} }} {order_clause}", **kwargs
            ):
                patchdoc.add_tag("remove", sel=f"/{match['docid']}")
        if self._from_tags is not None:
            rtype, kwargs = self._from_tags
            kwargs["view"] = "short"
            for match in run_tag_query(self._sess, rtype, **kwargs):
                patchdoc.add_tag("remove", sel=f"/{match.get_docid()}")
        meta = self._sess.service("meta")
        res = meta.request(method="patch", path="/", data=patchdoc, render=None)
        if res.status_code != 200:
            raise BQApiError(f"collection could not be deleted: {res.text}")


@copy_as_not_impl(Metadoc)
class VQResource:
    """
    Class to store any ViQi-backed resource doc;
    same interface as :external:py:class:`~bq.metadoc.formats.Metadoc` but has extra functions depending on resource type.
    """

    def __init__(self, sess, doc_uniq=None, doc_version=None, **attrs):
        # next five lines have to be first to enable refresh
        self._doc_uniq = _clean_uniq(doc_uniq)
        self._doc_version = doc_version
        self._doc_lvls = 0
        self._sess = sess
        self._meta = sess.service("meta")
        # additional inits (may trigger refresh)
        tag = self.resource_type
        self._doc = Metadoc(tag=tag, **attrs)

    @staticmethod
    def load(sess: "VQSession", uniq: str) -> "VQResource":
        """
        Load a resource from resource UUID.
        (Same as calling `sess.load(uniq)`.)

        Args:
            sess: active session
            uniq: resource UUID

        Returns:
            loaded resource
        """
        return sess.load(uniq)

    @classmethod
    def find(cls, sess: "VQSession", **kwargs) -> "VQResource":
        raise NotImplementedError(f"find operation not implemented for resource type {cls.resource_type}")

    def _refresh(self, lvls: int):
        view = "short" if lvls == 1 else ("full" if lvls == 2 else "deep")
        if self._doc_uniq is not None:
            if lvls <= self._doc_lvls:
                headers = {"If-None-Match": self._doc_version}  # fetch only if newer version available
            else:
                headers = {}  # fetch always, need more levels
            res = self._meta.request(
                method="get",
                path="/" + self._doc_uniq,
                params={"view": view},
                headers=headers,
                render=None,
            )
            if res.status_code == 200:
                self._doc = res.doc()
                self._doc_version = get_header(res, "ETag")
                self._doc_lvls = lvls
            elif res.status_code == 304:  # not modified
                pass
            else:
                raise BQApiError(f"resource {self._doc_uniq} could not be refreshed")

    def __getattr__(self, name: str) -> str:
        if name in ("_doc_uniq", "_doc_version", "_doc", "_doc_lvls", "_sess", "_meta"):
            return self.__dict__[name]
        self._refresh(lvls=1)
        return self._doc.__getattr__(name)

    def __setattr__(self, name: str, val: str):
        if name in ("_doc_uniq", "_doc_version", "_doc", "_doc_lvls", "_sess", "_meta"):
            self.__dict__[name] = val
            return
        raise NotImplementedError(f'setting of doc attribute "{name}" not implemented')

    def get_docid(self) -> str:
        """
        Get UUID of this resource.

        Returns:
            UUID
        """
        return self._doc_uniq

    def get_value(self):
        self._refresh(lvls=1)
        return self._doc.get_value()

    def get_attr(self, attr, default=None):
        self._refresh(lvls=1)
        return self._doc.get_attr(attr, default)

    def get(self, attr, default=None):
        self._refresh(lvls=1)
        return self._doc.get(attr, default)

    def as_dict(self, strip_attributes: bool = False) -> dict:
        """
        Get resource metadata as a JSON dictionary.

        Args:
            strip_attributes: if True, removes all attributes (keys starting with "@")

        Returns:
            dict
        """
        self._refresh(lvls=sys.maxsize)  # avoid if possible
        return self._doc.as_dict(strip_attributes=strip_attributes)

    def as_xml(self) -> str:
        """
        Get resource metadata as an XML string.

        Returns:
            str
        """
        self._refresh(lvls=sys.maxsize)  # avoid if possible
        return self._doc.as_xml()

    # alias
    to_json = as_dict

    def __str__(self):
        return f"{self.resource_type}@{self._doc_uniq}"

    __repr__ = __str__

    def path_query(self, path):
        self._refresh(lvls=sys.maxsize)  # TODO: maybe run as server side query?
        return self._doc.path_query(path)

    def add_sibling(self, tag, **attrs):
        if self._doc_uniq is not None:
            raise NotImplementedError("updates to stored docs not implemented")
        return self._doc.add_sibling(tag, **attrs)

    def add_tag(self, tag, **attrs):
        if self._doc_uniq is not None:
            raise NotImplementedError("updates to stored docs not implemented")
        return self._doc.add_tag(tag, **attrs)

    def delete(self):
        if self._doc_uniq is not None:
            raise NotImplementedError("updates to stored docs not implemented")
        return self._doc.delete()

    def add_child(self, newchild):
        if self._doc_uniq is not None:
            raise NotImplementedError("updates to stored docs not implemented")
        return self._doc.add_child(newchild)

    def permissions(self) -> str:
        """
        Get permissions to this resource (e.g., "read,write")

        Returns:
            string with comma-separated permissions to this resource
        """
        user_id = self._sess.current_user().get_docid()
        res = self._meta.request(method="get", path="/" + self._doc_uniq + "/auth", render="doc")
        matches = res.path_query(f"""user[./@name = "{user_id}"]""")
        if len(matches) > 0:
            return matches[0].get_value()
        else:
            return "read" if self.get_attr("permission") == "published" else ""

    def as_bytes(self):
        """
        Read raw bytes of resource.
        Careful with large resources!

        Returns:
            bytes
        """
        blob_service = self._sess.service("blobs")
        with blob_service.read_chunk(self.get_docid(), as_stream=True) as f:
            return f.readall()

    def as_native(self):
        """
        Get resource in best native representation.

        Returns:
            object
        """
        return self.as_bytes()


class VQMex(VQResource):
    """
    Class representing a Mex (running or past module run).
    """

    resource_type = "mex"

    @classmethod
    def find(
        cls,
        sess: "VQSession",
        module_name: str,
        version: str = None,
        status: str | list[str] = None,
        not_status: str | list[str] = None,
        _input_ts_check: bool = False,
        _execute_options: dict = None,
        **kwargs,
    ) -> VQCollection:
        """
        Fetch mex doc(s) for given execute options and inputs.

        Args:
            sess: session
            module_name: name of the module
            version: version tag of build (or None to search in all versions)
            status: mex statuses to match (e.g., "FINISHED"); can use wildcard "*"
            not_status: mex statuses to NOT match (e.g., ["STOPPED", "FAILED"]); can use wildcard "*"
            _input_ts_check: if True, find only mexes with input resources older than mex
            _execute_options: execute options to match (e.g., "requested_memory", "requested_gpus")
            kwargs: input parameters to match (will be mapped to module inputs)

        Returns:
            collection of mexes that match

        Raises:
            BQApiError
        """
        _execute_options = _execute_options or {}
        extra_filters = []
        extra_patterns = []
        resources = []
        for idx, (exop, exval) in enumerate(_execute_options.items()):
            extra_patterns.append(f"?exops :/ {exop}:?exop{idx}")
            try:
                exval = _parse_sizeof(exval)
            except ValueError:
                pass
            extra_filters.append(f'?exop{idx}/@value_str = "{exval}"')
        for idx, (argname, argval) in enumerate(kwargs.items()):
            extra_patterns.append(f"?inp :// {argname}:?arg{idx}")
            if isinstance(argval, VQResource):
                # for a resource input, also check that the resource ts is older than the mex creation time
                # if the resource has changed since the mex started, the mex cannot safely be reused
                if _input_ts_check and argval.get_docid() not in resources:
                    resources.append(argval.get_docid())
                    res_id = f"res{len(resources)}"
                    extra_patterns.append(f"/{argval.resource_type}:?{res_id}")
                    extra_filters.append(f'?{res_id}/@resource_uniq = "{argval.get_docid()}"')
                    extra_filters.append(f"?{res_id}/@ts < ?mex/@created")
                argval = argval.get_docid()
            elif isinstance(argval, list):
                argval = ";".join(str(param) for param in argval)
            elif isinstance(argval, bool):
                argval = ["False", "false"] if argval is False else ["True", "true"]
            if isinstance(argval, str):
                argval = argval.replace(r'"', r"\"")
            if isinstance(argval, list):
                extra_filters.append(
                    "("
                    + " OR ".join(_match_op(f"?arg{idx}/@value_str", str(argval_single)) for argval_single in argval)
                    + ")"
                )
            else:
                extra_filters.append(_match_op(f"?arg{idx}/@value_str", str(argval)))
        if status is not None:
            if not isinstance(status, list):
                status = [status]
            statuses = [_match_op("?mex/@value_str", sstatus) for sstatus in status]
            if len(statuses) > 1:
                extra_filters.append("(" + " OR ".join(statuses) + ")")
            else:
                extra_filters.append(statuses[0])
        if not_status is not None:
            if not isinstance(not_status, list):
                not_status = [not_status]
            not_statuses = [_nmatch_op("?mex/@value_str", not_sstatus) for not_sstatus in not_status]
            extra_filters.append(" AND ".join(not_statuses))
        if version is not None:
            extra_filters.append(f'?bld/@name = "{version}"')
        extra_patterns = ". ".join(extra_patterns)
        if extra_patterns != "":
            extra_patterns = ". " + extra_patterns
        extra_filters = " AND ".join(extra_filters)
        if extra_filters != "":
            extra_filters = " AND " + extra_filters
        where = f"""
                /mex:?mex :/ build:?bldref. ?bldref :-> /build:?bld. ?bld :/ module:?modref. ?modref :-> /module:?mod.
                ?mex :/ inputs:?inp.
                ?mex :/ execute_options:?exops
                {extra_patterns}
                FILTER( ?mod/@name = "{module_name}"
                        {extra_filters} )
            """
        log.debug("query for previous mex run: %s", where)
        return VQCollection(sess, from_query=(where, "mex"))

    def wait(self):
        """
        Wait for module to finish or fail.
        """
        while self.get_value() not in ("FINISHED", "FAILED", "STOPPED"):
            time.sleep(10)

    def retry(self):
        """
        (Partially) re-run a failed module with same settings.
        For multi-runs, only failed submexes will be re-run.
        """
        mex_service = self._sess.service("mexes")
        try:
            update_doc = Metadoc(tag="patch")
            update_doc.add_tag("replace", sel="/mex/@value", value="RUNNING")
            mex_doc = mex_service.request(
                path=f"/{self.get_docid()}",
                method="patch",
                render="doc",
                data=update_doc,
            )
            if not isinstance(mex_doc, Metadoc):
                raise BQApiError(f"module could not be restarted: {mex_doc.text}")
        except Exception as exc:
            raise BQApiError(f"module could not be restarted: {str(exc)}")

    def stop(self):
        """
        Stop a module run.
        For multi-runs, this will also stop all sub-runs.
        """
        mex_service = self._sess.service("mexes")
        try:
            mex_doc = mex_service.request(
                path=f"/{self.get_docid()}",
                method="delete",
                render="doc",
            )
            if not isinstance(mex_doc, Metadoc):
                raise BQApiError(f"module could not be stopped: {mex_doc.text}")
        except Exception as exc:
            raise BQApiError(f"module could not be stopped: {str(exc)}")

    def get_build(self) -> "VQBuild":
        """
        Get build def for this mex.

        Returns:
            build doc
        """
        self._refresh(lvls=2)
        build_id = self._doc.path_query("//build")[0]
        return VQBuild.load(self._sess, build_id.get_value())

    def get_input(self, input_name: str) -> object:
        """
        Retrieve input of module.

        Args:
            input_name: name of input

        Returns:
            input value (may be any type, including VQResource subtype)
        """
        self._refresh(lvls=sys.maxsize)
        mex_in = self._doc.path_query(f'/mex/inputs//{input_name}[not(@type) or @type != "group"]')
        if len(mex_in) == 0:
            if len(self._doc.path_query("/mex/mex")) > 0:
                raise BQApiError("this is a mex with submexes; please use get_sub_input or get_sub_inputs")
            else:
                raise BQApiError(f'input "{input_name}" not found')
        in_arg = mex_in[0]
        return self._get_io_single(
            arg_type=in_arg.get_attr("type", "doc"),
            arg_value=in_arg.get_value(),
            docid=self._doc_uniq,
            nid=in_arg.get("_id"),
        )

    def get_output(self, output_name: str) -> object:
        """
        Retrieve output of module.

        Args:
            output_name: name of output

        Returns:
            output value (may be any type, including VQResource subtype)
        """
        self.wait()
        self._refresh(lvls=sys.maxsize)
        mex_out = self._doc.path_query(f'/mex/outputs//{output_name}[not(@type) or @type != "group"]')
        if len(mex_out) == 0:
            if len(self._doc.path_query("/mex/mex")) > 0:
                raise BQApiError("this is a mex with submexes; please use get_sub_output or get_sub_outputs")
            else:
                raise BQApiError(f'output "{output_name}" not found')
        out_arg = mex_out[0]
        return self._get_io_single(
            arg_type=out_arg.get_attr("type", "doc"),
            arg_value=out_arg.get_value(),
            docid=self._doc_uniq,
            nid=out_arg.get("_id"),
        )

    def get_qc(self, qc_name: str) -> object:
        """
        Retrieve generated qc data of module.

        Args:
            qc_name: name of qc output

        Returns:
            output value (may be any type, including VQResource subtype)
        """
        self.wait()
        self._refresh(lvls=sys.maxsize)
        mex_out = self._doc.path_query(f'/mex/qc//{qc_name}[not(@type) or @type != "group"]')
        if len(mex_out) == 0:
            raise BQApiError(f'qc data "{qc_name}" not found')
        out_arg = mex_out[0]
        return self._get_io_single(
            arg_type=out_arg.get_attr("type", "doc"),
            arg_value=out_arg.get_value(),
            docid=self._doc_uniq,
            nid=out_arg.get("_id"),
        )

    def get_sub_output(self, output_name: str, **selectors) -> object:
        """
        Retrieve output in specific submex of a multimex run.

        Args:
            output_name: name of output
            selectors: one or more mex input tags/values to specify which submex

        Returns:
            output value (may be any type, including VQResource)
        """
        if len(selectors) == 0:
            raise BQApiError("need at least one selector to find output")
        self.wait()
        extra_patterns = []
        extra_filters = []
        for idx, (key, val) in enumerate(selectors.items()):
            val = val.get_docid() if isinstance(val, VQResource) else str(val)
            extra_patterns.append(f"?inputs :// tag:?tag{idx}")
            extra_filters.append(f'?tag{idx}/@name = "{key}" AND ?tag{idx}/@value_str = "{val}"')
        extra_patterns = ". ".join(extra_patterns)
        extra_filters = " AND ".join(extra_filters)
        query = f"""
            SELECT ?out/@resource_uniq AS out_docid
                   ?out/@node_id AS out_id
                   ?out/@type AS out_type
                   ?out/@value_str AS out_val
            WHERE {{
                /mex:?this :/ mex:?mexref. ?mexref :-> /mex:?submex. ?submex :/ tag:?outputs. ?outputs :/ tag:?out.
                ?submex :/ tag:?inputs. {extra_patterns}
                FILTER( ?this/@resource_uniq = "{self._doc_uniq}" AND
                        ?inputs/@name = "inputs" AND
                        ?outputs/@name = "outputs" AND
                        ?out/@name = "{output_name}" AND
                        {extra_filters} )
            }}
            """
        matches = run_sparql_query(self._sess, query)
        if len(matches) == 0:
            raise BQApiError(f'no outputs "{output_name}" with selectors found')
        if len(matches) > 1:
            raise BQApiError("selectors ambiguous")
        return self._get_io_single(
            arg_type=matches[0]["out_type"] or "doc",
            arg_value=matches[0]["out_val"] or None,
            docid=matches[0]["out_docid"],
            nid=matches[0]["out_id"],
        )

    def get_sub_outputs(self, output_name: str) -> list[object]:
        """
        Retrieve specific outputs in all submexes of a multimex run.

        Args:
            output_name: name of output

        Returns:
            list of output values (each may be any type, including VQResource)
        """
        self.wait()
        query = f"""
            SELECT ?out/@resource_uniq AS out_docid
                   ?out/@node_id AS out_id
                   ?out/@type AS out_type
                   ?out/@value_str AS out_val
            WHERE {{
                /mex:?this :/ mex:?mexref. ?mexref :-> /mex:?submex. ?submex :/ tag:?outputs. ?outputs :/ tag:?out
                FILTER( ?this/@resource_uniq = "{self._doc_uniq}" AND
                        ?outputs/@name = "outputs" AND
                        ?out/@name = "{output_name}" )
            }}
            """
        matches = run_sparql_query(self._sess, query)
        if len(matches) == 0:
            raise BQApiError(f'no outputs "{output_name}" found')
        return [
            self._get_io_single(
                arg_type=match["out_type"] or "doc",
                arg_value=match["out_val"] or None,
                docid=match["out_docid"],
                nid=match["out_id"],
            )
            for match in matches
        ]

    def _get_io_single(self, arg_type, arg_value, docid, nid):
        if arg_type in ("string", "number", "boolean", "datetime"):
            # value is already native => just return
            return arg_value
        elif arg_type == "doc":
            return _fetch_subdoc(self._sess, docid, nid)
        else:
            # try to load as a VQResource; if it fails, return doc
            try:
                return self._sess.load(arg_value)
            except BQApiError:
                return _fetch_subdoc(self._sess, docid, nid)

    def get_sub_states(self) -> dict:
        """
        Retrieve states in all submexes of a multimex run.

        Returns:
            submex states and counts
        """
        query = f"""
            SELECT ?submex/@value_str AS state
                   COUNT(?submex/@value_str) AS count
            WHERE {{
                /mex:?this :/ mex:?mexref. ?mexref :-> /mex:?submex
                FILTER( ?this/@resource_uniq = "{self._doc_uniq}" )
            }}
            GROUP BY ?submex/@value_str
            """
        matches = run_sparql_query(self._sess, query)
        return {match["state"]: int(match["count"]) for match in matches}

    def get_all_mexes(self) -> VQCollection:
        """
        Get collection of mex and all its submexes.

        Returns:
            collection of mex and submexes
        """
        query = f"""{{ /mex:?mex FILTER( ?mex/@resource_uniq = "{self._doc_uniq}" ) }} UNION
                    {{ /mex:?supermex :/ mex:?mexref. ?mexref :-> /mex:?mex FILTER( ?supermex/@resource_uniq = "{self._doc_uniq}" ) }}"""
        return VQCollection(self._sess, from_query=(query, "mex"))

    as_native = VQResource.as_dict


class VQModule(VQResource):
    """
    Class representing an analysis Module.
    """

    resource_type = "module"

    @classmethod
    def find(cls, sess: "VQSession", module_name: str) -> "VQModule":
        """
        Find module for given module name.

        Args:
            sess: session
            module_name: name of the module

        Returns:
            module resource

        Raises:
            BQApiError
        """
        # TODO: the following could be moved into the lower level build api
        query = f"""
            SELECT ?mod/@resource_uniq AS module_id
            WHERE {{
                /module:?mod
                FILTER( ?mod/@name = "{module_name}" )
            }}
            """
        matches = run_sparql_query(sess, query)
        if len(matches) == 0:
            raise BQApiError(f'module "{module_name}" not found')
        if len(matches) > 1:
            raise BQApiError(f'multiple modules "{module_name}" found')
        return VQResource.load(sess, matches[0]["module_id"])

    @property
    def builds(self) -> list["VQBuild"]:
        """
        Get all builds for this module, from newest to oldest.

        Returns:
            list of VQBuild objects
        """
        query = f"""
        SELECT ?bld/@resource_uniq AS build_id
        WHERE {{
           /build:?bld :/ module:?modref. ?modref :-> /module:?mod
           FILTER( ?mod/@resource_uniq = "{self._doc_uniq}" )
        }}
        ORDER BY DESC(?bld/@created)
        """
        matches = run_sparql_query(self._sess, query)
        return [self._sess.load(match["build_id"]) for match in matches]

    @property
    def inputs(self) -> list[tuple[str, str, str]]:
        """
        Get list of input names.

        Returns:
            list of (input name, input type, label)
        """
        self._refresh(lvls=sys.maxsize)
        return [
            (module_arg.get_attr("name"), _get_param_types(module_arg), _get_param_label(module_arg))
            for module_arg in self._doc.path_query('/module/inputs//*[not(@type) or @type != "group"][./template]')
        ]

    @property
    def outputs(self) -> list[tuple[str, str]]:
        """
        Get list of output names.

        Returns:
            list of (output name, output type)
        """
        self._refresh(lvls=sys.maxsize)
        return [
            (module_arg.get_attr("name"), _get_param_types(module_arg, "doc"), _get_param_label(module_arg))
            for module_arg in self._doc.path_query('/module/outputs//*[not(@type) or @type != "group"][./template]')
        ]

    def run(
        self,
        _keep_log: bool = False,
        _extra_tags: dict = None,
        _execute_options: dict = None,
        _merge_outputs: list = None,
        inputs: dict = None,
        **kwargs,
    ) -> VQMex:
        """
        Start this module (latest registered version) with the given input parameters.

        Args:
            _keep_log: preserve log of run in module execution dir
            _extra_tags: extra tags to be added to Mex
            _execute_options: override execute options (e.g., "requested_memory", "requested_gpus")
            _merge_outputs: list of output names for submex output merging
            inputs: a dict with complete hierarchical names of input params, like 'fibers/threshold'
            kwargs: input parameters (will be mapped to module inputs)

        Returns:
            mex doc

        Raises:
            BQApiError
        """
        return self.builds[0].run(
            _keep_log=_keep_log,
            _extra_tags=_extra_tags,
            _execute_options=_execute_options,
            _merge_outputs=_merge_outputs,
            inputs=inputs,
            **kwargs,
        )

    start = run

    def last_run(
        self,
        _keep_log: bool = False,
        _extra_tags: dict = None,
        _execute_options: dict = None,
        _merge_outputs: list = None,
        _last_run_status: str | list[str] = None,
        _last_run_not_status: str | list[str] = None,
        _last_run_version: str | None = None,
        _input_ts_check: bool = False,
        **kwargs,
    ) -> VQMex:
        """
        Find latest previous run with given input parameters.

        Args:
            _keep_log: preserve log of run in module execution dir (not used)
            _extra_tags: extra tags to be added to Mex (not used)
            _execute_options: execute options to match (e.g., "requested_memory", "requested_gpus")
            _merge_outputs: list of output names for submex output merging (not used)
            _last_run_status: allowed statuses of run; can use wildcard "*"
            _last_run_not_status: not allowed statuses of run; can use wildcard "*"
            _last_run_version: if not None, find only runs with this version
            _input_ts_check: if True, find only mexes with input resources older than mex
            kwargs: input parameters to match (will be mapped to module inputs)

        Returns:
            mex doc of latest run

        Raises:
            BQApiError
        """
        module_name = self.get("name")
        res = self._sess.find(
            "mex",
            module_name=module_name,
            version=_last_run_version,
            status=_last_run_status,
            not_status=_last_run_not_status,
            _input_ts_check=_input_ts_check,
            _execute_options=_execute_options,
            **kwargs,
        )
        if isinstance(res, VQCollection):
            match = None
            for match in res.order_by([("@created", "desc")]).limit(1):  # only get the latest
                break
            if match is None:
                raise BQApiError("no matching run found")
            res = match
        return res

    def last_good_run(
        self,
        _keep_log: bool = False,
        _extra_tags: dict = None,
        _execute_options: dict = None,
        _merge_outputs: list = None,
        _last_run_version: str | None = None,
        _input_ts_check: bool = False,
        **kwargs,
    ) -> VQMex:
        """
        Find latest previous successful run with given input parameters.

        Args:
            _keep_log: preserve log of run in module execution dir (not used)
            _extra_tags: extra tags to be added to Mex (not used)
            _execute_options: execute options to match (e.g., "requested_memory", "requested_gpus")
            _merge_outputs: list of output names for submex output merging (not used)
            _last_run_version: if not None, find only runs with this version
            _input_ts_check: if True, find only mexes with input resources older than mex
            kwargs: input parameters to match (will be mapped to module inputs)

        Returns:
            mex doc of latest run

        Raises:
            BQApiError
        """
        return self.last_run(
            _keep_log=_keep_log,
            _extra_tags=_extra_tags,
            _execute_options=_execute_options,
            _merge_outputs=_merge_outputs,
            _last_run_status="FINISHED",
            _last_run_version=_last_run_version,
            _input_ts_check=_input_ts_check,
            **kwargs,
        )

    def last_bad_run(
        self,
        _keep_log: bool = False,
        _extra_tags: dict = None,
        _execute_options: dict = None,
        _merge_outputs: list = None,
        _last_run_version: str | None = None,
        _input_ts_check: bool = False,
        **kwargs,
    ) -> VQMex:
        """
        Find latest previous failed run with given input parameters.

        Args:
            _keep_log: preserve log of run in module execution dir (not used)
            _extra_tags: extra tags to be added to Mex (not used)
            _execute_options: execute options to match (e.g., "requested_memory", "requested_gpus")
            _merge_outputs: list of output names for submex output merging (not used)
            _last_run_version: if not None, find only runs with this version
            _input_ts_check: if True, find only mexes with input resources older than mex
            kwargs: input parameters to match (will be mapped to module inputs)

        Returns:
            mex doc of latest run

        Raises:
            BQApiError
        """
        return self.last_run(
            _keep_log=_keep_log,
            _extra_tags=_extra_tags,
            _execute_options=_execute_options,
            _merge_outputs=_merge_outputs,
            _last_run_status="FAILED",
            _last_run_version=_last_run_version,
            _input_ts_check=_input_ts_check,
            **kwargs,
        )

    def find_or_run(
        self,
        _keep_log: bool = False,
        _extra_tags: dict = None,
        _execute_options: dict = None,
        _merge_outputs: list = None,
        _last_run_version: str | None = None,
        _ignore_for_find: list[str] | None = None,
        _input_ts_check: bool = False,
        **kwargs,
    ) -> VQMex:
        """
        Find successful run with the given input parameters or start a new one (latest version) if none found.

        Args:
            _keep_log: preserve log of run in module execution dir
            _extra_tags: extra tags to be added to Mex
            _execute_options: override execute options (e.g., "requested_memory", "requested_gpus")
            _merge_outputs: list of output names for submex output merging
            _last_run_version: if not None, find only runs with this version
            _ignore_for_find: inputs in kwargs to ignore during "find" phase
            _input_ts_check: if True, find only mexes with input resources older than mex
            kwargs: input parameters (will be mapped to module inputs)

        Returns:
            mex doc

        Raises:
            BQApiError
        """
        _ignore_for_find = _ignore_for_find or []
        find_kwargs = {k: v for k, v in kwargs.items() if k not in _ignore_for_find}
        try:
            # return self.last_good_run(
            #     _keep_log=_keep_log,
            #     _extra_tags=_extra_tags,
            #     #_execute_options=_execute_options,  # don't match exec options
            #     _merge_outputs=_merge_outputs,
            #     _last_run_version=_last_run_version,
            #     _input_ts_check=_input_ts_check,
            #     **find_kwargs,
            # )

            # find finished or running mexs
            return self.last_run(
                _keep_log=_keep_log,
                _extra_tags=_extra_tags,
                # _execute_options=_execute_options,  # don't match exec options
                _merge_outputs=_merge_outputs,
                _last_run_version=_last_run_version,
                _input_ts_check=_input_ts_check,
                _last_run_not_status=["STOPPED", "FAILED"],
                **find_kwargs,
            )

        except BQApiError:
            # not found => start it
            return self.run(
                _keep_log=_keep_log,
                _extra_tags=_extra_tags,
                _execute_options=_execute_options,
                _merge_outputs=_merge_outputs,
                **kwargs,
            )

    def inputname_to_label(self, inputname: str) -> str:
        """
        Convert internal input name to UI label.

        Args:
            inputname: input name to convert

        Returns:
            UI label if found, else None
        """
        for inputname_iter, _, label_iter in self.inputs:
            if inputname_iter == inputname:
                return label_iter
        return None

    def label_to_inputname(self, label: str) -> str:
        """
        Convert UI label to internal input name.

        Args:
            label: UI label to convert

        Returns:
            internal input name if found, else None
        """
        for inputname_iter, _, label_iter in self.inputs:
            if label_iter == label:
                return inputname_iter
        return None

    def outputname_to_label(self, outputname: str) -> str:
        """
        Convert internal output name to UI label.

        Args:
            outputname: output name to convert

        Returns:
            UI label if found, else None
        """
        for outputname_iter, _, label_iter in self.outputs:
            if outputname_iter == outputname:
                return label_iter
        return None

    def label_to_outputname(self, label: str) -> str:
        """
        Convert UI label to internal output name.

        Args:
            label: UI label to convert

        Returns:
            internal output name if found, else None
        """
        for outputname_iter, _, label_iter in self.outputs:
            if label_iter == label:
                return outputname_iter
        return None

    as_native = VQResource.as_dict


class VQBuild(VQModule):
    """
    Class representing a Build (specific analysis module version).
    """

    resource_type = "build"

    @classmethod
    def find(cls, sess: "VQSession", module_name: str, version: str | None = None) -> "VQBuild":
        """
        Fetch build doc for given module/version combo.

        Args:
            sess: session
            module_name: name of the module
            version: version tag of build (or None to find the latest version)

        Returns:
            build doc

        Raises:
            BQApiError
        """
        # TODO: the following could be moved into the lower level build api
        build_filter = f' AND ?bld/@name = "{version}"' if version is not None else ""
        query = f"""
            SELECT ?bld/@resource_uniq AS build_id
            WHERE {{
                /build:?bld :/ module:?modref. ?modref :-> /module:?mod
                FILTER( ?mod/@name = "{module_name}" {build_filter} )
            }}
            ORDER BY DESC(?bld/@created)
            """
        matches = run_sparql_query(sess, query)
        if len(matches) == 0:
            raise BQApiError(f'module "{module_name}" (version "{version}") not found')
        if len(matches) > 1 and version is not None:
            raise BQApiError(f'multiple modules "{module_name}" (version "{version}") found')
        return VQResource.load(sess, matches[0]["build_id"])

    def get_module(self) -> VQModule:
        """
        Get module def for this build.

        Returns:
            module doc
        """
        self._refresh(lvls=2)
        module_id = self._doc.path_query("//module")[0]
        return VQModule.load(self._sess, module_id.get_value())

    @property
    def inputs(self) -> list[tuple[str, str, str]]:
        """
        Get list of input names.

        Returns:
            list of (input name, input type, label)
        """
        self._refresh(lvls=sys.maxsize)
        return [
            (module_arg.get_attr("name"), _get_param_types(module_arg), _get_param_label(module_arg))
            for module_arg in self._doc.path_query('/build/inputs//*[not(@type) or @type != "group"][./template]')
        ]

    @property
    def outputs(self) -> list[tuple[str, str]]:
        """
        Get list of output names.

        Returns:
            list of (output name, output type)
        """
        self._refresh(lvls=sys.maxsize)
        return [
            (module_arg.get_attr("name"), _get_param_types(module_arg, "doc"), _get_param_label(module_arg))
            for module_arg in self._doc.path_query('/build/outputs//*[not(@type) or @type != "group"][./template]')
        ]

    def last_good_run(
        self,
        _keep_log: bool = False,
        _extra_tags: dict = None,
        _execute_options: dict = None,
        _merge_outputs: list = None,
        _ignore_version: bool = False,
        _input_ts_check: bool = False,
        **kwargs,
    ) -> VQMex:
        """
        Find latest previous successful run with given input parameters.

        Args:
            _keep_log: preserve log of run in module execution dir (not used)
            _extra_tags: extra tags to be added to Mex (not used)
            _execute_options: execute options to match (e.g., "requested_memory", "requested_gpus")
            _merge_outputs: list of output names for submex output merging (not used)
            _ignore_version: if True, search in all available module versions
            _input_ts_check: if True, find only mexes with input resources older than mex
            kwargs: input parameters to match (will be mapped to module inputs)

        Returns:
            mex doc of latest run

        Raises:
            BQApiError
        """
        return self.last_run(
            _keep_log=_keep_log,
            _extra_tags=_extra_tags,
            _execute_options=_execute_options,
            _merge_outputs=_merge_outputs,
            _last_run_status="FINISHED",
            _ignore_version=_ignore_version,
            _input_ts_check=_input_ts_check,
            **kwargs,
        )

    def last_bad_run(
        self,
        _keep_log: bool = False,
        _extra_tags: dict = None,
        _execute_options: dict = None,
        _merge_outputs: list = None,
        _ignore_version: bool = False,
        _input_ts_check: bool = False,
        **kwargs,
    ) -> VQMex:
        """
        Find latest previous failed run with given input parameters.

        Args:
            _keep_log: preserve log of run in module execution dir (not used)
            _extra_tags: extra tags to be added to Mex (not used)
            _execute_options: execute options to match (e.g., "requested_memory", "requested_gpus")
            _merge_outputs: list of output names for submex output merging (not used)
            _ignore_version: if True, search in all available module versions
            _input_ts_check: if True, find only mexes with input resources older than mex
            kwargs: input parameters to match (will be mapped to module inputs)

        Returns:
            mex doc of latest run

        Raises:
            BQApiError
        """
        return self.last_run(
            _keep_log=_keep_log,
            _extra_tags=_extra_tags,
            _execute_options=_execute_options,
            _merge_outputs=_merge_outputs,
            _last_run_status="FAILED",
            _ignore_version=_ignore_version,
            _input_ts_check=_input_ts_check,
            **kwargs,
        )

    def last_run(
        self,
        _keep_log: bool = False,
        _extra_tags: dict = None,
        _execute_options: dict = None,
        _merge_outputs: list = None,
        _last_run_status: str | list[str] = None,
        _last_run_not_status: str | list[str] = None,
        _ignore_version: bool = False,
        _input_ts_check: bool = False,
        **kwargs,
    ) -> VQMex:
        """
        Find latest previous run with given input parameters.

        Args:
            _keep_log: preserve log of run in module execution dir (not used)
            _extra_tags: extra tags to be added to Mex (not used)
            _execute_options: execute options to match (e.g., "requested_memory", "requested_gpus")
            _merge_outputs: list of output names for submex output merging (not used)
            _last_run_status: allowed statuses of run; can use wildcard "*"
            _last_run_not_status: not allowed statuses of run; can use wildcard "*"
            _ignore_version: if True, search in all available module versions
            _input_ts_check: if True, find only mexes with input resources older than mex
            kwargs: input parameters to match (will be mapped to module inputs)

        Returns:
            mex doc of latest run

        Raises:
            BQApiError
        """
        version = self.get("name") if _ignore_version is False else None
        return self.get_module().last_run(
            _keep_log=_keep_log,
            _extra_tags=_extra_tags,
            _execute_options=_execute_options,
            _merge_outputs=_merge_outputs,
            _last_run_status=_last_run_status,
            _last_run_not_status=_last_run_not_status,
            _last_run_version=version,
            _input_ts_check=_input_ts_check,
            **kwargs,
        )

    def run(
        self,
        _keep_log: bool = False,
        _extra_tags: dict = None,
        _execute_options: dict = None,
        _merge_outputs: list = None,
        inputs: dict = None,
        **kwargs,
    ) -> VQMex:
        """
        Start this build with the given input parameters.

        Args:
            _keep_log: preserve log of run in module execution dir
            _extra_tags: extra tags to be added to Mex
            _execute_options: override execute options (e.g., "requested_memory", "requested_gpus")
            _merge_outputs: list of output names for submex output merging
            inputs: a dict with complete hierarchical names of input params, like 'fibers/threshold'
            kwargs: input parameters (will be mapped to module inputs)

        Returns:
            mex doc

        Raises:
            BQApiError
        """

        self._refresh(lvls=sys.maxsize)  # we need most of the doc anyway

        # create new mex resource based on build doc
        mex_doc = Metadoc(tag="mex")

        # find out if there are iterable inputs
        iterable_nodes = self._doc.path_query("/build/execute_options/iterable")
        iterables = {
            iterable_node.get_value_str(): iterable_node.get("type", "string") for iterable_node in iterable_nodes
        }

        # copy inputs from build doc, remove templates and overwrite any params
        build_inputs = self._doc.path_query("/build/inputs")[0]
        mex_inputs = copy.deepcopy(build_inputs)

        # fill in parameters from kwargs
        add_iterables = {}
        for param_name, param_val in kwargs.items():
            module_arg = mex_inputs.path_query(f'/inputs//{param_name}[not(@type) or @type != "group"][./template]')
            if len(module_arg) == 0:
                raise BQApiError(f'Unknown module parameter "{param_name}"')
            module_arg = module_arg[0]
            single_param_val = param_val
            skip_typecheck = False
            if isinstance(param_val, VQDataset) and param_name in iterables and iterables[param_name] == "dataset":
                add_iterables[param_name] = "dataset"
                skip_typecheck = True  # would need to check the type of elements of dataset
            elif isinstance(param_val, list) and not any(
                ptype.startswith("list") for ptype in _get_param_types(module_arg)
            ):
                if param_name in iterables and iterables[param_name].startswith("list"):
                    add_iterables[param_name] = Metadoc(tag="tmp", value=param_val).get_attr("type")
                    single_param_val = param_val[0]
                else:
                    raise BQApiError(f'List of values provided for non-iterable parameter "{param_name}"')
            if not skip_typecheck:
                if (
                    (isinstance(single_param_val, bool) and "boolean" not in _get_param_types(module_arg))
                    or (
                        isinstance(single_param_val, (int, float, complex))
                        and not isinstance(single_param_val, bool)
                        and "number" not in _get_param_types(module_arg)
                    )
                    or (
                        isinstance(single_param_val, str)
                        and "string" not in _get_param_types(module_arg)
                        and "combo" not in _get_param_types(module_arg)
                    )
                    or (
                        isinstance(single_param_val, list)
                        and not any(ptype.startswith("list") for ptype in _get_param_types(module_arg))
                    )
                    or (
                        isinstance(single_param_val, VQResource)
                        and single_param_val.resource_type not in _get_param_types(module_arg)
                        and "resource" not in _get_param_types(module_arg)
                    )
                ):
                    if not isinstance(single_param_val, str) or all(
                        ptype in ("number", "boolean") or ptype in RESERVED_TAGNAMES or ptype.startswith("list")
                        for ptype in _get_param_types(module_arg)
                    ):
                        raise BQApiError(
                            f'Type mismatch for module parameter "{param_name}"; expected: {_get_param_types(module_arg)} got: {type(single_param_val)}'
                        )
                    else:
                        log.info('passing parameter "%s" (type %s) as string', param_name, _get_param_types(module_arg))
            if isinstance(param_val, VQResource):
                module_arg.set_value(param_val.get_docid())
                module_arg.set_attr("type", param_val.resource_type)
            elif isinstance(param_val, (bool, int, float, complex, list, str)):
                module_arg.set_value(param_val)
            else:
                module_arg.set_value(str(param_val))

        # fill inputs from inputs dict, can be used in addition to the function arguments
        if inputs is not None:
            for param_name, param_val in inputs.items():
                param_name = param_name.lstrip("/")
                module_arg = mex_inputs.path_query(f"/inputs/{param_name}")
                if len(module_arg) == 0:
                    raise BQApiError(f'Unknown module parameter "{param_name}"')
                module_arg = module_arg[0]
                single_param_val = param_val
                if isinstance(param_val, VQDataset) and param_name in iterables and iterables[param_name] == "dataset":
                    add_iterables[param_name] = "dataset"
                elif isinstance(param_val, list) and not any(
                    ptype.startswith("list") for ptype in _get_param_types(module_arg)
                ):
                    if param_name in iterables and iterables[param_name].startswith("list"):
                        add_iterables[param_name] = Metadoc(tag="tmp", value=param_val).get_attr("type")
                        single_param_val = param_val[0]
                    else:
                        raise BQApiError(f'List of values provided for non-iterable parameter "{param_name}"')

                if isinstance(param_val, VQResource):
                    module_arg.set_value(param_val.get_docid())
                    module_arg.set_attr("type", param_val.resource_type)
                elif isinstance(param_val, (bool, int, float, complex, list, str)):
                    module_arg.set_value(param_val)
                else:
                    module_arg.set_value(str(param_val))

        # remove templates
        for templ in mex_inputs.path_query("//template"):
            templ.delete()

        # add inputs to mex
        mex_doc.add_child(mex_inputs)

        # add iterable / keep_log options / overrides
        if len(add_iterables) > 0 or _keep_log or _execute_options:
            ex_opt_tag = mex_doc.add_tag("execute_options")
            for iter_name, iter_type in add_iterables.items():
                ex_opt_tag.add_tag("iterable", type=iter_type, value=iter_name)
            if _keep_log:
                ex_opt_tag.add_tag("keep_log", value="true")
            if _merge_outputs:
                for out_name in _merge_outputs:
                    ex_opt_tag.add_tag("mergeable", type="dataset", value=out_name)
            if _execute_options:
                for key, val in _execute_options.items():
                    ex_opt_tag.add_tag(key, value=str(val))  # force as str for now, since mex doc validator expects it

        # add build reference
        mex_doc.add_tag("build", value=self.get_docid())

        # add any extra tags
        if _extra_tags:
            extra_tag = mex_doc.add_tag("optional-tags")
            for key, val in _extra_tags.items():
                extra_tag.add_tag(key, value=val)

        # POST mex doc to mex_service to start module
        mex_service = self._sess.service("mexes")
        try:
            mex_doc = mex_service.request(path="/", method="post", render="doc", data=mex_doc)
            if not isinstance(mex_doc, Metadoc):
                raise BQApiError(f"module could not be started: {mex_doc.text}")
        except Exception as exc:
            raise BQApiError(f"module could not be started: {str(exc)}")

        # return created mex resource
        return VQMex.load(self._sess, mex_doc.get_docid())

    def find_or_run(
        self,
        _keep_log: bool = False,
        _extra_tags: dict = None,
        _execute_options: dict = None,
        _merge_outputs: list = None,
        _ignore_version: bool = False,
        _ignore_for_find: list[str] | None = None,
        _input_ts_check: bool = False,
        **kwargs,
    ) -> VQMex:
        """
        Find successful run with the given input parameters or start a new one (this build) if none found.

        Args:
            _keep_log: preserve log of run in module execution dir
            _extra_tags: extra tags to be added to Mex
            _execute_options: override execute options (e.g., "requested_memory", "requested_gpus")
            _merge_outputs: list of output names for submex output merging
            _ignore_version: if True, search in all available module versions
            _ignore_for_find: inputs in kwargs to ignore during "find" phase
            _input_ts_check: if True, find only mexes with input resources older than mex
            kwargs: input parameters (will be mapped to module inputs)

        Returns:
            mex doc

        Raises:
            BQApiError
        """
        _ignore_for_find = _ignore_for_find or []
        find_kwargs = {k: v for k, v in kwargs.items() if k not in _ignore_for_find}
        try:
            # return self.last_good_run(
            #     _keep_log=_keep_log,
            #     _extra_tags=_extra_tags,
            #     #_execute_options=_execute_options,  # don't match exec options
            #     _merge_outputs=_merge_outputs,
            #     _ignore_version=_ignore_version,
            #     _input_ts_check=_input_ts_check,
            #     **find_kwargs,
            # )

            # find finished or running mexs
            return self.last_run(
                _keep_log=_keep_log,
                _extra_tags=_extra_tags,
                # _execute_options=_execute_options,  # don't match exec options
                _merge_outputs=_merge_outputs,
                _ignore_version=_ignore_version,
                _input_ts_check=_input_ts_check,
                _last_run_not_status=["STOPPED", "FAILED"],
                **find_kwargs,
            )

        except BQApiError:
            # not found => start it
            return self.run(
                _keep_log=_keep_log,
                _extra_tags=_extra_tags,
                _execute_options=_execute_options,
                _merge_outputs=_merge_outputs,
                **kwargs,
            )

    start = run

    as_native = VQResource.as_dict


class VQTableContainer(VQResource):
    resource_type = "tablecontainer"

    @staticmethod
    def concat(
        sess: "VQSession",
        table_containers: list["VQTableContainer"],
        in_path: str,
        out_path: str,
        dim: int,
    ) -> "VQTableContainer":
        pass  # !!!

    def get_array(self, path, slices=None):
        table_service = self._sess.service("tables")
        return table_service.load_array(table_uniq=self.get_docid(), path=path, slices=slices)

    def get_table(self, path, slices=None, as_dataframe=True):
        table_service = self._sess.service("tables")
        return table_service.load_table(
            table_uniq=self.get_docid(),
            path=path,
            slices=slices,
            as_dataframe=as_dataframe,
        )


class VQTable(VQResource):
    resource_type = "table"

    def get_table(self, slices=None, as_dataframe=True):
        table_service = self._sess.service("tables")
        return table_service.load_table(
            table_uniq=self.get_docid(),
            path="",
            slices=slices,
            as_dataframe=as_dataframe,
        )

    as_native = get_table


class VQFile(VQResource):
    resource_type = "file"

    as_native = VQResource.as_dict

    def __init__(self, sess, doc_uniq=None, doc_version=None, path=None, **attrs):
        # super().__init__(sess, doc_uniq=doc_uniq, doc_version=doc_version, **attrs)

        # need to rewrite it here to allow for doc_uniq as None
        self._doc_uniq = None if doc_uniq is None else _clean_uniq(doc_uniq)
        self._doc_version = doc_version
        self._doc_lvls = 0
        self._sess = sess
        self._meta = None if sess is None else sess.service("meta")
        # additional inits (may trigger refresh)
        self._doc = Metadoc(tag=self.resource_type, **attrs)

        self._path = path

    def __getattr__(self, name):
        if name in ("_path"):
            return self.__dict__[name]
        return super().__getattr__(name)

    def __setattr__(self, name, val):
        if name in ("_path"):
            self.__dict__[name] = val
            return
        return super().__setattr__(name, val)

    def get_docid(self) -> str:
        """
        Get UUID of this resource.

        Returns:
            UUID
        """
        return self._doc_uniq or self._path

    def get_value(self):
        if self._doc_uniq is None:
            return self._path
        return super().get_value()


class VQFilePath(VQFile):
    resource_type = "file_path"

    as_native = VQResource.as_dict


class VQDirPath(VQFile):
    resource_type = "dir_path"

    as_native = VQResource.as_dict


class VQDataset(VQResource):
    resource_type = "dataset"

    as_native = VQResource.as_dict


class VQConnoisseur(VQResource):
    resource_type = "connoisseur"

    as_native = VQResource.as_dict


class VQUser(VQResource):
    resource_type = "user"

    @classmethod
    def find(cls, sess: "VQSession") -> "VQUser":
        """
        Fetch current user.

        Args:
            sess: session

        Returns:
            user doc

        Raises:
            BQApiError
        """
        query = """
            SELECT ?usr/@resource_uniq AS user_id
            WHERE {{
                /user:?usr
            }}
            """
        matches = run_sparql_query(sess, query, wpublic="owner")
        if len(matches) == 0:
            raise BQApiError("no current user found")
        if len(matches) > 1:
            raise BQApiError("multiple users found")
        return VQResource.load(sess, matches[0]["user_id"])

    as_native = VQResource.as_dict


class VQPlotly(VQResource):
    resource_type = "plotly"

    def as_plotly(self):
        """
        Get plot as plotly figure.

        Returns:
            plotly.graph_objects.Figure
        """
        try:
            from plotly.graph_objects import Figure
        except ImportError:
            raise BQApiError("as_plotly requires installed plotly package")

        blob_service = self._sess.service("blobs")
        with blob_service.read_chunk(self.get_docid(), as_stream=True) as f:
            stored_fig = json.loads(f.readall().decode("utf-8"))
            return Figure(data=stored_fig[0], layout=stored_fig[1])

    # alias for backward comp
    show = as_plotly

    as_native = as_plotly


class VQHTML(VQResource):
    resource_type = "html"

    def as_html(self):
        """
        Get as html object.

        Returns:
            plotly.graph_objects.Figure
        """
        try:
            from IPython.core.display import HTML
        except ImportError:
            raise BQApiError("as_html requires installed IPython package")

        blob_service = self._sess.service("blobs")
        with blob_service.read_chunk(self.get_docid(), as_stream=True) as f:
            return HTML(f.readall().decode("utf-8"))

    as_native = as_html


class VQImage(VQResource):
    resource_type = "image"

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._geometry = None
        self._imgmeta = None
        self._imginfo = {}
        self._histogram = None

    def __getattr__(self, name):
        if name in ("_imgmeta", "_imginfo", "_geometry", "_histogram"):
            return self.__dict__[name]
        return super().__getattr__(name)

    def __setattr__(self, name, val):
        if name in ("_imgmeta", "_imginfo", "_geometry", "_histogram"):
            self.__dict__[name] = val
            return
        return super().__setattr__(name, val)

    def meta(self):
        "return image meta as doc"
        if self._imgmeta is None:
            info = self.pixels().meta().fetch(want_str=True)
            self._imgmeta = Metadoc(et=anyxml_to_etree(info))
            self._imginfo = self._imgmeta.to_json()["resource"]
        return self._imgmeta

    def info(self):
        "return image meta as dict"
        if self._imgmeta is None:
            self.meta()
        return self._imginfo

    def geometry(self):
        "return x,y,z,t,ch of image"
        if self._geometry is None:
            info = self.meta()
            geom = []
            for n in "xyztc":
                tn = info.path_query(f"//image_num_{n}")
                geom.append(tn[0].get("value"))
            self._geometry = tuple(map(int, geom))
        return self._geometry

    def histogram(self):
        "returns image histogram"
        if self._histogram is None:
            s = self.pixels().command("histogram", arguments="json").fetch(want_str=True)
            h = json.loads(s)
            if "histogram" in h:
                self._histogram = h["histogram"]
        return self._histogram

    def pixels(self):
        return self._sess.service("pixels").pixels(self.get_docid())


class VQFactory:
    resources = {
        x[1].resource_type: x[1]
        for x in inspect.getmembers(sys.modules[__name__])
        if inspect.isclass(x[1]) and hasattr(x[1], "resource_type")
    }

    def load(self, session: BQSession, uniq: str) -> VQResource:
        """
        Establish link to ViQi-backed resource via its uniq.

        Args:
            session (BQSession): initialized session
            uniq (str): resource uniq

        Returns:
            VQResource: the resource object
        """
        uniq = _clean_uniq(uniq)
        meta = session.service("meta")
        res = meta.request(method="get", path="/" + uniq, params={}, view="short", render=None)
        if res.status_code != 200:
            raise BQApiError(f"resource {uniq} could not be loaded")
        doc_version = get_header(res, "ETag")
        doc = res.doc()
        resource_type = doc.tag
        attrs = {"value": doc.get_value()}
        for attr in doc.attrib:
            attrs[attr] = doc.get(attr)
        c = self.resources.get(resource_type, VQResource)
        c.resource_type = resource_type
        return c(session, doc_uniq=uniq, doc_version=doc_version, **attrs)

    def find(self, session: BQSession, resource_type: str, **kwargs) -> VQResource | VQCollection:
        """
        Find a resource based on resource specific search args.

        Args:
            session (BQSession): initialized session
            resource_type (str): the type of the resource
            kwargs: type-specific search args

        Returns:
            the found resource or a collection of matching resources
        """
        c = self.resources.get(resource_type)
        return c.find(session, **kwargs)


class VQSession(BQSession):
    """
    A session with a ViQi server.
    """

    def __init__(self, **kw):
        super().__init__(**kw)
        self.factory = VQFactory()
        self._deltas = []

    def __getstate__(self):
        state = super().__getstate__()
        state.session_fields["_deltas"] = self._deltas
        state.session_fields["factory"] = self.factory
        return state

    # def __setstate__(self, state):
    #     super().__setstate__(state[0])
    #     self.factory = state[1]
    #     self._deltas = state[2]

    def init(
        self,
        bisque_url,
        credentials=None,
        moduleuri=None,
        create_mex=False,
        enable_cache=True,
    ):
        res = super().init(bisque_url, credentials, moduleuri, create_mex, enable_cache=enable_cache)
        # self.factory = VQFactory()
        # self._init_cache()
        return res

    def init_local(
        self,
        user: str,
        pwd: str,
        moduleuri: str = None,
        bisque_root: str = None,
        create_mex: bool = True,
        as_user: str = None,
        enable_cache: bool = False,
    ) -> "VQSession":
        """
        Initialize a session based on user name and password.

        Args:
            user: user id (email)
            pwd: password
            moduleuri: module uri to be set to the mex (only matters if create_mex is set to True)
            bisque_root: the root URL of the ViQi platform the user is trying to access
            create_mex: creates a mex session under the user
            as_user: switch session to specified user id (only for admin)
            enable_cache: enable request caching under this session (should be False)

        Returns
            initialized session

        Examples:
            >>> sess = VQSession().init_local(
            ...     "clang@viqiai.com", "pass", bisque_root="https://science.viqiai.cloud", create_mex=False
            ... )
        """
        res = super().init_local(
            user=user,
            pwd=pwd,
            moduleuri=moduleuri,
            bisque_root=bisque_root,
            create_mex=create_mex,
            as_user=as_user,
            enable_cache=enable_cache,
        )
        # self.factory = VQFactory()
        # self._init_cache()
        return res

    def init_mex(
        self, mex_url: str, token: str, user: str = None, bisque_root: str = None, enable_cache: bool = False
    ) -> "VQSession":
        """
        Initialize a session based on a mex url and token (typically used for debug mexes).

        Args:
            mex_url: mex url to initalize the session from
            token: the mex token to access the mex
            bisque_root: the root URL of the ViQi platform the user is trying to access
            enable_cache: enable request caching under this session (should be False)

        Returns
            initialized session

        Examples:
            >>> sess = VQSession().init_mex(
            ...     "https://science.viqiai.cloud/00-dkjqbdkjqdgq",
            ...     "kfjffwerf__whhhe8fye-89fhwe8h",
            ...     bisque_root="https://science.viqiai.cloud",
            ... )
        """
        res = super().init_mex(mex_url, token, user, bisque_root, enable_cache=enable_cache)
        ##self.factory = VQFactory()
        # self._init_cache()
        return res

    def init_request(self, request, enable_cache=True):
        res = super().init_request(request, enable_cache=enable_cache)
        # self.factory = VQFactory()
        # self._init_cache()
        return res

    def load(self, uniq: str) -> VQResource:
        """
        Load a resource from resource UUID.

        Args:
            uniq: resource UUID

        Returns:
            loaded resource
        """
        return self.factory.load(self, uniq)

    def flush(self):
        """
        Write any pending doc changes back to ViQi server.
        """
        if len(self._deltas) > 0:
            # some local changes => try to write them back as PATCH
            raise NotImplementedError(
                "write back of metadata docs not implemented"
            )  # need to write back if any changes or new doc (might throw version conflict!)

    def find(self, resource_type: str, **kwargs) -> VQResource | VQCollection:
        """
        Find a resource based on resource specific search args.

        Args:
            resource_type: the type of the resource
            kwargs: type-specific search args

        Returns:
            the found resource or a collection if multiple matches
        """
        return self.factory.find(self, resource_type, **kwargs)

    def select_from_sparql(self, pattern: str, select_var: str) -> VQCollection:
        """
        Select one or more resources based on a SPARQL WHERE clause.

        Args:
            pattern: the SPARQL WHERE clause
            select_var: the variable in the pattern that identifies the resources to select

        Returns:
            collection of resources that match pattern

        Examples:
            >>> res = sess.select_from_sparql(
            ...     "/mex:?mex :/ outputs:?out. ?out :/ image:?imgref. ?imgref :-> /image:?img", "img"
            ... )
        """
        res = VQCollection(self, from_query=(pattern, select_var))
        _ = len(res.limit(1))  # force query to catch any query errors
        res = res.limit(None)
        return res

    def select_from_tags(self, resource_type: str, **kwargs) -> VQCollection:
        """
        Select one or more resources based on a tag query.

        Args:
            resource_type: the resource type to find
            kwargs: the tag query

        Returns:
            collection of resources that match pattern

        Examples:
            >>> res = sess.select_from_tags("image", tag_query="plate:1234 AND @ts:>=2023-01-01")
        """
        res = VQCollection(self, from_tags=(resource_type, kwargs))
        _ = len(res.limit(1))  # force query to catch any query errors
        res = res.limit(None)
        return res

    def current_user(self) -> VQUser:
        """
        Return current user.

        Returns:
            user resource
        """
        return self.find("user")

    def get_provenance(
        self,
        seed: VQResource,
        upstream: bool = True,
        downstream: bool = True,
        max_fanout: int = 3,
        out_format: str = "dot",
    ) -> object:
        """
        Experimental fct to retrieve provenance graph.

        Args:
            seed (VQResource): starting resource for graph
            upstream (bool): find upstream provenance
            downstream (bool): find downstream provenance
            max_fanout (int): max fanout from/to mex after which "(More)" nodes are added
            out_format (str): desired return format ("dot" or "list")

        Returns:
            object: either DOT string or list of VQResources
        """
        return get_provenance(
            self,
            seed,
            upstream=upstream,
            downstream=downstream,
            max_fanout=max_fanout,
            out_format=out_format,
        )
