# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from ..command import command
from ..ui import make_ui
from mercurial import (
    ui as uimod,
    util,
)


def capture_ui_write(monkeypatch, records):
    """Helper to capture calls to `ui.write`.

    Needed because the standard stdout capture facilities in pytest
    (capsys fixture) fail to perform in that case.

    # TODO provide a generic facility in pytest-mercurial for ui.write capture
    """
    def write(ui, *args, **kwargs):
        records.append(args)

    monkeypatch.setattr(uimod.ui, 'write', write)


def join_out(captured):
    """Convert captured `ui.write` calls to a single bytes string"""
    return b''.join(arg for call in captured for arg in call)


def test_command_auto_ui(monkeypatch):
    captured = []
    capture_ui_write(monkeypatch, captured)

    command('version', template=b'{ver}')
    assert captured[0][0] == util.version()


def test_command_passed_ui(monkeypatch):
    captured = []
    capture_ui_write(monkeypatch, captured)

    # `hg version -q` does not output the copyright notice,
    # let's reproduce that in the prepared ui instance
    ui = make_ui(None, config=dict(ui=dict(quiet=True, debug=False)))
    command('version', ui=ui)
    assert b'copyright' not in join_out(captured).lower()
