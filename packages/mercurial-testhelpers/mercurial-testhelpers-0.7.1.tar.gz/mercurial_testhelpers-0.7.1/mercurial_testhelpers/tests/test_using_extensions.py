# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from __future__ import absolute_import
from mercurial import (
    extensions,
    pycompat,
    ui as uimod,
)
from ..repo_wrapper import RepoWrapper


SAMPLE_EXTENSION = """
"sample_ext docstring"

from mercurial import registrar

cmdtable = {}
command = registrar.command(cmdtable)

@command(b'thlp-extcmd')
def thlp_extcmd(ui, repo):
    return repo.root, ui.configitems(b'foo')
"""


def create_sample_extension(root_path):
    ext_path = root_path / 'sample_ext.py'
    ext_path.write(SAMPLE_EXTENSION)
    return str(ext_path)


def assert_sample_extension(wrapper, ext_name):
    exts = dict(extensions.extensions(wrapper.repo.ui))
    ext_module = exts.get(pycompat.sysbytes(ext_name))

    assert ext_module is not None
    assert ext_module.__doc__ == "sample_ext docstring"


def test_load_hgrc_extension(tmpdir):
    sample_ext_path = create_sample_extension(tmpdir)
    repo_path = tmpdir / 'repo'

    RepoWrapper.init(repo_path)
    repo_path.join('.hg', 'hgrc').write('\n'.join((
        "[extensions]",
        "sample_ext=" + sample_ext_path,
    )))
    wrapper = RepoWrapper.load(repo_path,
                               config=dict(foo=dict(bar='17')))

    assert_sample_extension(wrapper, 'sample_ext')
    assert wrapper.repo.ui.configint(b'foo', b'bar') == 17
    assert wrapper.command('thlp-extcmd') == (wrapper.repo.root,
                                              [(b'bar', b'17')])


def test_init_baseui_config_extension(tmpdir):
    sample_ext_path = create_sample_extension(tmpdir)
    ui = uimod.ui.load()
    ui.setconfig(b'foo', b'bar', b'yes', source=b'tests')
    ui.setconfig(b'extensions', b'foo_ext', pycompat.sysbytes(sample_ext_path),
                 source=b'tests')
    wrapper = RepoWrapper.init(tmpdir / 'repo', base_ui=ui)

    assert wrapper.repo.ui.configbool(b'foo', b'bar')
    assert_sample_extension(wrapper, 'foo_ext')
    assert wrapper.command('thlp-extcmd') == (wrapper.repo.root,
                                              [(b'bar', b'yes')])


def test_init_config_extension(tmpdir):
    sample_ext_path = create_sample_extension(tmpdir)

    ui = uimod.ui.load()
    ui.setconfig(b'foo', b'bar', b'yes', source=b'tests')
    wrapper = RepoWrapper.init(
        tmpdir,
        config=dict(foo=dict(bar='yes'),
                    extensions=dict(testext=sample_ext_path),
                    ))

    assert wrapper.repo.ui.configbool(b'foo', b'bar')
    assert_sample_extension(wrapper, 'testext')
    assert wrapper.command('thlp-extcmd') == (wrapper.repo.root,
                                              [(b'bar', b'yes')])
