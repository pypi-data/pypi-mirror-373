.. pyexpander documentation master file, created by
   sphinx-quickstart on Wed Oct 12 15:41:21 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: logo_hzb_big.png
   :align: right
   :target: https://www.helmholtz-berlin.de

======================================
Welcome to pyexpander's documentation!
======================================

pyexpander - a powerful turing complete macro processor
=======================================================

pyexpander is a macro processor that allows to embed python code in text files.

Some of the features are:

- Variables like ``$(VAR)`` are replaced.
- Valid python expressions like ``$(2+3/2)`` are evaluated.
- Arbitrary python code like in ``$py(import math; math.pi)`` can be executed.
- The functionality is available as a script and a python library.

See :doc:`introduction` for more information.

:Author:
    Goetz Pfeiffer (Goetz.Pfeiffer@helmholtz-berlin.de, goetzpf@googlemail.com)

:Version:
    |version|

.. seealso::
   `Goetz Pfeiffer's Project site <https://goetzpf.github.io/>`_
   for other open source projects.

Documentation
=============

Introduction
------------

This gives a first impression on pyexpander's capabilities:

:doc:`Introduction to pyexpander <introduction>`

Reference documents
-------------------

This is the reference of the pyexpander language:

:doc:`pyexpander reference <reference-expander>`

Full list of documents
----------------------

.. toctree::
   :maxdepth: 1

   introduction
   reference-expander
   epics-support
   python3
   expander-options
   msi2pyexpander-options
   pyexpander-install
   source-code-documentation
   license


License and copyright
=====================

Copyright (c) 2025 by `Helmholtz-Zentrum Berlin <https://www.helmholtz-berlin.de>`_.

This software of this project can be used under GPL v.3, see :doc:`license`.

Download and install
====================

By using `pip <https://en.wikipedia.org/wiki/Pip_(package_manager)>`_, installing
pyexpander is a single line command. This and other installation methods
are described in

:doc:`Installing pyexpander <pyexpander-install>`

pyexpander at sourceforge
=========================

You find the sourceforge summary page for pyexpander at
`pyexpander <https://sourceforge.net/projects/pyexpander>`_.

The source
==========

You can browse the mercurial repository here:

`repository at Sourceforge <https://sourceforge.net/p/pyexpander/code/ci/default/tree/>`_.

or clone it with this command:

Sourceforge::

  hg clone http://hg.code.sf.net/p/pyexpander/code pyexpander-code

You can then commit changes in your own repository copy. 

If you plan to share these changes you can create a mercurial 
`bundle <https://www.mercurial-scm.org/help/commands/bundle>`_ and send it to my e-mail
address.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

