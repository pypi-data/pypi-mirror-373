import re

from psycopg2 import InterfaceError
from psycopg2.extensions import AsIs

_pattern = re.compile(r'(\d+)\.(\d+)')


class GraphId(object):
    def __init__(self, gid):
        self.gid = gid

    def getId(self):
        return self.gid

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.gid == other.gid
        return False

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self)

    def __str__(self):
        return "%d.%d" % self.gid


def cast_graphid(value, cur):
    if value is None:
        return None

    m = _pattern.match(value)
    if m:
        labid = int(m.group(1))
        locid = int(m.group(2))
        gid = (labid, locid)
        return GraphId(gid)
    else:
        raise InterfaceError("bad graphid representation: %s" % value)


def adapt_graphid(graphid):
    return AsIs("'%s'" % graphid)
