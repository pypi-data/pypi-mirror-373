import io
import logging
import os
import tempfile

import tifffile

from .base_proxy import FuturizedServiceProxy

log = logging.getLogger("vqapi.services")


class ImageProxy(FuturizedServiceProxy):
    service_name = "pixels"

    class ImagePixels:
        """manage requests to the image pixels"""

        def __init__(self, image_service, image_uniq):
            self.image_service = image_service
            self.image_uniq = image_uniq
            self.ops = []

        def _construct_url(self):
            """build the final url based on the operation"""
            return self.image_service.construct(
                path="{}?{}".format(self.image.get_docid(), "&".join("%s=%s" % tp for tp in self.ops))
            )

        # TODO: image_fetch instead of want_str, need better way to infer return type (binary or str)
        def fetch(self, path=None, stream=False, want_str=False):
            """resolve the current and fetch the pixel"""
            # url = self._construct_url()
            if path is not None:
                response = self.image_service.fetch_file(path=self.image_uniq, params=self.ops, localpath=path)
            else:
                response = self.image_service.fetch(self.image_uniq, params=self.ops, stream=stream)
                return response.text if want_str else response.content

        def command(self, operation, arguments=""):
            arguments = "" if arguments is None else arguments
            self.ops.append((operation, arguments))  # In case None is passed .. requests library removes
            return self

        def slice(self, x="", y="", z="", t=""):
            """Slice the current image"""
            return self.command("slice", f"{x},{y},{z},{t}")

        def format(self, fmt):
            return self.command("format", fmt)

        def resize(self, w="", h="", interpolation=""):
            """interpoaltion may be,[ NN|,BL|,BC][,AR]"""
            return self.command("resize", f"{w},{h},{interpolation}")

        def localpath(self):
            return self.command("localpath")

        def meta(self):
            return self.command("meta")

        def info(self):
            return self.command("info")

        def asarray(self):
            # Force format to be tiff by removing any format and append format tiff
            self.ops = [tp for tp in self.ops if tp[0] != "format"]
            self.format("tiff")
            with self.image_service.fetch(path=self.image_uniq, params=self.ops, stream=True) as response:
                # response.raw.decode_content = True
                return tifffile.imread(io.BytesIO(response.content))

        def savearray(self, fname, imdata=None, imshape=None, dtype=None, **kwargs):
            import_service = self.image_service.session.service("import_service")
            imfile = tempfile.mkstemp(suffix=".tiff")
            tifffile.imsave(imfile, imdata, imshape, dtype, **kwargs)
            import_service.transfer_fileobj(fname, fileobj=open(imfile, "rb"))
            os.remove(imfile)

        ## End ImagePixels

    def get_thumbnail(self, image_uniq, **kw):
        # url = urllib.parse.urljoin( self.session.service_map['image_service'], image_uniq, 'thumbnail' )
        r = self.get("%s/thumbnail" % image_uniq)
        return r

    def get_metadata(self, image_uniq, **kw):
        r = self.get("%s/meta" % image_uniq, render="doc").doc()
        return r

    def pixels(self, image_uniq):
        return ImageProxy.ImagePixels(self, image_uniq)
