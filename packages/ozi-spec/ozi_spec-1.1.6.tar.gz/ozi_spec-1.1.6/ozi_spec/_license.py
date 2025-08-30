# ozi/spec/_license.py
# Part of the OZI Project.
# See LICENSE.txt for license information.
# SPDX-License-Identifier: Unlicense
"""License specification constants."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence  # pragma: no cover

NOT_SUPPORTED = {
    'Aladdin Free Public License (AFPL)',  # nonreusable
    'Free For Educational Use',  # too broad
    'Free For Home Use',  # too broad
    'Free for non-commercial use',  # too broad
    'Freely Distributable',  # too broad
    'Freeware',  # too broad
    'GUST Font License 1.0',  # no licenseref
    'GUST Font License 2006-09-30',  # no licenseref
    'Netscape Public License (NPL)',  # nonreusable
    'Nokia Open Source License (NOKOS)',  # nonreusable
    'OSI Approved :: Attribution Assurance License',  # boilerplate
    'OSI Approved :: Common Development and Distribution License 1.0 (CDDL-1.0)',  # legacy
    'OSI Approved :: Common Public License',  # superseded
    'OSI Approved :: Historical Permission Notice and Disclaimer (HPND)',  # legacy
    'OSI Approved :: IBM Public License',  # superseded
    'OSI Approved :: Intel Open Source License',  # legacy
    'OSI Approved :: Jabber Open Source License',  # legacy
    'OSI Approved :: MITRE Collaborative Virtual Workspace License (CVW)',  # legacy
    'OSI Approved :: Motosoto License',  # nonreusable
    'OSI Approved :: European Union Public Licence 1.0 (EUPL 1.0)',  # superseded
    'OSI Approved :: Mozilla Public License 1.0 (MPL)',  # superseded
    'OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)',  # superseded
    'OSI Approved :: NASA Open Source Agreement v1.3 (NASA-1.3)',  # other
    'OSI Approved :: Nethack General Public License',  # nonreusable
    'OSI Approved :: Nokia Open Source License',  # nonreusable
    'OSI Approved :: Python License (CNRI Python License)',  # legacy
    'OSI Approved :: Python Software Foundation License',
    'OSI Approved :: Qt Public License (QPL)',  # nonreusable
    'OSI Approved :: Ricoh Source Code Public License',  # nonreusable
    'OSI Approved :: Sleepycat License',  # nonreusable
    'OSI Approved :: Sun Industry Standards Source License (SISSL)',  # legacy
    'OSI Approved :: Sun Public License',  # nonreusable
    'OSI Approved :: Vovida Software License 1.0',  # nonreusable
    'OSI Approved :: W3C License',  # nonreusable
    'OSI Approved :: X.Net License',  # legacy
    'OSI Approved :: Zope Public License',  # nonreusable
    'Repoze Public License',  # no licenseref
}

SPDX_LICENSE_MAP: dict[str, Sequence[str]] = {
    'CC0 1.0 Universal (CC0 1.0) Public Domain Dedication': ('CC0-1.0',),
    'CeCILL-B Free Software License Agreement (CECILL-B)': ('CECILL-B',),
    'CeCILL-C Free Software License Agreement (CECILL-C)': ('CECILL-C',),
    'DFSG approved': (
        'AGPL-3.0-only',
        'AGPL-3.0-or-later',
        'Apache-2.0',
        'Artistic-2.0',
        'BSD-3-Clause',
        'CC-BY-4.0',
        'CC-BY-SA-4.0',
        'EPL-1.0',
        'EFL-2.0',
        'GPL-2.0-only',
        'GPL-2.0-or-later',
        'GPL-3.0-only',
        'GPL-3.0-or-later',
        'ISC',
        'LGPL-2.1-only',
        'LGPL-2.1-or-later',
        'LGPL-3.0-only',
        'LGPL-3.0-or-later',
        'MIT',
        'OFL-1.1',
        'WTFPL',
        'Zlib',
    ),
    'Eiffel Forum License (EFL)': ('EFL-2.0',),
    'OSI Approved :: Academic Free License (AFL)': ('AFL-3.0',),
    'OSI Approved :: Apache Software License': ('Apache-2.0',),
    'OSI Approved :: Apple Public Source License': (
        'APSL-1.0',
        'APSL-1.1',
        'APSL-1.2',
        'APSL-2.0',
    ),
    'OSI Approved :: Artistic License': ('Artistic-2.0',),
    'OSI Approved :: Blue Oak Model License (BlueOak-1.0.0)': ('BlueOak-1.0.0',),
    'OSI Approved :: Boost Software License 1.0 (BSL-1.0)': ('BSL-1.0',),
    'OSI Approved :: BSD License': (
        '0BSD',
        'BSD-2-Clause',
        'BSD-3-Clause',
        'BSD-3-Clause-Clear',
        'BSD-4-Clause',
    ),
    'OSI Approved :: CEA CNRS Inria Logiciel Libre License, version 2.1 (CeCILL-2.1)': (
        'CECILL-2.1',
    ),
    'OSI Approved :: CMU License (MIT-CMU)': ('MIT-CMU',),
    'OSI Approved :: Eclipse Public License 1.0 (EPL-1.0)': ('EPL-1.0',),
    'OSI Approved :: Eclipse Public License 2.0 (EPL-2.0)': ('EPL-2.0',),
    'OSI Approved :: Eiffel Forum License': ('EFL-2.0',),
    'OSI Approved :: European Union Public Licence 1.1 (EUPL 1.1)': ('EUPL-1.1',),
    'OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)': ('EUPL-1.2',),
    'OSI Approved :: GNU Affero General Public License v3': (
        'AGPL-3.0-only',
        'AGPL-3.0-or-later',
    ),
    'OSI Approved :: GNU Free Documentation License (FDL)': (
        'GFDL-1.3-only',
        'GFDL-1.3-or-later',
    ),
    'OSI Approved :: GNU General Public License (GPL)': (
        'GPL-2.0-only',
        'GPL-2.0-or-later',
        'GPL-3.0-only',
        'GPL-3.0-or-later',
    ),
    'OSI Approved :: GNU General Public License v2 (GPLv2)': (
        'GPL-2.0-only',
        'GPL-2.0-or-later',
    ),
    'OSI Approved :: GNU General Public License v3 (GPLv3)': (
        'GPL-3.0-only',
        'GPL-3.0-or-later',
    ),
    'OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)': (
        'LGPL-2.0-only',
        'LGPL-2.1-only',
    ),
    'OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)': (
        'LGPL-2.0-or-later',
        'LGPL-2.1-or-later',
    ),
    'OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)': (
        'LGPL-3.0-only',
        'LGPL-3.0-or-later',
    ),
    'OSI Approved :: GNU Library or Lesser General Public License (LGPL)': (
        'LGPL-2.0-only',
        'LGPL-2.0-or-later',
        'LGPL-2.1-only',
        'LGPL-2.1-or-later',
        'LGPL-3.0-only',
        'LGPL-3.0-or-later',
    ),
    'OSI Approved :: ISC License (ISCL)': ('ISC',),
    'OSI Approved :: MirOS License (MirOS)': ('MirOS',),
    'OSI Approved :: MIT License': ('MIT', 'MIT-CMU', 'MIT-0'),
    'OSI Approved :: MIT No Attribution License (MIT-0)': ('MIT-0',),
    'OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)': ('MPL-2.0',),
    'OSI Approved :: Mulan Permissive Software License v2 (MulanPSL-2.0)': ('MulanPSL-2.0',),
    'OSI Approved :: Open Group Test Suite License': ('OGTSL',),
    'OSI Approved :: Open Software License 3.0 (OSL-3.0)': ('OSL-3.0',),
    'OSI Approved :: PostgreSQL License': ('PostgreSQL',),
    'OSI Approved :: SIL Open Font License 1.1 (OFL-1.1)': ('OFL-1.1',),
    'OSI Approved :: The Unlicense (Unlicense)': ('Unlicense',),
    'OSI Approved :: Universal Permissive License': ('UPL-1.0',),
    'OSI Approved :: University of Illinois/NCSA Open Source License': ('NCSA',),
    'OSI Approved :: Zero-Clause BSD (0BSD)': ('0BSD',),
    'OSI Approved :: zlib/libpng License': ('Zlib',),
    'OSI Approved': (
        '0BSD',
        'AFL-3.0',
        'AGPL-3.0-only',
        'AGPL-3.0-or-later',
        'APSL-1.0',
        'APSL-1.1',
        'APSL-1.2',
        'APSL-2.0',
        'Apache-2.0',
        'Artistic-2.0',
        'BSD-2-Clause',
        'BSD-3-Clause',
        'BSD-3-Clause-Clear',
        'BSD-4-Clause',
        'BSL-1.0',
        'BlueOak-1.0.0',
        'CECILL-2.1',
        'EFL-2.0',
        'EPL-1.0',
        'EPL-2.0',
        'EUPL-1.1',
        'EUPL-1.2',
        'GFDL-1.3-only',
        'GFDL-1.3-or-later',
        'GPL-2.0-only',
        'GPL-2.0-or-later',
        'GPL-3.0-only',
        'GPL-3.0-or-later',
        'ISC',
        'LGPL-2.0-only',
        'LGPL-2.0-or-later',
        'LGPL-2.1-only',
        'LGPL-2.1-or-later',
        'LGPL-3.0-only',
        'LGPL-3.0-or-later',
        'MIT',
        'MIT-0',
        'MIT-CMU',
        'MPL-2.0',
        'MirOS',
        'MulanPSL-2.0',
        'NCSA',
        'OFL-1.1',
        'OGTSL',
        'OSL-3.0',
        'PostgreSQL',
        'UPL-1.0',
        'Unlicense',
        'Zlib',
    ),
    'Other/Proprietary License': ('LicenseRef-Proprietary',),
    'Private': ('LicenseRef-Proprietary',),
    'Public Domain': ('LicenseRef-Public-Domain', 'Unlicense', 'CC0-1.0'),
}
SPDX_LICENSE_EXCEPTIONS = {
    '389-exception': ('GPL-2.0-only',),
    'Asterisk-exception': ('GPL-2.0-only',),
    'Asterisk-linking-protocols-exception': ('GPL-2.0-only',),
    'Autoconf-exception-2.0': ('GPL-2.0-only', 'GPL-2.0-or-later'),
    'Autoconf-exception-3.0': ('GPL-3.0-only', 'GPL-3.0-or-later'),
    'Autoconf-exception-generic': ('GPL-2.0-only', 'GPL-2.0-or-later'),
    'Autoconf-exception-generic-3.0': ('GPL-3.0-only', 'GPL-3.0-or-later'),
    'Autoconf-exception-macro': (
        'GPL-2.0-only',
        'GPL-2.0-or-later',
        'GPL-3.0-only',
        'GPL-3.0-or-later',
    ),
    'Bison-exception-1.24': ('GPL-2.0-only', 'GPL-2.0-or-later'),
    'Bison-exception-2.2': (
        'GPL-2.0-only',
        'GPL-2.0-or-later',
        'GPL-3.0-only',
        'GPL-3.0-or-later',
    ),
    'Bootloader-exception': (
        'GPL-2.0-only',
        'GPL-2.0-or-later',
        'GPL-3.0-only',
        'GPL-3.0-or-later',
    ),
    'CGAL-linking-exception': ('GPL-2.0-only',),
    'Classpath-exception-2.0': ('GPL-2.0-only',),
    'CLISP-exception-2.0': ('GPL-2.0-only',),
    'cryptsetup-OpenSSL-exception': (
        'GPL-2.0-only',
        'GPL-2.0-or-later',
        'GPL-3.0-only',
        'GPL-3.0-or-later',
    ),
    'DigiRule-FOSS-exception': ('GPL-2.0-only', 'GPL-2.0-or-later'),
    'eCos-exception-2.0': ('GPL-2.0-only', 'GPL-2.0-or-later'),
    'erlang-otp-linking-exception': (
        'GPL-2.0-only',
        'GPL-2.0-or-later',
        'GPL-3.0-only',
        'GPL-3.0-or-later',
    ),
    'Fawkes-Runtime-exception': (
        'GPL-2.0-only',
        'GPL-2.0-or-later',
        'GPL-3.0-only',
        'GPL-3.0-or-later',
    ),
    'FLTK-exception': ('LGPL-2.0-only',),
    'fmt-exception': ('MIT',),
    'Font-exception-2.0': ('GPL-2.0-only', 'GPL-2.0-or-later'),
    'freertos-exception-2.0': ('GPL-2.0-only', 'GPL-2.0-or-later'),
    'GCC-exception-2.0': ('GPL-2.0-only', 'GPL-2.0-or-later'),
    'GCC-exception-2.0-note': ('GPL-2.0-only', 'GPL-2.0-or-later'),
    'GCC-exception-3.1': ('GPL-3.0-and-later',),
    'Gmsh-exception': ('GPL-2.0-only',),
    'GNAT-exception': (
        'GPL-2.0-only',
        'GPL-2.0-or-later',
        'GPL-3.0-only',
        'GPL-3.0-or-later',
    ),
    'GNOME-examples-exception': ('CC-BY-SA-3.0',),
    'GNU-compiler-exception': (
        'GPL-2.0-only',
        'GPL-2.0-or-later',
        'GPL-3.0-only',
        'GPL-3.0-or-later',
    ),
    'gnu-javamail-exception': (
        'GPL-2.0-only',
        'GPL-2.0-or-later',
        'GPL-3.0-only',
        'GPL-3.0-or-later',
    ),
    'GPL-3.0-389-ds-base-exception': ('GPL-3.0-only',),
    'GPL-3.0-interface-exception': ('GPL-3.0-only',),
    'GPL-3.0-linking-exception': ('GPL-3.0-only',),
    'GPL-3.0-linking-source-exception': ('GPL-3.0-only',),
    'GPL-CC-1.0': (
        'GPL-2.0-only',
        'LGPL-2.0-only',
        'LGPL-2.1-only',
    ),
    'GStreamer-exception-2005': (
        'GPL-2.0-only',
        'GPL-2.0-or-later',
        'GPL-3.0-only',
        'GPL-3.0-or-later',
    ),
    'GStreamer-exception-2008': (
        'GPL-2.0-only',
        'GPL-2.0-or-later',
        'GPL-3.0-only',
        'GPL-3.0-or-later',
    ),
    'harbour-exception': (
        'GPL-2.0-only',
        'GPL-2.0-or-later',
        'GPL-3.0-only',
        'GPL-3.0-or-later',
    ),
    'i2p-gpl-java-exception': ('GPL-2.0-only', 'GPL-2.0-or-later'),
    'Independent-modules-exception': (
        'LGPL-2.0-only',
        'LGPL-2.1-or-later',
        'LGPL-2.1-only',
        'LGPL-3.0-only',
        'LGPL-3.0-or-later',
    ),
    'KiCad-libraries-exception': ('CC-BY-SA-4.0',),
    'LGPL-3.0-linking-exception': ('LGPL-3.0-only',),
    'libpri-OpenH323-exception': (
        'GPL-2.0-only',
        'GPL-2.0-or-later',
        'GPL-3.0-only',
        'GPL-3.0-or-later',
        'MPL-2.0',
    ),
    'Libtool-exception': (
        'GPL-2.0-only',
        'GPL-2.0-or-later',
        'GPL-3.0-only',
        'GPL-3.0-or-later',
        'LGPL-2.0-only',
        'LGPL-2.1-or-later',
        'LGPL-3.0-only',
        'LGPL-3.0-or-later',
    ),
    'Linux-syscall-note': ('GPL-2.0-only',),
    'LLGPL': ('LGPL-2.1-only',),
    'LLVM-exception': ('Apache-2.0',),
    'LZMA-exception': ('CPL-1.0',),
    'mif-exception': ('GPL-2.0-only', 'GPL-2.0-or-later'),
    'mxml-exception': ('Apache-2.0',),
    'OCaml-LGPL-linking-exception': (
        'LGPL-2.0-only',
        'LGPL-2.1-or-later',
        'LGPL-2.1-only',
        'LGPL-3.0-only',
        'LGPL-3.0-or-later',
    ),
    'OCCT-exception-1.0': ('LGPL-2.1-only',),
    'OpenJDK-assembly-exception-1.0': ('GPL-2.0-only',),
    'openvpn-openssl-exception': ('GPL-2.0-only', 'GPL-2.0-or-later'),
    'PCRE2-exception': ('BSD-3-Clause',),
    'PS-or-PDF-font-exception-20170817': ('AGPL-3.0-only',),
    'QPL-1.0-INRIA-2004-exception': ('QPL-1.0-INRIA-2004',),
    'Qt-GPL-exception-1.0': ('GPL-3.0-only',),
    'Qt-LGPL-exception-1.1': ('LGPL-2.1-only',),
    'Qwt-exception-1.0': ('LGPL-2.1-only',),
    'romic-exception': ('AGPL-3.0-only',),
    'RRDtool-FLOSS-exception-2.0': ('GPL-3.0-only',),
    'SANE-exception': (
        'GPL-2.0-only',
        'GPL-2.0-or-later',
        'GPL-3.0-only',
        'GPL-3.0-or-later',
    ),
    'SHL-2.0': ('Apache-2.0',),
    'SHL-2.1': ('Apache-2.0',),
    'stunnel-exception': (
        'GPL-2.0-only',
        'GPL-2.0-or-later',
        'GPL-3.0-only',
        'GPL-3.0-or-later',
    ),
    'SWI-exception': (
        'GPL-2.0-only',
        'GPL-2.0-or-later',
        'GPL-3.0-only',
        'GPL-3.0-or-later',
    ),
    'Swift-exception': ('Apache-2.0',),
    'Texinfo-exception': ('GPL-3.0-only',),
    'u-boot-exception-2.0': (
        'GPL-2.0-only',
        'GPL-2.0-or-later',
    ),
    'UBDL-exception': ('GPL-2.0-only',),
    'Universal-FOSS-exception-1.0': (
        '0BSD',
        'AFL-3.0',
        'AGPL-3.0-only',
        'AGPL-3.0-or-later',
        'APSL-1.0',
        'APSL-1.1',
        'APSL-1.2',
        'APSL-2.0',
        'Apache-2.0',
        'Artistic-2.0',
        'BSD-2-Clause',
        'BSD-3-Clause',
        'BSD-3-Clause-Clear',
        'BSD-4-Clause',
        'BSL-1.0',
        'BlueOak-1.0.0',
        'CECILL-2.1',
        'EFL-2.0',
        'EPL-1.0',
        'EPL-2.0',
        'EUPL-1.1',
        'EUPL-1.2',
        'GFDL-1.3-only',
        'GFDL-1.3-or-later',
        'GPL-2.0-only',
        'GPL-2.0-or-later',
        'GPL-3.0-only',
        'GPL-3.0-or-later',
        'ISC',
        'LGPL-2.0-only',
        'LGPL-2.0-or-later',
        'LGPL-2.1-only',
        'LGPL-2.1-or-later',
        'LGPL-3.0-only',
        'LGPL-3.0-or-later',
        'MIT',
        'MIT-0',
        'MIT-CMU',
        'MPL-2.0',
        'MirOS',
        'MulanPSL-2.0',
        'NCSA',
        'OFL-1.1',
        'OGTSL',
        'OSL-3.0',
        'PostgreSQL',
        'UPL-1.0',
        'Unlicense',
        'Zlib',
    ),
    'vsftpd-openssl-exception': ('GPL-2.0-only',),
    'WxWindows-exception-3.1': ('GPL-2.0-only', 'GPL-2.0-or-later'),
    'x11vnc-openssl-exception': ('GPL-2.0-only', 'GPL-2.0-or-later'),
}
