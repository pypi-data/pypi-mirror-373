# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from ..extension import (
    is_available,
)


def test_available_core():
    # of course this will break if someday churn isn't an extension anymore
    # but that's a very easy fix
    assert is_available('churn')


def test_ext_available_third_party():
    # a good occasion to test that we severed all dependencies to
    # the 'heptapod' extension where these testhelpers originated
    # if this fails, rerun in a context where the heptapod extension
    # is not available if you can. If you can't, that's a bug.
    assert not is_available('heptapod')


def test_module_available(monkeypatch):
    """To complete the coverage, especially with Python2"""
    from ..extension import module_found

    assert not module_found('does_not_exist')
    assert not module_found('mercurial_testhelpers.does_not_exist')

    # already imported
    assert module_found(__name__)
    import sys

    # deeper level if the need arises
    assert not module_found('mercurial_testhelpers.tests.does_not_exist')

    monkeypatch.delitem(sys.modules, __name__)
    assert module_found(__name__)
