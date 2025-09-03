###############################################################################
##  ViQi BisQue                                                              ##
##  ViQi Inc                                                                 ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2007-2023                                               ##
##     by the ViQI Inc                                                       ##
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
##                                                                           ##
## THIS SOFTWARE IS PROVIDED BY <COPYRIGHT HOLDER> ''AS IS'' AND ANY         ##
## EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE         ##
## IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR        ##
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> OR           ##
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,     ##
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,       ##
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR        ##
## PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF    ##
## LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING      ##
## NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS        ##
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.              ##
##                                                                           ##
## The views and conclusions contained in the software and documentation     ##
## are those of the authors and should not be interpreted as representing    ##
## official policies, either expressed or implied, of <copyright holder>.    ##
###############################################################################

import logging
import os
import posixpath
import shutil
import tempfile

import numpy as np
import pandas as pd
import tables
from bq.metadoc.formats import Metadoc

from vqapi.exception import BQApiError

from .base_proxy import FuturizedServiceProxy, custom_json_loads

# from botocore.credentials import RefreshableCredentials
# from botocore.session import get_session


log = logging.getLogger("vqapi.services")


def _to_dtype(typestr: str):
    if typestr in ("str", "string", "image"):
        return "O"
    else:
        return typestr


class TableProxy(FuturizedServiceProxy):
    service_name = "tables"

    def load_array(self, table_uniq, path, slices=None, want_info=False, use_binary_transfer=True):
        """
        Load array from BisQue.
        """
        slices = slices or []
        if table_uniq.startswith("http"):
            table_uniq = table_uniq.split("/")[-1]
        slice_list = []
        for single_slice in slices:
            if isinstance(single_slice, slice):
                slice_list.append(
                    "{};{}".format(
                        "" if single_slice.start is None else single_slice.start,
                        "" if single_slice.stop is None else single_slice.stop - 1,
                    )
                )
            elif isinstance(single_slice, int):
                slice_list.append(f"{single_slice};{single_slice}")
            else:
                raise BQApiError("malformed slice parameter")
        path = "/".join([table_uniq.strip("/"), path.strip("/")])
        info_url = "/".join([path, "info", "format:json"])
        info_response = self.get(info_url)
        try:
            num_dims = len(custom_json_loads(info_response.text).get("sizes"))
        except ValueError:
            raise BQApiError("array could not be read")
        # fill slices with missing dims
        for _ in range(num_dims - len(slice_list)):
            slice_list.append(";")

        if use_binary_transfer is False:
            # JSON TRANSFER -- SAFE BUT MAY BE SLOWER
            data_url = "/".join([path, ",".join(slice_list), "format:extjs"])
            response = self.get(data_url)
            # convert JSON to Numpy array
            res = custom_json_loads(response.content)
            res = np.array(
                [tuple(res["data"][ix]) for ix in range(len(res["data"]))],
                dtype=[(res["headers"][ix], _to_dtype(res["types"][ix])) for ix in range(len(res["headers"]))],
            )

        else:
            # BINARY TRANSFER -- NOT ALWAYS WORKING
            data_url = "/".join([path, ",".join(slice_list), "format:hdf"])
            response = self.get(data_url)
            # convert HDF5 to Numpy array (preserve indices??)
            with tables.open_file(
                "array.h5",
                driver="H5FD_CORE",
                driver_core_image=response.content,
                driver_core_backing_store=0,
            ) as h5file:
                res = h5file.root.array.read()

            # -------------------------------------------------------------------------------------
            # convert "|S" (bytearray) columns to correctly decoded "<U" (unicode) columns
            if res.dtype.kind == "V":  # compound => check each component
                # remember str cols and their original lengths
                strcols = {d[0]: int(d[1][2:]) for d in res.dtype.descr if d[1].startswith("|S")}
                # first, convert any dtype "|Sx" to "|O" to allow for padding with b'\x00'
                res = res.astype(
                    [(d[0], "|O") if d[0] in strcols else d for d in res.dtype.descr if d[0] in res.dtype.names]
                )  # skip cols that are not in names (object types seem to get lost via pytables)
                # pad any strcol with b'\x00' to be divisible by 4 (since it is assumed utf-32)
                with np.nditer(res, flags=["refs_ok"], op_flags=["readwrite"]) as it:
                    for row in it:
                        for fname in strcols:
                            row[fname] = (
                                row[fname].item() + b"\x00" * ((4 - (len(row[fname].item()) % 4)) % 4)
                            ).decode("utf-32")
                # next, convert any dtype "|Sx" to "<U(x/4)"
                res = res.astype(
                    [
                        (d[0], f"<U{strcols[d[0]]//4}") if d[0] in strcols else d
                        for d in res.dtype.descr
                        if d[0] in res.dtype.names
                    ]
                )  # skip cols that are not in names (object types seem to get lost via pytables)
            else:
                # single type
                if res.dtype.descr[0][1].startswith("|S"):
                    strlen = int(res.dtype.descr[0][1][2:])
                    # first, convert any dtype "|Sx" to "|O" to allow for padding with b'\x00'
                    res = res.astype("|O")
                    # pad any dtype "|Sx" with b'\x00' to be divisible by 4 (since it is assumed utf-32)
                    with np.nditer(res, flags=["refs_ok"], op_flags=["readwrite"]) as it:
                        for x in it:
                            x[...] = (x.item() + b"\x00" * ((4 - (len(x.item()) % 4)) % 4)).decode("utf-32")
                    # next, convert any dtype "|Sx" to "<U(x/4)"
                    res = res.astype(f"<U{strlen//4}")
            # -------------------------------------------------------------------------------------

        if want_info:
            return res, custom_json_loads(info_response.text)
        else:
            return res

    def store_array(self, array, storepath, name) -> Metadoc:
        """
        Store numpy array or record array in BisQue and return resource doc.
        """
        try:
            dirpath = tempfile.mkdtemp()
            # (1) store array as HDF5 file
            out_name = name + ".h5" if not name.endswith((".h5", ".hdf5")) else name  # importer needs extension .h5
            out_file = os.path.join(dirpath, out_name)
            with tables.open_file(out_file, "w", filters=tables.Filters(complevel=5)) as h5file:  # compression level 5
                if array.__class__.__name__ == "recarray":
                    h5file.create_table(h5file.root, name, array)
                elif array.__class__.__name__ == "ndarray":
                    h5file.create_array(h5file.root, name, array)
                else:
                    raise BQApiError("unknown array type")  # TODO: more specific error
            # (2) call bisque blob service with file
            mountpath = posixpath.join(storepath, out_name)
            blobs = self.session.service("blobs")
            blobs.create_blob(path=mountpath, localfile=out_file)
            # (3) register resource
            return blobs.register(path=mountpath)

        finally:
            shutil.rmtree(dirpath)

    def load_table(self, table_uniq, path, slices=None, as_dataframe=True):
        """
        Load table as a numpy recarray or pandas dataframe.
        """
        ndarr, info = self.load_array(table_uniq, path, slices, want_info=True, use_binary_transfer=False)

        #         # -------------------------------------------------------------------------------------
        #         # use format "<Ux" for any col of type "<Ux"
        #         if ndarr.dtype.kind == "V":
        #             # compound => check each component
        #             formats = [None]*len(info["types"])
        #             for ix in range(len(ndarr.dtype)):
        #                 formats[ix] = ndarr.dtype.descr[ix][1] if ndarr.dtype.descr[ix][1].startswith("<U") else info["types"][ix]
        #         else:
        #             # single type
        #             formats = [ndarr.dtype.descr[0][1] if ndarr.dtype.descr[0][1].startswith("<U") else ty for ty in info["types"]]
        #         # -------------------------------------------------------------------------------------

        if as_dataframe is True:
            res = pd.DataFrame(ndarr)
        else:
            # return as recarray
            res = ndarr.view(np.recarray)
        return res

    def store_table(self, table, storepath, name) -> Metadoc:
        """
        Store numpy recarray or pandas dataframe in BisQue and return resource doc.
        """
        if isinstance(table, pd.DataFrame):
            table = table.to_records()
        if table.__class__.__name__ != "recarray":
            raise BQApiError("unknown table type")  # TODO: more specific error
        return self.store_array(table, storepath, name)
