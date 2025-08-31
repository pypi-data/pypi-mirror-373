# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Simple coverage plugin to exclude statements according to Mercurial version.

Syntax: comment code with ``hg==X.Y`` to indicate that it runs for version X.Y
(exactly). Other supported comparison operators are ``<``, ``>``, ``<=`` and ``>=``.

The only supported type of version is ``x.y``. Patch numbers ``x.y.z``, pre-releases
aren't supported at this point.

Complex expressions aren't implemented: results are expected to be impredictible.
Any complex expression that would turn out to work would probably stop working
the day we decide to properly implement them.

(inspired by coverage-pyver-pragma and coverage-python-version)
"""
from coverage import CoveragePlugin
from mercurial.util import versiontuple

# for now the rule is that x.9 is followed by (x+1).0
# hence major and minor have no actual semantics. Still, using the
# major version will help us to reduce the number of generated regexps
MAJOR_VERSIONS = [4, 5, 6, 7]


def exclude_regexps(current_major, current_minor):
    excl = []
    for maj in MAJOR_VERSIONS:
        if maj < current_major:
            excl.append(r'hg<[=]?%d\.' % maj)
        elif maj > current_major:
            excl.append(r'hg>[=]?%d\.' % maj)
        else:
            for minor in range(10):
                if minor < current_minor:
                    excl.append(r'hg<[=]?%d\.%d' % (maj, minor))
                elif minor > current_minor:
                    excl.append(r'hg>[=]?%d\.%d' % (maj, minor))
                else:
                    excl.append(r'hg>%d\.%d' % (maj, minor))
                    excl.append(r'hg<%d\.%d' % (maj, minor))
                if minor != current_minor:
                    excl.append(r'hg==%d\.%d' % (maj, minor))

    return excl


class MercurialVersionExclusionPlugin(CoveragePlugin):
    def configure(self, config):
        opt_name = 'report:exclude_lines'
        exclude_lines = config.get_option(opt_name)
        major, minor = versiontuple()[:2]
        exclude_lines.extend(exclude_regexps(major, minor))
        config.set_option(opt_name, exclude_lines)


def coverage_init(reg, _options):
    reg.add_configurer(MercurialVersionExclusionPlugin())
