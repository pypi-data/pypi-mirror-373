import logging
from collections import namedtuple
from functools import lru_cache
from typing import List

from bq.metadoc.formats import Metadoc

from vqapi.exception import BQApiError

log = logging.getLogger("vqapi.vqquery")


def run_sparql_query(sess: "VQSession", query: str, **kwargs) -> List:  # noqa
    if "wpublic" not in kwargs:
        kwargs["wpublic"] = "1"  # search all visible by default
    meta = sess.service("meta")
    matches = meta.request(
        method="get",
        path="/",
        params={"sparql_query": " ".join(query.split()), **kwargs},
        render="doc",
    ).to_json()["result"]
    try:
        matches = matches["match"]
        if not isinstance(matches, list):
            matches = [matches]
    except KeyError:
        matches = []
    return matches


def run_tag_query(sess: "VQSession", rtype: str, **kwargs) -> Metadoc:  # noqa
    if "wpublic" not in kwargs:
        kwargs["wpublic"] = "1"  # search all visible by default
    meta = sess.service("meta")
    matches = meta.request(
        method="get",
        path=f"/{rtype}",
        params=kwargs,
        render="doc",
    )
    return matches


def get_provenance(
    sess: "VQSession",  # noqa
    seed: "VQResource",  # noqa
    upstream: bool = True,
    downstream: bool = True,
    max_fanout: int = 3,
    out_format: str = "dot",
) -> object:
    """
    Experimental fct to retrieve provenance graph in DOT notation
    """
    max_graph_size = 100
    supermex_map = {}  # mapping sub mex id -> super mex Node
    Node = namedtuple("Node", ["id", "name", "type", "supermex"])
    Edge = namedtuple("Edge", ["from_id", "to_id"])
    more_cnt = 0

    def _cache_submexes(res: Node) -> bool:
        query = f"""
            SELECT ?submexref/@value_str AS sub_id
            WHERE {{
                /mex:?supermex :/ mex:?submexref
                FILTER( ?supermex/@resource_uniq = "{res.id}" )
            }}
            """
        matches = run_sparql_query(sess, query)
        if len(matches) > 0:
            for match in matches:
                supermex_map[match["sub_id"]] = res
            return True
        else:
            return False

    @lru_cache(maxsize=None)
    def _supermex(res: Node) -> Node:
        # switch to supermex and add to map if appropriate
        if res.id in supermex_map:
            return supermex_map[res.id]
        query = f"""
            SELECT ?supermex/@resource_uniq AS super_id
                   ?supermex/@name AS name
            WHERE {{
                /mex:?supermex :/ mex:?submexref
                FILTER( ?submexref/@value_str = "{res.id}" )
            }}
            """
        matches = run_sparql_query(sess, query)
        if len(matches) > 0:
            # this is a submex => get and cache all submexes and return supermex
            super_res = Node(
                id=matches[0]["super_id"],
                name=matches[0]["name"],
                type="mex",
                supermex=True,
            )
            _cache_submexes(super_res)
        else:
            # this is a supermex or a normal mex => get/cache submexes and return res
            has_submexes = _cache_submexes(res)
            super_res = Node(id=res.id, name=res.name, type=res.type, supermex=has_submexes)
        return super_res

    @lru_cache(maxsize=None)
    def _input_resources(res: Node) -> List[Node]:
        # return all input resources of mex
        # if res is supermex, look in all sub-mexes, otherwise look in res
        query = f"""
            SELECT ?in/@type AS in_type
                   ?in/@value_str AS in_val
            WHERE {{
                /mex:?submex :/ inputs:?inputs. ?inputs :// tag:?in
                FILTER( ?submex/@resource_uniq = "{res.id}" )
            }}
            """
        matches = run_sparql_query(sess, query)
        inputs = []
        for match in matches:
            if match["in_val"] and (match["in_type"] or "string") in list(sess.factory.resources.keys()) + ["resource"]:
                vqr = sess.load(match["in_val"])
                inputs.append(
                    Node(
                        id=vqr.get_docid(),
                        name=vqr.get("name"),
                        type=vqr.resource_type,
                        supermex=False,
                    )
                )
        return inputs

    @lru_cache(maxsize=None)
    def _output_resources(res: Node) -> List[Node]:
        # return all output resources of mex
        # if res is supermex, look in all sub-mexes, otherwise look in res
        query = f"""
            SELECT ?out/@type AS out_type
                   ?out/@value_str AS out_val
            WHERE {{
                /mex:?submex :/ outputs:?outputs. ?outputs :// tag:?out
                FILTER( ?submex/@resource_uniq = "{res.id}" )
            }}
            """
        matches = run_sparql_query(sess, query)
        outputs = []
        for match in matches:
            if match["out_val"] and (match["out_type"] or "doc") in list(sess.factory.resources.keys()) + ["resource"]:
                vqr = sess.load(match["out_val"])
                outputs.append(
                    Node(
                        id=vqr.get_docid(),
                        name=vqr.get("name"),
                        type=vqr.resource_type,
                        supermex=False,
                    )
                )
        return outputs

    @lru_cache(maxsize=None)
    def _down_mexes(res: Node) -> List[Node]:
        # return all mexes that have res as input
        nonlocal more_cnt
        query = f"""
            SELECT ?mex/@resource_uniq AS mex_id
            WHERE {{
                /mex:?mex :/ inputs:?inputs. ?inputs :// tag:?in
                FILTER( ?in/@value_str = "{res.id}" AND
                        NOT EXISTSP {{ /mex:?supermex :/ mex:?submexref. ?submexref :-> ?mex }} )
            }}
            """
        matches = run_sparql_query(sess, query, limit=max_fanout + 1)
        mexes = []
        for idx, match in enumerate(matches):
            if idx == max_fanout:
                mexes.append(Node(id=f"99-{more_cnt}", name=None, type=None, supermex=False))
                more_cnt += 1
                break
            vqr = sess.load(match["mex_id"])
            mexes.append(
                Node(
                    id=vqr.get_docid(),
                    name=vqr.get("name"),
                    type=vqr.resource_type,
                    supermex=False,
                )
            )
        return mexes

    @lru_cache(maxsize=None)
    def _up_mexes(res: Node) -> List[Node]:
        # return all mexes that have res as output
        nonlocal more_cnt
        query = f"""
            SELECT ?mex/@resource_uniq AS mex_id
            WHERE {{
                /mex:?mex :/ outputs:?outputs. ?outputs :// tag:?out
                FILTER( ?out/@value_str = "{res.id}" AND
                        NOT EXISTSP {{ /mex:?supermex :/ mex:?submexref. ?submexref :-> ?mex }} )
            }}
            """
        matches = run_sparql_query(sess, query, limit=max_fanout + 1)
        mexes = []
        for idx, match in enumerate(matches):
            if idx == max_fanout:
                mexes.append(Node(id=f"99-{more_cnt}", name=None, type=None, supermex=False))
                more_cnt += 1
                break
            vqr = sess.load(match["mex_id"])
            mexes.append(
                Node(
                    id=vqr.get_docid(),
                    name=vqr.get("name"),
                    type=vqr.resource_type,
                    supermex=False,
                )
            )
        return mexes

    curr_seeds = [
        (
            Node(
                id=seed.get_docid(),
                name=seed.get("name"),
                type=seed.resource_type,
                supermex=False,
            ),
            upstream,
            downstream,
        )
    ]
    nodes = {}  # map resource id -> Node
    edges = set()
    while len(curr_seeds) > 0:
        res, up, down = curr_seeds.pop(0)
        if res.type == "mex":
            res = _supermex(res)
            nodes[res.id] = res
            if up:
                for res_in in _input_resources(res):
                    if res_in.type == "mex":
                        res_in = _supermex(res_in)
                    if res_in.id not in nodes:
                        curr_seeds.append((res_in, True, False))
                        if len(nodes) + len(curr_seeds) > max_graph_size:
                            raise BQApiError("provenance graph too large")
                    edges.add(Edge(from_id=res_in.id, to_id=res.id))
            if down:
                for res_out in _output_resources(res):
                    if res_out.type == "mex":
                        res_out = _supermex(res_out)
                    if res_out.id not in nodes:
                        curr_seeds.append((res_out, False, True))
                        if len(nodes) + len(curr_seeds) > max_graph_size:
                            raise BQApiError("provenance graph too large")
                    edges.add(Edge(from_id=res.id, to_id=res_out.id))
        else:  # res is non-mex
            nodes[res.id] = res
            if down:
                for down_mex in _down_mexes(res):
                    if down_mex.id.startswith("99-"):
                        nodes[down_mex.id] = down_mex
                        edges.add(Edge(from_id=res.id, to_id=down_mex.id))
                        continue
                    down_mex = _supermex(down_mex)
                    if down_mex.id not in nodes:
                        curr_seeds.append((down_mex, False, True))
                        if len(nodes) + len(curr_seeds) > max_graph_size:
                            raise BQApiError("provenance graph too large")
                    edges.add(Edge(from_id=res.id, to_id=down_mex.id))
            if up:
                for up_mex in _up_mexes(res):
                    if up_mex.id.startswith("99-"):
                        nodes[up_mex.id] = up_mex
                        edges.add(Edge(from_id=up_mex.id, to_id=res.id))
                        continue
                    up_mex = _supermex(up_mex)
                    if up_mex.id not in nodes:
                        curr_seeds.append((up_mex, True, False))
                        if len(nodes) + len(curr_seeds) > max_graph_size:
                            raise BQApiError("provenance graph too large")
                    edges.add(Edge(from_id=up_mex.id, to_id=res.id))

    if out_format == "dot":
        # convert nodes and edges to DOT
        def _dot_name(res):
            return f'"{res.type} {res.id}\n{res.name}"'

        def _dot_extras(res):
            extras = []
            if res.id.startswith("99-"):
                extras.append('label="(More)"')
                extras.append("style=dotted")
            if res.id == seed.get_docid():
                extras.append("color=red")
            if extras:
                return "[" + ",".join(extras) + "]"
            else:
                return ""

        dot_nodes = [f"{_dot_name(res)} {_dot_extras(res)}" for res in nodes.values()]
        dot_edges = [f"{_dot_name(nodes[res.from_id])} -> {_dot_name(nodes[res.to_id])}" for res in edges]
        return f"digraph {{ rankdir=LR; node [shape=box, margin=0.05, width=0, height=0, fontsize=10]; {'; '.join(dot_nodes)}; {'; '.join(dot_edges)} }}"

    elif out_format == "list":
        return [sess.load(res.id) for res in nodes.values()]

    else:
        raise BQApiError(f'unknown provenance format "{out_format}"')
