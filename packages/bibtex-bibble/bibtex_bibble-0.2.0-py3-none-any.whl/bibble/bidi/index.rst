.. -*- mode: ReST -*-

.. _bidi:

=========================
Bidirectional Middlewares
=========================

.. contents:: Contents
   :local:

      
Bidirectional Middlewares are based on :class:`~bibble.util.middlecore.IdenBidiMiddleware`,
to provide :class:`~bibble.util.pair_stack.PairStack`'s with a tranform when reading a bibtex file,
and an equivalent reverse transform to undo it when writing.

For Example, :class:`~bibble.bidi.braces.BraceWrapper` provides unwrapping fields on read
(so ``entry.Field("title", "{This is an Example}")`` is transformed to
``entry.Field("title", "This is an Example")``), and then when writing the reverse occurs.

Where normal middlewares implement ``transform`` and ``transform_{type}`` methods,
bidirectional middlewares implement ``read_transform_{type}``
and ``write_transform_{type}`` methods.
So ``BraceWrapper`` implements ``read_transform_Entry`` and ``write_transform_Entry`` methods.

Meanwhile, when read and write middlewares are already implemented (eg: :class:`~bibble.metadata.isbn_writer.IsbnWriter` and :class:`~bibble.metadata.isbn_validator.IsbnValidator`), then the bidirectional version can be as simple as:

.. code:: python

    from bibble.util.middlecore import IdenBidiMiddleware
    from bibble.metadata import IsbnValidator, IsbnWriter
    
    class BidiIsbn(IdenBidiMiddleware):
    
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self._reader = IsbnValidator()
            self._writer = IsbnWriter()
    
        def read_transform_Entry(self, entry:Entry, library:Library) -> list[Entry]:
            return self._reader.transform_Entry(entry, library)
    
        def write_transform_Entry(self, entry:Entry, library:Library) -> list[Entry]:
            return self._writer.transform_Entry(entry, library)
