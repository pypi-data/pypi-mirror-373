# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Common imports used throughout the package. '''

# ruff: noqa: F401


import                      abc
import                      asyncio
import collections.abc as   cabc
import                      collections
import contextlib as        ctxl
import                      datetime
import dataclasses as       dcls
import                      enum
import functools as         funct
import                      io
import                      inspect
import                      json
import                      locale
import                      platform
import                      re
import                      shutil
import                      stat
import                      subprocess
import                      sys
import                      time
import                      types
import urllib.parse as      urlparse
import                      warnings

from logging import getLogger as acquire_scribe
from pathlib import Path

import accretive as         accret
import                      appcore
import dynadoc as           ddoc
import detextive as         detext
import exceptiongroup as    excg
import frigid as            immut
import typing_extensions as typx
# --- BEGIN: Injected by Copier ---
import tyro
# --- END: Injected by Copier ---

from absence import Absential, absent, is_absent
from appcore import asyncf, generics
from appcore.state import Globals


simple_tyro_class = tyro.conf.configure( )
standard_tyro_class = tyro.conf.configure( tyro.conf.OmitArgPrefixes )
