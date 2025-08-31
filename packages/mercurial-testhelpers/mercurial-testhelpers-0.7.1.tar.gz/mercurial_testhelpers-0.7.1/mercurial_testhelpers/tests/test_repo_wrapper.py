# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from __future__ import absolute_import
from datetime import (
    datetime,
    timedelta,
)
from mercurial import (
    error,
    phases,
    ui as uimod,
)
import pytest
import time

from ..repo_wrapper import (
    RepoWrapper,
    as_bytes,
    NULL_ID,
    NULL_REVISION,
    timezone,
)

parametrize = pytest.mark.parametrize


def test_init_commit_file(tmpdir):
    wrapper = RepoWrapper.init(tmpdir)
    assert wrapper.path is tmpdir

    node = wrapper.commit_file('foo', content='Foo', message='Foo committed')
    ctx = wrapper.repo[node]
    assert ctx.description() == b'Foo committed'
    parents = ctx.parents()
    assert len(parents) == 1
    assert parents[0].rev() == NULL_REVISION
    assert parents[0].node() == NULL_ID

    del wrapper, ctx

    reloaded = RepoWrapper.load(tmpdir)
    assert reloaded.path is tmpdir

    rl_ctx = reloaded.repo[node]
    assert rl_ctx.description() == b'Foo committed'


def test_config(tmpdir):
    wrapper = RepoWrapper.init(tmpdir,
                               config=dict(ui=dict(username='Someone')))
    assert wrapper.config('unknown', 'item') is None
    assert wrapper.config('ui', 'username') == b'Someone'
    assert wrapper.config('ui.username') == b'Someone'
    assert wrapper.repo.ui.config(b'ui', b'username') == b'Someone'

    wrapper.setconfig('ui', 'username', 'Else')
    assert wrapper.config('ui', 'username') == b'Else'
    assert wrapper.repo.ui.config(b'ui', b'username') == b'Else'

    # sub options
    wrapper.setconfig('experimental', 'foo', 'main')
    wrapper.setconfig('experimental', 'foo:bar', '2')
    wrapper.setconfig('experimental', 'foo:baz', '3')
    expected = (b'main', {b'bar': b'2', b'baz': b'3'})
    assert wrapper.configsuboptions('experimental', 'foo') == expected
    assert wrapper.config_sub_options('experimental', 'foo') == expected

    # paths (using tmpdir for convenience as a Path-like object
    # lying around, even under Python 2)
    wrapper.setconfig('foo', 'bar', 'file', source=tmpdir / 'hgrc:section')
    expected = as_bytes(tmpdir / 'file')
    assert wrapper.configpath('foo', 'bar') == expected
    assert wrapper.config_path('foo', 'bar') == expected

    # booleans
    wrapper.setconfig('experimental', 'foo', 'yes')
    assert wrapper.configbool('experimental', 'foo')
    assert wrapper.config_bool('experimental', 'foo')
    wrapper.setconfig('experimental', 'foo', '0')
    assert not wrapper.configbool('experimental', 'foo')
    assert not wrapper.config_bool('experimental', 'foo')

    # generic conversion
    wrapper.setconfig('experimental', 'foo', '6.4')
    expected = 6.4
    wrapper.configwith(float, 'experimental', 'foo') == expected
    wrapper.config_with(float, 'experimental', 'foo') == expected

    # integers
    wrapper.setconfig('experimental', 'foo', '12')
    assert wrapper.configint('experimental', 'foo') == 12
    assert wrapper.config_int('experimental', 'foo') == 12

    # (number of) bytes
    wrapper.setconfig('experimental', 'foo', '1 MB')
    expected = 1 << 20
    assert wrapper.configbytes('experimental', 'foo') == expected
    assert wrapper.config_bytes('experimental', 'foo') == expected

    # lists
    wrapper.setconfig('experimental', 'foo', 'bar, baz')
    expected = [b'bar', b'baz']
    assert wrapper.configlist('experimental', 'foo') == expected
    assert wrapper.config_list('experimental', 'foo') == expected

    # dates
    wrapper.setconfig('experimental', 'foo', "2020-12-6 13:18 -0600")
    expected = (1607282280, 21600)
    assert wrapper.configdate('experimental', 'foo') == expected
    assert wrapper.config_date('experimental', 'foo') == expected

    # byte strings are supported in all arguments, of course
    wrapper.setconfig('ui', 'username', b"Rapha\xebl")
    assert wrapper.config('ui', 'username') == b"Rapha\xebl"
    wrapper.setconfig(b'f\xf8o', 'bar', 'yes')
    assert wrapper.config(b'f\xf8o', 'bar') == b'yes'
    assert wrapper.configbool(b'f\xf8o', 'bar')

    wrapper.setconfig(b'foo', b'r\xe9ussi', 'oui')
    assert wrapper.config(b'foo', b'r\xe9ussi') == b'oui'

    # default values
    if getattr(uimod.ui, 'configdefault', None) is not None:  # hg>5.1
        assert wrapper.configdefault('phases', 'publish') is True
        assert wrapper.config_default('phases', 'publish') is True

    # config item presence
    wrapper.setconfig('experimental', 'foo', "bar")
    assert wrapper.hasconfig('experimental.foo')
    assert wrapper.hasconfig('experimental', 'foo')
    assert wrapper.has_config('experimental.foo')
    assert not wrapper.hasconfig('experimental.bar')

    # has_section
    assert wrapper.config_has_section('ui')
    assert not wrapper.config_has_section('in-your-dreams')

    # items
    wrapper.setconfig('mysection', 'bar', 'hop')
    expected = [(b'bar', b'hop')]
    assert wrapper.config_items('mysection') == expected
    assert wrapper.configitems('mysection') == expected

    # fully dotted name in setconfig()
    wrapper.setconfig('ui.username', "Lazy Tester")
    assert wrapper.config('ui', 'username') == b'Lazy Tester'
    assert wrapper.config('ui.username') == b'Lazy Tester'

    # deeper fully dotted names
    wrapper.setconfig('experimental.foo.bar', 'yes')
    assert wrapper.config('experimental.foo.bar') == b'yes'
    assert wrapper.repo.ui.config(b'experimental', b'foo.bar') == b'yes'
    assert wrapper.config('experimental', 'foo.bar') == b'yes'
    assert wrapper.configbool('experimental', 'foo.bar')

    for invalid_args in (('no-value', ),
                         ('experimental', 'foo', 'bar', False),
                         ):
        with pytest.raises(TypeError):
            wrapper.setconfig(*invalid_args)

    for invalid_args in ((),
                         ('experimental', 'foo', 'bar'),
                         ):
        with pytest.raises(TypeError):
            wrapper.config(*invalid_args)


