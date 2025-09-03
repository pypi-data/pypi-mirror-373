import unittest

from zeonegraph._graphid import GraphId, cast_graphid, adapt_graphid


class TestGraphId(unittest.TestCase):
    def setUp(self):
        self.out = '7.9'
        self.gid = cast_graphid(self.out, None)

    def test_getId(self):
        self.assertEqual((7, 9), self.gid.getId())

    def test_eq(self):
        self.assertEqual(self.gid, self.gid)

    def test_str(self):
        self.assertEqual(self.out, str(self.gid))

    def test_repr(self):
        self.assertEqual("%s(%s)" % (GraphId.__name__, self.gid),
                         repr(self.gid))

    def test_adapt(self):
        self.assertEqual(b"'7.9'", adapt_graphid(self.gid).getquoted())
