.. -*- mode: ReST -*-

.. _io:

============
Input/Output
============

.. contents:: Contents
   :local:


For reading, bibble provides :class:`~bibble.io.reader.BibbleReader`. 
      
For writing, bibble provides :class:`~bibble.io.writer.BibbleWriter` for writing bibtex,
:class:`~bibble..io.rst_writer.RstWriter` for converting bibtex to rst files (for use with
`sphinx_bib_domain`_). There is also :class:`~bibble.io.jinja_writer.JinjaWriter` for
writing out text files using jinja templates.





.. _sphinx_bib_domain: https://github.com/jgrey4296/sphinx_bib_domain

