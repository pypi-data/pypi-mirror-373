import re

from psycopg2 import InterfaceError
from psycopg2.extras import json

from zeonegraph._graphid import cast_graphid

_pattern = re.compile(r'(.+?)\[(.+?)\]\[(.+?),(.+?)\](.*)', re.S)


class Edge(object):
    def __init__(self, label, eid, start, end, props):
        self.label = label
        self.eid = eid
        self.start = start
        self.end = end
        self.props = props

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.eid == other.eid
        return False

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self)

    def __str__(self):
        return "%s[%s][%s,%s]%s" % (self.label, self.eid, self.start, self.end,
                                    json.dumps(self.props))


def cast_edge(value, cur):
    if value is None:
        return None

    m = _pattern.match(value)
    if m:
        label = m.group(1)
        eid = cast_graphid(m.group(2), cur)
        start = cast_graphid(m.group(3), cur)
        end = cast_graphid(m.group(4), cur)
        props = json.loads(m.group(5))
        return Edge(label, eid, start, end, props)
    else:
        raise InterfaceError("bad edge representation: %s" % value)