def test_update(tmpdir):
    wrapper = RepoWrapper.init(tmpdir)
    wrapper.commit_file('foo', content='Foo 0')
    node1 = wrapper.commit_file('foo', content='Foo 1', return_ctx=False)
    foo = tmpdir.join('foo')
    assert foo.read() == 'Foo 1'

    wrapper.update('0')
    assert foo.read() == 'Foo 0'

    wrapper.update_bin(NULL_ID)
    assert not foo.isfile()

    wrapper.update_bin(node1)
    assert foo.read() == 'Foo 1'


@parametrize('meth', ['class', 'instance'])
def test_share(tmpdir, meth):
    main_path = tmpdir.join('main')
    dest_path = tmpdir.join('dest')
    main_wrapper = RepoWrapper.init(main_path)
    node0 = main_wrapper.commit_file('foo', message='Done in main')

    if meth == 'class':
        dest_wrapper = RepoWrapper.share_from_path(main_path, dest_path)
    else:
        dest_wrapper = main_wrapper.share(dest_path)

    assert dest_wrapper.path is dest_path

    dest_ctx = dest_wrapper.repo[node0]
    assert dest_ctx.description() == b'Done in main'

    node1 = dest_wrapper.commit_file(
        'foo', message='Done in dest', parent=node0)

    # we need to reload the main repo to see the new changeset
    reloaded = RepoWrapper.load(main_path)
    main_ctx = reloaded.repo[node1]
    assert main_ctx.description() == b'Done in dest'


def test_commit(tmpdir):
    """Demonstrates message auto generation and how to commit several files."""
    wrapper = RepoWrapper.init(tmpdir)
    (tmpdir / 'foo').write('foo')
    (tmpdir / 'bar').write('bar')
    ctx0 = wrapper.commit(('foo', 'bar'), add_remove=True)
    assert set(ctx0.files()) == {b'foo', b'bar'}


def test_commit_file_named_branch(tmpdir):
    """Demonstrate the use of commit_file with parent."""
    wrapper = RepoWrapper.init(tmpdir)
    ctx0 = wrapper.commit_file('foo', content='Foo 0')
    wrapper.commit_file('foo', content='Foo 1')
    ctxbr = wrapper.commit_file('foo', content='Foo branch',
                                parent=ctx0, branch='other')

    assert ctxbr.branch() == b'other'
    assert ctxbr.parents() == [ctx0]


def test_commit_file_parent_nodeid(tmpdir):
    """Demonstrate the use of commit_file with parent given as node id"""
    wrapper = RepoWrapper.init(tmpdir)
    node0 = wrapper.commit_file('foo', content='Foo 0', return_ctx=False)
    assert isinstance(node0, bytes)  # avoid tautologies

    wrapper.commit_file('foo', content='Foo 1')
    ctxbr = wrapper.commit_file('foo', content='Foo branch',
                                parent=node0, branch='other')

    assert ctxbr.branch() == b'other'
    assert [c.node() for c in ctxbr.parents()] == [node0]


