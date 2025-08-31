# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Helpers for datetime instance conversion to internal Mercurial format.

Also provides some uniformity between Python 2 and Python 3:

- ``timezone`` class for fixed offset time zones. Under Python 3, it's just
  reexposition of ``datetime.timezone``
"""
from __future__ import absolute_import
import attr
import calendar

try:
    from datetime import timezone
    py2 = False  # pragma: PY3
except ImportError:  # pragma: PY2
    py2 = True
    from datetime import timedelta, tzinfo

    @attr.s
    class timezone(tzinfo):
        offset = attr.ib()  # timedelta instance

        def utcoffset(self, _dt):
            return self.offset

    timezone.utc = timezone(timedelta(0))


class TimeZoneMissing(ValueError):
    pass


def timestamp_offset(dt):
    """Conversion of time zone aware datetime to timestamp and offset.

    :param dt: a time zone aware :class:`datetime` instance.
    :raises TimeZoneMissing: if ``dt`` is naive (not time zone aware)

    Note: according to
    https://docs.python.org/3/library/datetime.html#determining-if-an-object-is-aware-or-naive,
    the notion of naive :class:`datetime` instance includes cases where
    ``tzinfo`` is not ``None`` but still return a ``None`` offsets to UTC.
    """  # noqa (long URL)
    offset = dt.utcoffset()
    if offset is None:
        raise TimeZoneMissing(dt)

    # An alternative for the UTC timestamp part would be to substract a
    # `datetime` epoch constant, and return the seconds of the resulting
    # `timedelta`.
    # This could better guard against overflows, but we need the offset anyway.
    return (calendar.timegm(dt.utctimetuple()), -offset.seconds)
