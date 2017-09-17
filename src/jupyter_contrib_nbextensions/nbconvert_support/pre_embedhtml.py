# -*- coding: utf-8 -*-
"""Nbconvert preprocessor for the embedding img sources into the cells."""

from nbconvert.preprocessors import Preprocessor
from .embedhtml import EmbedHTMLExporter, HT, ImgTagTransform


class PyMarkdownPreprocessor(Preprocessor, EmbedHTMLExporter):
    """
    :mod:`nbconvert` Preprocessor which embeds graphics as base64 into markdown
    cells.

    This :class:`~nbconvert.preprocessors.Preprocessor` replaces kernel code in
    markdown cells with the results stored in the cell metadata.
    """

    def preprocess_cell(self, cell, resources, index):
        """
        Preprocess cell

        Parameters
        ----------
        cell : NotebookNode cell
            Notebook cell being processed
        resources : dictionary
            Additional resources used in the conversion process.  Allows
            preprocessors to pass variables into the Jinja engine.
        index : int
            Index of the cell being processed (see base.py)
        """

        if cell.cell_type == "markdown":
            if 'attachments' in cell.keys():
                self.attachments += cell['attachments']
            # Parse HTML and replace <img> tags with the embedded data
            transformer = HT()
            transformer.pushTagTransform(ImgTagTransform(
                path=resources['metadata']['path'],
                log=self.log))
            transformer.feed(cell)

            # Convert back to HTML
            embedded_output = transformer.get_html()

            return embedded_output, resources
        else:
            return cell, resources
