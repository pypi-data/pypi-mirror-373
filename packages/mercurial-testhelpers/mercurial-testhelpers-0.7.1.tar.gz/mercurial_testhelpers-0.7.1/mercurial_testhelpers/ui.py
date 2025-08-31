# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import os
from mercurial import (
    ui as uimod,
)

from .util import as_bytes


def make_ui(base_ui, config=None):
    """Create a ui instance, applying the given configuration.

    :param config: the given configuration is a nested :class:`dict`.
       Its keys are section names and values are themselves :class:`dict`
       for the section content.

       All section names and config item names and values can be passed
       either as string-like or bytes-like objects. They do not undergo
       conversion in the latter case.

    Unless specified otherwise, the ``ui.debug`` setting is activated,
    so that user messages are tested all the way.
    With the default settings of the :class:`ui` class, some output methods
    (e.g, :meth:`ui.note`) don't do anything (early return),
    with the consequence that feeding inappropriate arguments to these methods
    would not be detected by the tests.
    """
    # let's make sure we aren't polluted by surrounding settings
    os.environ['HGRCPATH'] = ''
    if base_ui is None:
        ui = uimod.ui.load()
    else:
        ui = base_ui.copy()

    # with load(), ui.environ is encoding.environ, with copy() it's not copied
    # we need the environ to be unique for each test to avoid side effects.
    # Also, on Python 2, encoding.environ is os.environ, leading to even
    # worse side effects.
    ui.environ = dict(ui.environ)

    ui.setconfig(b'ui', b'debug', b'yes')

    if config is not None:
        for section_name, section in config.items():
            for item_name, item_value in section.items():
                ui.setconfig(as_bytes(section_name),
                             as_bytes(item_name),
                             as_bytes(item_value),
                             source=b'tests')
    return ui
