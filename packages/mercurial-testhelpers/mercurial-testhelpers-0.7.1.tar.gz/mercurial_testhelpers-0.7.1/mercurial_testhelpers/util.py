# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later


def as_bytes(s):
    """Whether s is a path, an str, or bytes, return a bytes representation.

    Explicitely, the conversion to bytes is done in UTF-8, so that it cannot
    fail.

    If that doesn't suit your case, just encode your string or path
    before hand as needed.
    """
    if s is None:
        return None
    if isinstance(s, bytes):
        return s
    return str(s).encode('utf-8')
