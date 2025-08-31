# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import re
from .. import exclude_regexps


def is_excluded(regexps, comment):
    return any(re.search(rx, comment) is not None for rx in regexps)


def test_exclude_regexps():
    # this test reasons like the code, that is not very convincing
    excl_4_7 = exclude_regexps(4, 7)
    assert r'hg<[=]?4\.0' in excl_4_7
    assert r'hg=4\.7' not in excl_4_7
    assert r'hg<4\.7' in excl_4_7


def test_excluded():
    # trying not to reason like the code.
    regexps = exclude_regexps(4, 7)
    assert is_excluded(regexps, 'hg<4.6')
    assert not is_excluded(regexps, 'hg<4.8')
    assert not is_excluded(regexps, 'hg>=4.5')
    assert not is_excluded(regexps, 'hg==4.7')
    assert is_excluded(regexps, 'hg>4.7')
    assert is_excluded(regexps, 'hg>=4.8')
    assert is_excluded(regexps, 'hg>5.1')
    assert is_excluded(regexps, 'hg>=5.2')
    assert is_excluded(regexps, 'hg>4.7')
    assert is_excluded(regexps, 'hg>=6.0')


def test_excluded_6_0():
    # trying not to reason like the code.
    regexps = exclude_regexps(6, 0)
    assert is_excluded(regexps, 'hg<4.6')
    assert is_excluded(regexps, 'hg<6.0')
    assert not is_excluded(regexps, 'hg==6.0')
    assert not is_excluded(regexps, 'hg>5.3')
