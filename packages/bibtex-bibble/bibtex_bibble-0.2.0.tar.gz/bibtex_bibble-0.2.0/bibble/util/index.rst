.. -*- mode: ReST -*-

.. _util:

====
Util
====

.. contents:: Contents
   :local:


The :class:`~bibble.util.pair_stack.PairStack` provides the logic for assembling unidirectional
and bidirectional middlewares into a `read_stack` and `write_stack`.
The main logic is the `read_stack` is `FIFO`, while the `write_stack` is `LIFO`.
Thus:

.. code:: python

   stack = PairStack()
   stack.add(Bidi_1)
   stack.add(read=[Mid_1], write=[Mid_2])
   stack.add(Bidi_2)


Would result in a read stack of ``[Bidi_1, Mid_1, Bidi_2]``,
while the write stack would be ``[Bidi_2, Mid_2, Bidi_1]``.
So the last transform applied when reading, is the first transform undone when writing.
