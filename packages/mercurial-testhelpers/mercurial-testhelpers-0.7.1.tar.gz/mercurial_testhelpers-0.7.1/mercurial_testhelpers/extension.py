# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Utilities for handling of extensions."""
import sys
from mercurial import pycompat

if pycompat.ispy3:
    # this raises ImportError on Python < 3.4 (way too old anyway for hg)
    from importlib.util import find_spec  # pragma: PY3
else:  # pragma: PY2
    import imp


def py3_module_found(dotted_name):
    """Tell whether Python can find the module, without importing it.
    """
    return find_spec(dotted_name) is not None  # pragma: PY3


def py2_module_found(dotted_name):  # pragma: PY2
    """Implementation of module_found() for Python 2

    Caveats:

    - for modules in packages, the current implementation will
      import the parent package if it's not already imported.
    - uses ``imp`` which may not implement the full finder/loader protocol
      of PEP 302.
    - tested with CPython only.

    References:
.
    https://docs.python.org/2/reference/simple_stmts.html#the-import-statement
    https://www.python.org/dev/peps/pep-0302/
    """
    if dotted_name in sys.modules:
        return True  # already imported

    split = dotted_name.rsplit('.', 1)
    mod_name = split[-1]

    if len(split) == 1:
        pkg_path = None
    else:
        pkg = __import__(split[0])
        for segment in split[0].split('.')[1:]:
            pkg = getattr(pkg, segment)
        pkg_path = pkg.__path__

    try:
        found = imp.find_module(mod_name, pkg_path)
    except ImportError:
        return False

    try:
        close_source = found[0].close
    except AttributeError:  # pragma: no cover  (don't know how to trigger)
        # file-like object not supposed to be closed
        pass
    else:
        # if this raises an exception, we'll want to know about it
        # and perhaps decide to ignore in a later version.
        close_source()

    return True


module_found = py3_module_found if pycompat.ispy3 else py2_module_found


def is_available(name):
    """Tell if an extension with given name available.

    :param name: must be `str` on Python 3

    Like the import logic in ``mercurial.extensions``, we look in the
    current ``hgext`` namespaces and fall back to direct importability of
    the given name.

    Since we don't really import the module of the extension, there is
    no guarantee that what was found is indeed a Mercurial extension.
    Collisions are probably more worrisome in case of fall back.
    """
    in_hgext_ns = any(module_found('.'.join((pkg, name)))
                      for pkg in ('hgext', 'hgext3rd'))
    return in_hgext_ns or module_found(name)