def test_commit_file_time(tmpdir):
    """Demonstrate the utc_timestamp optional parameter."""
    wrapper = RepoWrapper.init(tmpdir)
    ctx = wrapper.commit_file('foo', content='Foo', utc_timestamp=123456)
    assert ctx.date() == (123456.0, 0)

    # floats are accepted, but get truncated
    ctx = wrapper.commit_file('foo', content='Foo2', utc_timestamp=12.34)
    assert ctx.date() == (12.0, 0)

    # tz_timestamp allows to record the time zone
    ctx = wrapper.commit_file('foo', content='Foo3',
                              tz_timestamp=(123456, -7200))  # UTC+2
    assert ctx.date() == (123456.0, -7200)

    # utc_datetime accepts a naive datetime and interprets it as UTC
    ctx = wrapper.commit_file('foo', content='Foo4',
                              utc_datetime=datetime(2020, 12, 1, 12, 34, 0))
    assert ctx.date() == (1606826040.0, 0)  # manually checked with hg log

    french_summer = timezone(timedelta(hours=2))  # UTC+2

    # time zones are not accepted with `utc_datetime`
    with pytest.raises(ValueError):
        wrapper.commit_file('whatever',
                            utc_datetime=datetime(2020, 12, 1, 12, 34, 0,
                                                  tzinfo=french_summer))

    # tz_datetime accepts timezone aware datetime instances
    ctx = wrapper.commit_file('foo', content='Foo5',
                              tz_datetime=datetime(2020, 12, 1, 14, 34, 0,
                                                   tzinfo=french_summer))
    assert ctx.date() == (1606826040.0, -7200)  # manually checked with hg log
    ctx = wrapper.commit_file('foo', content='Foo6',
                              tz_datetime=datetime(2020, 12, 1, 12, 34, 0,
                                                   tzinfo=timezone.utc))
    assert ctx.date() == (1606826040.0, 0)  # manually checked with hg log

    # and refuses naive datetime instances
    with pytest.raises(ValueError):
        wrapper.commit_file('whatever',
                            tz_datetime=datetime(2020, 12, 1, 12, 34, 0))


def test_commit_file_parent(tmpdir):
    """Demonstrate the use of commit_file with parent"""
    wrapper = RepoWrapper.init(tmpdir)
    ctx0 = wrapper.commit_file('foo', content='Foo 0')
    wrapper.commit_file('foo', content='Foo 1')
    ctxbr = wrapper.commit_file('foo', content='Foo branch',
                                parent=ctx0)

    assert ctxbr.branch() == b'default'
    assert ctxbr.parents() == [ctx0]


def test_commit_file_random(tmpdir):
    """Demonstrate how random content is generated."""

    wrapper = RepoWrapper.init(tmpdir)
    node0 = wrapper.commit_file('foo')
    ctx1 = wrapper.commit_file('foo', parent=node0, return_ctx=True)
    ctx2 = wrapper.commit_file('foo', parent=node0, return_ctx=True)

    assert ctx1.p1() == ctx2.p1()
    assert ctx1 != ctx2


def test_phase(tmpdir):
    wrapper = RepoWrapper.init(tmpdir)
    node = wrapper.commit_file('foo', content='Foo 0')
    ctx = wrapper.repo[node]
    assert ctx.phase() == phases.draft

    wrapper.set_phase('public', ['.'], force=False)
    assert ctx.phase() == phases.public

    wrapper.set_phase('draft', ['.'], force=True)
    assert ctx.phase() == phases.draft


@parametrize('msg_kind', ('no-message', 'explicit-message'))
def test_remove_file(tmpdir, msg_kind):
    wrapper = RepoWrapper.init(tmpdir)
    wrapper.commit_file('foo', content='bar')
    assert tmpdir.join('foo').read() == 'bar'

    if msg_kind == 'no-message':
        passed_msg, expected_msg = (None, b'removing foo')
    else:
        passed_msg, expected_msg = ('explicit', b'explicit')

    ctx = wrapper.commit_removal('foo', message=passed_msg)
    assert ctx.description() == expected_msg
    assert b'foo' not in ctx
    assert b'foo' in ctx.p1()
    assert not tmpdir.join('foo').exists()


def test_write_local_hrc(tmpdir):
    writer = RepoWrapper.init(tmpdir)
    writer.write_hgrc({'xp': dict(foo='bar', bin=b'\xe9'),
                       b'risqu\xe9': {b'fo\xfb': 'yes'}})
    assert writer.repo.vfs.exists(path=b'hgrc')

    reader = RepoWrapper.load(tmpdir)
    assert set(reader.config_items('xp')) == {(b'foo', b'bar'),
                                              (b'bin', b'\xe9')}
    assert reader.config_items(b'risqu\xe9') == [(b'fo\xfb', b'yes')]


