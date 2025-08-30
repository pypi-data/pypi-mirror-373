#!/usr/bin/env python3
"""

"""
# mypy: disable-error-code="import-untyped,import-not-found"

# Imports:
from __future__ import annotations

# ##-- stdlib imports
import datetime
import enum
import functools as ftz
import itertools as itz
import logging as logmod
import pathlib as pl
import re
import time
import types
import collections
import contextlib
import hashlib
from copy import deepcopy
from uuid import UUID, uuid1
from weakref import ref
import atexit # for @atexit.register
import faulthandler
# ##-- end stdlib imports

# ##-- 3rd party imports
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, Index, IndexEntry, ObjType
from sphinx.domains.std import StandardDomain
from sphinx.roles import AnyXRefRole, ReferenceRole, XRefRole
from sphinx.util.nodes import make_refnode

# ##-- end 3rd party imports

from sphinx.util.logging import getLogger as getSphinxLogger
from sphinx_bib_domain._interface import DOMAIN_NAME

# ##-- types
# isort: off
import abc
import collections.abc
from typing import TYPE_CHECKING, cast, assert_type, assert_never
from typing import Generic, NewType
# Protocols:
from typing import Protocol, runtime_checkable
# Typing Decorators:
from typing import no_type_check, final, override, overload
# from dataclasses import InitVar, dataclass, field
# from pydantic import BaseModel, Field, model_validator, field_validator, ValidationError

if TYPE_CHECKING:
    from jgdv import Maybe
    from typing import Final
    from typing import ClassVar, Any, LiteralString
    from typing import Never, Self, Literal
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable

##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
sphlog = getSphinxLogger(__name__)
##-- end logging

# Vars:

# Body:

class InstitutionIndex(Index):
    """ A Custom index for sphinx """

    name      = 'institution-index'
    localname = 'Institution Index'
    shortname = 'instindex'

    def generate(self, docnames=None) -> tuple[Any, bool]:
        """ """
        content : dict[str, list[IndexEntry]] = collections.defaultdict(list)
        collapse = True
        entries = self.domain.data['entries']

        for institution, sigs in sorted(self.domain.data['institutions'].items()):
            sigs = sorted(sigs)
            sig_count = len(sigs)
            letter = institution[0].upper()
            content[letter].append(IndexEntry(f"{institution} ({sig_count})", 1, "",  "", "", "", ""))
            for sig in sigs:
                if sig not in entries:
                    continue
                obj = entries[sig]
                name = obj[0].removeprefix(f"{DOMAIN_NAME}.")
                content[letter].append(IndexEntry(name, 2, obj[2], obj[3], '', '', ''))
        else:
            return sorted(content.items()), collapse
