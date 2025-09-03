Installing pyexpander
=====================

Parts of pyexpander
-------------------

pyexpander consists of scripts, python modules, documentation and configuration
files.

pyexpander is available on `pypi <https://pypi.python.org/pypi>`_, as a debian
or rpm package, as a tar.gz and zip file.

For `Nix <https://nixos.org/>`_, a `Flake <https://nixos.wiki/wiki/Flakes>`_
package was created by Mathis Laroche <ecomath360@gmail.com> which is
available `here <https://github.com/Ecoral360/pyexpander-flake>`_.

The following chapters describe how to install pyexpander.

Requirements
------------

pyexpander requires python version 3 or newer.

pyexpander is tested on `debian <https://www.debian.org>`_ and 
`Fedora <https://getfedora.org>`_ linux distributions but should run on all
linux distributions. It probably also runs on other flavours of unix, probably
even MacOS, but this is not tested.

It may run on windows, escpecially the `Cygwin <https://www.cygwin.com>`_
environment, but this is also not tested.

Install from pypi with pip
--------------------------

In order to install pyexpander with `pip <https://en.wikipedia.org/wiki/Pip_(package_manager)>`_, 
you use the command [1]_::

  pip3 install pyexpander

.. [1] Your version of pip may have a different name, e.g. "pip-3", "pip-3.2" or just "pip"

You find documentation for the usage of pip at `Installing Python Modules
<https://docs.python.org/3/installing/index.html#installing-index>`_.

Install from a debian package
-----------------------------

There are packages for some of the recent debian versions. In order to see
what debian version you use enter::

  cat /etc/debian_version

Download the package here:

* `pyexpander downloads at Sourceforge <https://sourceforge.net/projects/pyexpander/files/?source=navbar>`_

and install with::

  dpkg -i <PACKAGENAME>

The packages may with other debian versions or debian package based
distributions like ubuntu, but this is not tested. 

Install from a rpm package
--------------------------

There are packages for some of the recent fedora versions. 
In order to see what fedora version you use enter::

  cat /etc/fedora-release

Download the package here:

* `pyexpander downloads at Sourceforge <https://sourceforge.net/projects/pyexpander/files/?source=navbar>`_

and install with::

  rpm -ivh  <PACKAGENAME>

The packages may work with other fedora versions or rpm package based
distributions like, redhat, scientific linux or opensuse, but this was not
tested. 

Install from source
-------------------

You should do this only if it is impossible to use one of the methods described
above. 

Download the \*.tar.gz or \*.whl file here:

* `pyexpander downloads at Sourceforge <https://sourceforge.net/projects/pyexpander/files/?source=navbar>`_

Install with::

  pip install <FILENAME>

For more information in `pip` and installing python modules see
`Installing Python Modules
<https://docs.python.org/3/installing/index.html#installing-index>`_.