def test_empty_changeset(tmpdir):
    wrapper = RepoWrapper.init(tmpdir)
    root_ctx = wrapper.commit_file('foo', content='bar')

    ctx = wrapper.commit_empty(branch='new', message='empty')
    assert ctx.branch() == b'new'
    assert ctx.description() == b'empty'

    ctx = wrapper.commit_empty(branch='other', message='again',
                               parent=root_ctx)
    assert ctx.branch() == b'other'
    assert ctx.description() == b'again'


def test_extensibility_commit(tmpdir):
    class MyWrapper(RepoWrapper):
        def mark_repo(self, marker):
            self.repo.test_marker = marker

    MyWrapper.register_commit_option('mark', 'mark_repo')

    # registration worked, without side effects on the parent class
    assert 'mark' in MyWrapper.commit_option_handlers
    assert 'mark' not in RepoWrapper.commit_option_handlers

    wrapper = MyWrapper.init(tmpdir)
    ctx = wrapper.commit_file('foo', content='bar', mark="extended!")

    # mark_repo() was called as expected
    assert wrapper.repo.test_marker == 'extended!'

    # commit looks normal
    assert (tmpdir / 'foo').read() == 'bar'
    assert ctx.files() == [b'foo']


@parametrize('datetime_opt', ('no-datetime', 'tz-datetime'))
@parametrize('message', ('auto-msg', 'str-msg'))
def test_merge_commit(tmpdir, datetime_opt, message):
    wrapper = RepoWrapper.init(tmpdir)
    ctx0 = wrapper.commit_file('foo', content='foo')
    ctx1 = wrapper.commit_file('bar', content='bar')
    ctx2 = wrapper.commit_file('zoo', content='zoo', parent=ctx0,
                               branch='stable')
    wrapper.update(ctx1.rev())

    opts = {}
    if datetime_opt == 'tz-datetime':
        french_summer = timezone(timedelta(hours=2))  # UTC+2
        opts['tz_datetime'] = datetime(2020, 12, 1, 14, 34, 0,
                                       tzinfo=french_summer)
    else:
        opts['utc_timestamp'] = time.time()

    if message == 'auto-msg':
        # deemed preferable than using `None` directly in parametrization
        # because `auto-msg` is more understandable in `pytest -v` output
        message = None

    merge_ctx = wrapper.merge_commit(ctx=ctx2,
                                     user='testuser',
                                     message=message,
                                     **opts)

    assert merge_ctx.parents() == [ctx1, ctx2]
    assert merge_ctx.user() == b'testuser'
    if message == 'str-msg':
        assert merge_ctx.description() == b'str-msg'
    if datetime_opt == 'tz-datetime':
        # same as in test_commit_file_time
        assert merge_ctx.date() == (1606826040.0, -7200)


def test_merge_commit_change_branch_user_config(tmpdir):
    wrapper = RepoWrapper.init(tmpdir,
                               config=dict(ui=dict(username=b'testuser')))

    ctx0 = wrapper.commit_file('foo', content='foo')
    ctx1 = wrapper.commit_file('bar', content='bar')
    ctx2 = wrapper.commit_file('zoo', content='zoo', parent=ctx0,
                               branch='feature')
    wrapper.update(ctx1.rev())
    merge_ctx = wrapper.merge_commit(ctx2, branch='merged')

    assert merge_ctx.parents() == [ctx1, ctx2]
    assert merge_ctx.branch() == b'merged'
    assert merge_ctx.user() == b'testuser'


def test_reload(tmpdir):
    wrapper1 = RepoWrapper.init(tmpdir / 'source')
    wrapper2 = RepoWrapper.load(wrapper1.path,
                                config=dict(foo=dict(something='great')))
    wrapper1.commit_file('README')

    repo2 = wrapper2.repo
    # We need repo2 to actually read some data for reload to be necessary
    repo2[0]

    ctx = wrapper1.commit_file('README', content="Not seen in wrapper2")
    with pytest.raises(error.RepoLookupError):
        # ensure test relevance
        seen_from_repo2 = repo2[1]
        if seen_from_repo2.node() == NULL_ID:  # hg<4.8
            raise error.RepoLookupError(
                b"Unknown rev, "
                b"raised directly from test to give old hg a hand")

    wrapper2.reload()
    assert wrapper2.repo[1].hex() == ctx.hex()
    assert wrapper2.repo.ui.config(b'foo', b'something') == b'great'

    # Users should be aware of this:
    assert wrapper2.repo is not repo2
