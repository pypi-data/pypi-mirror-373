from psycopg2 import InterfaceError

from zeonegraph._vertex import cast_vertex
from zeonegraph._edge import cast_edge


class Path(object):
    def __init__(self, vertices, edges):
        self.vertices = vertices
        self.edges = edges

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.vertices == other.vertices and self.edges == other.edges
        return False

    def __len__(self):
        return len(self.edges)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self)

    def __str__(self):
        p = [None] * (len(self.vertices) + len(self.edges))
        p[::2] = [str(v) for v in self.vertices]
        p[1::2] = [str(e) for e in self.edges]
        return "[%s]" % ','.join(p)


def cast_graphpath(value, cur):
    if value is None:
        return None

    tokens = []

    # ignore wrapping '[' and ']' characters
    pos = 1
    length = len(value) - 1

    start = pos
    depth = 0
    gid = False

    while pos < length:
        c = value[pos]
        if c == '"':
            if depth > 0:
                # Parse "string".
                # Leave pos unchanged if unmatched right " were found.

                escape = False
                i = pos + 1

                while i < length:
                    c = value[i]
                    if c == '\\':
                        escape = not escape
                    elif c == '"':
                        if escape:
                            escape = False
                        else:
                            pos = i
                            break
                    else:
                        escape = False

                    i += 1
        elif c == '[' and depth == 0:
            gid = True
        elif c == ']' and depth == 0:
            gid = False
        elif c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth < 0:
                raise InterfaceError("bad graphpath representation: %s" % value)
        elif c == ',' and depth == 0 and not gid:
            tokens.append(value[start:pos])
            start = pos + 1

        pos += 1

    tokens.append(value[start:pos])

    vertices = [cast_vertex(t, cur) for t in tokens[0::2]]
    edges = [cast_edge(t, cur) for t in tokens[1::2]]
    return Path(vertices, edges)
