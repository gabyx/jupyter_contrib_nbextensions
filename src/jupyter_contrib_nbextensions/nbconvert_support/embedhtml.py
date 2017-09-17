"""Embed graphics into HTML Exporter class"""

import os
import base64
from nbconvert.exporters.html import HTMLExporter
from .html_parser import HTMLTransformer as HT
from ipython_genutils.ipstruct import Struct

try:
    from urllib.request import urlopen  # py3
except ImportError:
    from urllib2 import urlopen


class ImgTagTransform(HT.TagTransform):
    """
        Transforms <img> tags in the HTML.
    """

    def __init__(self, log):
        super(ImgTagTransform, self).__init__("ImgTagTransform", ["img"])
        self.log = log

    def transform(self, attrs):
        """Replace source url or file link with base64 encoded blob."""

        url = attrs["src"]
        imgformat = url.split('.')[-1]

        if url.startswith('data'):
            return  # Already in base64 Format

        self.log.info("try embedding url: %s, format: %s" % (url, imgformat))

        if url.startswith('http'):
            data = urlopen(url).read()
        elif url.startswith('attachment'):
            imgname = url.split(':')[1]
            available_formats = self.attachments[imgname]
            # get the image based on the configured image type priority
            for imgformat in self.config.NbConvertBase.display_data_priority:
                if imgformat in available_formats.keys():
                    b64_data = self.attachments[imgname][imgformat]
                    attrs["src"] = "data:%s;base64," % imgformat \
                        + b64_data
                    return
            raise ValueError("""Could not find attachment for image '%s'
                                 in notebook""" % imgname)
        else:
            filename = os.path.join(self.path, url)
            with open(filename, 'rb') as f:
                data = f.read()

        b64_data = base64.b64encode(data).decode("utf-8")
        if imgformat == "svg":
            prefix = "data:image/svg+xml;base64,"
        elif imgformat == "pdf":
            prefix = "data:application/pdf;base64,"
        else:
            prefix = "data:image/" + imgformat + ';base64,'

        attrs["src"] = prefix + b64_data


class EmbedHTMLExporter(HTMLExporter):
    """
    :mod:`nbconvert` Exporter which embeds graphics as base64 into html.

    Convert to HTML and embed graphics (pdf, svg and raster images) in the HTML
    file.

    Example usage::

        jupyter nbconvert --to html_embed mynotebook.ipynb
    """

    def from_notebook_node(self, nb, resources=None, **kw):
        output, resources = super(
            EmbedHTMLExporter, self).from_notebook_node(nb, resources)

        self.path = resources['metadata']['path']

        # Get attachments
        self.attachments = Struct()
        for cell in nb.cells:
            if 'attachments' in cell.keys():
                self.attachments += cell['attachments']

        # Parse HTML and replace <img> tags with the embedded data
        parser = HT()
        parser.pushTagTransform(ImgTagTransform(log=self.log))
        parser.feed(output)

        # Convert back to HTML
        embedded_output = parser.get_html()

        return embedded_output, resources
