# Copyright 2019-2023 Georges Racinet <georges.racinet@octobus.net>
# Copyright 2024 Georges Racinet <georges.racinet@cloudcrane.io>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Helpers for automatic tests.

These allow both high level operation on testing repos, and lower level
calls and introspections, making it possible to test more exhaustively inner
code paths that with `.t` tests, which are really functional tests.
"""
import functools
import os
from mercurial import (
    cmdutil,
    hg,
    node,
    phases,
    pycompat,
)
from mercurial.util import versiontuple
import random
import time

from .command import command
from .datetime import (
    TimeZoneMissing,
    timestamp_offset,
    timezone,
)
from .util import as_bytes
from .ui import make_ui

# re-exports for stability
NULL_REVISION = node.nullrev  # pragma: no cover
NULL_ID = node.nullid

try:
    phase_names = phases.cmdphasenames
except AttributeError:  # hg<4.8
    phase_names = phases.phasenames[:3]

MERCURIAL_VERSION = versiontuple()


def _config_key_args(args):
    """Convert arguments to bytes and take care of full dotted notation.

    :return: `(section, name)`, as :class:`bytes`
    """
    args = tuple(as_bytes(arg) for arg in args)
    argl = len(args)
    if argl == 2:
        return args
    elif argl == 1:
        return args[0].split(b'.', 1)

    raise ValueError('nbargs')


def configreader(reader):

    @functools.wraps(reader)
    def wrapped(repo_wrapper, *args, **kw):
        try:
            section, name = _config_key_args(args)
        except ValueError:
            raise TypeError(
                "RepoWrapper config reader methods require one "
                "('section.name') or two ('section', 'name') "
                "positional arguments.")
        return reader(repo_wrapper, section, name, **kw)

    return wrapped


def convert_date_times(tz_timestamp=None,
                       utc_timestamp=None,
                       utc_datetime=None,
                       tz_datetime=None,
                       ):
    if tz_timestamp is not None:
        return tz_timestamp
    if utc_timestamp is not None:
        return (utc_timestamp, 0)

    if tz_datetime is not None:
        try:
            return timestamp_offset(tz_datetime)
        except TimeZoneMissing:
            raise ValueError("tz_datetime must have time zone information")

    if utc_datetime is not None:
        if utc_datetime.tzinfo is not None:
            raise ValueError(
                "utc_datetime must not come with time zone information. "
                "Use tz_datetime for time zone aware datetimes, even if "
                "the time zone is UTC.")
        return timestamp_offset(utc_datetime.replace(tzinfo=timezone.utc))

    return (time.time(), 0)


class RepoWrapper(object):
    """Facilities for handling Mercurial repositories.

    As the name suggests, this is a wrapper class that embeds an
    instance of :class:`mercurial.localrepo.localrepo` as :attr:`repo`.

    It provides helper methods for initialization and content creation or
    mutation, both in the working directory and in changesets.

    For convenience, these high level methods accept both unicode and bytes
    strings. The path objects used by pytest can be used readily where
    a path is expected. There is one notable exception to this principle:
    the generic :meth:`command`, which is designed to forward its arguments
    to the underlying Mercurial command directly.

    All return values that are from Mercurial are untouched, hence strings
    would be bytes.

    All conversions to bytes are done with the UTF-8 codec. If that doesn't
    suit your case, simply encode your strings before hand.

    Running unmodified tests based on this helper on a non UTF-8 filesystem
    is not supported at this point, but it could be done, we are open to
    suggestions.
    """

    def __init__(self, repo, path):
        self.repo = repo
        # under Python 3 we could just normalize to pathlib.Path object
        # from repo.root but under Python 2, we cannot, and we cannot
        # make any assumptions on available high-level facilities, such
        # as ``py.path`` (provided by ``pytest``).
        self.path = path

    @classmethod
    def init(cls, path, base_ui=None, config=None):
        """Create the repository on disk at given path and return wrapper.

        :param path: can be :class:`str`, :class:`bytes` or any path-like
            object. The :attr:`path` attribute on the resulting wrapper
            is the given path, without any conversion.
        :param config: same structure and automatic conversions to
            :class:`bytes` as the ``config`` argument of :func:`ui.make_ui`.
        """
        ui = make_ui(base_ui, config)

        pathb = as_bytes(path)
        command('init', ui=ui, dest=pathb)
        return cls(hg.repository(ui, pathb), path)

    @classmethod
    def load(cls, path, base_ui=None, config=None):
        """Return a wrapper for the repository existing on disk at given path.

        :param path: can be :class:`str`, :class:`bytes` or any path-like
            object. The :attr:`path` attribute on the resulting wrapper
            is the given path, without any conversion.
        :param config: same structure and automatic conversions to
            :class:`bytes` as the ``config`` argument of :func:`ui.make_ui`.
        """
        ui = make_ui(base_ui, config=config)
        return cls(hg.repository(ui, as_bytes(path)), path)

    def reload(self):
        self.repo = hg.repository(self.repo.ui, as_bytes(self.path))

    @classmethod
    def share_from_path(cls, src_path, dest_path,
                        ui=None, base_ui=None, config=None,
                        **share_opts):
        """Create a new repo as the ``share`` command would do.

        :param ui: if specified, will be copied and used for the new repo
                   creation through ``share``
        :param config: only if ``ui`` is not specified, will be used to
                       create a new ``ui`` instance
        :param base_ui: only if ``ui`` is not specified, will be used to
                       create a new :class:`ui` instance
        :param share_opts: passed directly to :func:`hg.share()`
        :return: wrapper for the new repo, with :attr:`path` attribute the
           given `dest_path`
        """
        if ui is None:
            ui = make_ui(base_ui, config=config)
        else:
            # TODO not enough for environ independence
            ui = ui.copy()

        # the 'share' command defined by the 'share' extension, is just a thin
        # wrapper around `hg.share()`, which furthermore returns a repo object.
        repo = hg.share(ui, as_bytes(src_path), dest=as_bytes(dest_path),
                        **share_opts)
        if repo is None:
            return cls.load(dest_path)  # hg<=4.3
        return cls(repo, dest_path)  # hg>4.3

    def share(self, dest_path, **share_opts):
        return self.share_from_path(self.repo.root, dest_path,
                                    ui=self.repo.ui, **share_opts)

    def command(self, name, *args, **kwargs):
        repo = self.repo
        kwargs['ui'] = repo.ui
        return command(name, repo, *args, **kwargs)

    def setconfig(self, *args, **kwargs):
        """Shortcut to set config on the wrapped repo.

        Provides automatic conversion to :class:`bytes` of all
        arguments that need it.

        The fully dotted notation is also supported. Namely,
        these are equivalent::

            wrapper.setconfig('experimental.foo.bar', value)
            wrapper.setconfig('experimental', 'foo.bar', value)
        """
        try:
            section, name = _config_key_args(args[:-1])
        except ValueError:
            raise TypeError("RepoWrapper.setconfig requires two "
                            "('section.name', 'value') or three "
                            "('section', 'name', 'value') positional "
                            "arguments.")

        value = as_bytes(args[-1])
        source = as_bytes(kwargs.get('source', b''))
        self.repo.ui.setconfig(section, name, value, source=source)

    set_config = setconfig

    @configreader
    def config(self, section, name, **kwargs):
        """Return the plain string version of a config.

        Does not provide a default value system, as this is probaly
        useless for test assertions.

        The returned value is not converted to :class:`bytes`, for
        consistency with other values returned from `hg`.

        The fully dotted notation is also supported. Namely,
        these are equivalent::

            wrapper.config('experimental.foo.bar')
            wrapper.config('experimental', 'foo.bar')
        """
        return self.repo.ui.config(section, name, **kwargs)

    @configreader
    def configsuboptions(self, section, name, **kwargs):
        return self.repo.ui.configsuboptions(section, name, **kwargs)
    config_sub_options = configsuboptions

    @configreader
    def configpath(self, section, name, **kwargs):
        return self.repo.ui.configpath(section, name, **kwargs)
    config_path = configpath

    @configreader
    def configbool(self, section, name, **kwargs):
        return self.repo.ui.configbool(section, name, **kwargs)
    config_bool = configbool

    def configwith(self, convert, *args, **kwargs):
        @configreader
        def inner(self, section, name, **kwargs):
            return self.repo.ui.configwith(convert, section, name, **kwargs)

        return inner(self, *args, **kwargs)
    config_with = configwith

    @configreader
    def configint(self, section, name, **kwargs):
        return self.repo.ui.configint(section, name, **kwargs)
    config_int = configint

    @configreader
    def configbytes(self, section, name, **kwargs):
        return self.repo.ui.configbytes(section, name, **kwargs)
    config_bytes = configbytes

    @configreader
    def configlist(self, section, name, **kwargs):
        return self.repo.ui.configlist(section, name, **kwargs)
    config_list = configlist

    @configreader
    def configdate(self, section, name, **kwargs):
        return self.repo.ui.configdate(section, name, **kwargs)
    config_date = configdate

    @configreader
    def configdefault(self, section, name, **kwargs):  # hg>5.1
        return self.repo.ui.configdefault(section, name, **kwargs)
    config_default = configdefault

    @configreader
    def hasconfig(self, section, name, **kwargs):
        return self.repo.ui.hasconfig(section, name, **kwargs)
    has_config = hasconfig

    def config_has_section(self, section, **kwargs):
        return self.repo.ui.has_section(as_bytes(section), **kwargs)

    def configitems(self, section, **kwargs):
        return self.repo.ui.configitems(as_bytes(section), **kwargs)
    config_items = configitems

    def write_hgrc(self, config_dict):
        """Write the given configuration to the repo hgrc file.

        In cases the repository has to be reloaded, possibly from another
        code path or even another process, it is useful to store some wanted
        configuration in the local hgrc file (usually `.hg/hgrc`).

        :param config_dict: same structure and automatic conversions to
            :class:`bytes` as the ``config`` argument of :func:`ui.make_ui`.
        """
        linesep = pycompat.oslinesep
        with self.repo.vfs(b'hgrc', mode=b'wb') as hgrcf:
            for section, content in config_dict.items():
                hgrcf.write(b'[%s]' % as_bytes(section) + linesep)
                hgrcf.write(
                    linesep.join((
                        b'%s = %s' % (as_bytes(key), as_bytes(value))
                        for key, value in content.items()
                    )))
                hgrcf.write(linesep * 2)

    def random_content(self):
        return "random: {}\n\nparent: {}\n".format(
            random.random(),
            node.hex(self.repo.dirstate.p1()))

    def prepare_wdir(self, parent=None):
        if parent is not None:
            if isinstance(parent, bytes):
                self.update_bin(parent)
            else:
                self.update(parent.hex())

    def set_dirstate_branch(self, branch):
        if MERCURIAL_VERSION >= (6, 7):
            # transaction argument of `setbranch` is used to register
            # hooks for rollback, it is harmless to just pass `None`
            self.repo.dirstate.setbranch(as_bytes(branch), None)  # hg>=6.7
        else:
            self.repo.dirstate.setbranch(as_bytes(branch))  # hg<6.7

    commit_option_handlers = dict(branch='set_dirstate_branch',
                                  )

    @classmethod
    def register_commit_option(cls, name, handler):
        super_registry = super(cls, cls).commit_option_handlers
        registry = cls.commit_option_handlers
        if registry is super_registry:
            registry = cls.commit_option_handlers = super_registry.copy()

        registry[name] = handler

    def commit(self, rel_paths,
               message=None,
               user=None,
               utc_timestamp=None,
               tz_timestamp=None,
               utc_datetime=None,
               tz_datetime=None,
               add_remove=False, return_ctx=True, **opts):
        """Commit the current state of working directory.

        This method does not perform any update nor does it change the dirstate
        before committing. See :meth:`prepare_wdir` for helpers about that.

        If no time information is provided, the current UTC time is used.

        :param rel_paths: any iterable of relative paths from the repository
           root. Each can be specified as :class:`str` or :class:`bytes`
        :param message: commit message. If not specified, a randomized value
           is used.
        :param user: full user name and email, as in ``ui.username`` config
                     option. Can be :class:`str` or :class:`bytes`
        :param tz_timestamp: (timestamp, offset) where timestamp is seconds
            since the UNIX epoch and offset (seconds) is what has to be
            added to times of the time zone to get UTC values. This is the
            same as Mercurial internal representation format and goes straight
            to the commit. Floats can be provided but will be truncated to
            seconds anyway.

            Has the highest precedence.
        :param utc_timestamp: seconds since Epoch UTC. Can be float (only
            seconds will be kept).

            Has the second-most precedence.
        :param tz_datetime: a :class:`datetime` with mandatory time zone
            information.

            Has the third-most precedence.
        :param utc_datetime: a :class:`datetime` instance with ``tzinfo=None``.
            Will be interpreted as UTC.

            Has the lowest precedence.
        :param return_ctx: if ``True``, returns a :class:`changectx` instance
                           and a binary node id otherwise, which can be more
                           straightforward and faster in some cases.
        :returns: :class:`changectx` instance or binary node id for the
                  generated commit, according to ``return_ctx``.
        """
        repo = self.repo

        if user is None:
            user = repo.ui.config(b'ui', b'username')

        if message is None:
            message = self.random_content()

        tz_timestamp = convert_date_times(tz_timestamp=tz_timestamp,
                                          utc_timestamp=utc_timestamp,
                                          utc_datetime=utc_datetime,
                                          tz_datetime=tz_datetime,
                                          )

        def commitfun(ui, repo, message, match, opts):
            return repo.commit(message,
                               as_bytes(user),
                               tz_timestamp,
                               match=match,
                               editor=False,
                               extra=None,
                               )

        for opt, opt_value in opts.items():
            handler = self.commit_option_handlers[opt]
            getattr(self, handler)(opt_value)

        new_node = cmdutil.commit(repo.ui, repo, commitfun,
                                  (os.path.join(repo.root, as_bytes(rel_path))
                                   for rel_path in rel_paths),
                                  {b'addremove': add_remove,
                                   b'message': as_bytes(message),
                                   })
        return repo[new_node] if return_ctx else new_node

    def commit_file(self, relative_path,
                    content=None, message=None,
                    parent=None,
                    **commit_opts):
        """Write content at relative_path and commit in one call.

        This is meant to allow fast and efficient preparation of
        testing repositories. To do so, it goes a bit lower level
        than the actual commit command, so is not suitable to test specific
        commit options, especially if through extensions.

        This leaves the working directoy updated at the new commit.

        :param relative_path: relative path from repository root. If existing,
           will be overwritten by `content`
        :param content: what's to be written in ``relative_path``.
                        If not specified, will be replaced by random content.
        :param parent: binary node id or :class:`changectx` instance.
                       If specified, the repository is
                       updated to it first. Useful to produce branching
                       histories. This is single valued, because the purpose
                       of this method is not to produce merge commits.
        :param commit_opts: additional kwargs as in :meth:`commit`
        :returns: same as :meth:`commit`
        """
        repo = self.repo
        path = os.path.join(repo.root, as_bytes(relative_path))
        self.prepare_wdir(parent=parent)

        if content is None:
            content = self.random_content()
        content = as_bytes(content)

        if message is None:
            message = content

        with open(path, 'wb') as fobj:
            fobj.write(content)

        return self.commit((path, ), message=message, add_remove=True,
                           **commit_opts)

    def commit_removal(self, relative_path, parent=None, message=None,
                       **commit_opts):
        """Make a commit removing the given file.

        :param commit_opts: see :meth:`commit` except for ``add_removed`` which
           is ignored (forced to ``True``).
        """
        commit_opts.pop('add_remove', None)
        if message is None:
            message = b"removing %s" % as_bytes(relative_path)

        self.prepare_wdir(parent=parent)
        os.unlink(os.path.join(self.repo.root, as_bytes(relative_path)))
        return self.commit((relative_path, ),
                           message=as_bytes(message),
                           add_remove=True,
                           **commit_opts)

    def commit_empty(self, parent=None, **commit_opts):
        self.prepare_wdir(parent=parent)
        return self.commit((), **commit_opts)

    def update_bin(self, bin_node, **opts):
        """Update to a revision specified by its node in binary form.

        This is separated in order to avoid ambiguities
        """
        # maybe we'll do something lower level later
        self.update(node.hex(bin_node), **opts)

    def update(self, rev, hidden=False):
        repo = self.repo.unfiltered() if hidden else self.repo
        command('update', repo, as_bytes(rev), ui=repo.ui)

    def set_phase(self, phase_name, revs, force=True):
        opts = dict(force=force, rev=[as_bytes(r) for r in revs])
        phase_name_bytes = as_bytes(phase_name)
        opts.update((phn.decode(), phn == phase_name_bytes)
                    for phn in phase_names)
        self.command('phase', **opts)

    def merge_commit(self, ctx,
                     message=None,
                     tz_timestamp=None,
                     tz_datetime=None,
                     utc_timestamp=None,
                     utc_datetime=None,
                     user=None,
                     **precommit_opts):
        """Perform merge with given changeset <ctx> and create merge commit.

        Precedence rules for the timestamp and datetime parameters are
        as in :meth:`commit`.

        return: merge commit <changectx>
        """
        rev = ctx.rev()
        self.command(b'merge', rev=rev)

        for opt, opt_value in precommit_opts.items():
            handler = self.commit_option_handlers[opt]
            getattr(self, handler)(opt_value)

        opts = {}
        tz_timestamp = convert_date_times(tz_timestamp=tz_timestamp,
                                          utc_timestamp=utc_timestamp,
                                          utc_datetime=utc_datetime,
                                          tz_datetime=tz_datetime,
                                          )
        opts['date'] = b"%d %d" % tz_timestamp
        if user is None:
            user = self.repo.ui.config(b'ui', b'username')
        opts['user'] = as_bytes(user)

        if message is None:
            message = b'merge with revision %s' % ctx
        self.command(b'ci', message=as_bytes(message), **opts)
        return self.repo[b'.']
