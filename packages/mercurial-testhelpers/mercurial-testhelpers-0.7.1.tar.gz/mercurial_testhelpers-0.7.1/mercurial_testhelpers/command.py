# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from mercurial import (
    cmdutil,
    commands,
)
from .ui import make_ui
from .util import as_bytes


def command(name, *args, **kwargs):
    """Utility to call Mercurial commands.

    This saves a bit of boilerplate.

    :param name: name of the command, can be :class:`str` or :class:`bytes`
    :param ui: if specified, the :class:`mercurial.ui.ui` instance to run
       the command with. Otherwise a default one shall be created and used.
    """
    ui = kwargs.pop('ui', None)
    if ui is None:
        ui = make_ui(None)

    cmd = cmdutil.findcmd(as_bytes(name), commands.table)[1][0]
    return cmd(ui, *args, **kwargs)
