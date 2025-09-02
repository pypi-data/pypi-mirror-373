import unittest

from case_insensitive_string_set import CaseInsensitiveStringSet


class TestCaseInsensitiveSet(unittest.TestCase):
    def test_in(self) -> None:
        cis = CaseInsensitiveStringSet()
        cis.add("a")
        self.assertIn("a", cis)
        self.assertIn("A", cis)
        self.assertIn("A", cis)
        self.assertNotIn("b", cis)
        self.assertNotIn("B", cis)
        self.assertNotIn("B", cis)

    def test_add(self) -> None:
        cis = CaseInsensitiveStringSet()
        cis.add("a")
        cis.add("A")
        self.assertEqual(["a"], list(cis))

    def test_remove(self) -> None:
        cis = CaseInsensitiveStringSet()
        cis.add("a")
        cis.remove("A")
        self.assertEqual([], list(cis))

    def test_discard(self) -> None:
        cis = CaseInsensitiveStringSet()
        cis.add("a")
        cis.discard("A")
        self.assertEqual([], list(cis))
        cis.discard("A")
        self.assertEqual([], list(cis))

    def test_pop(self) -> None:
        cis = CaseInsensitiveStringSet()
        cis.add("a")
        cis.add("A")
        self.assertEqual("a", cis.pop())
        self.assertEqual([], list(cis))

    def test_clear(self) -> None:
        cis = CaseInsensitiveStringSet()
        cis.add("a")
        cis.add("A")
        cis.clear()
        self.assertEqual([], list(cis))

    def test_intersection(self) -> None:
        cis1 = CaseInsensitiveStringSet(["a", "B", "c"])
        cis2 = CaseInsensitiveStringSet(["A", "b", "d"])
        self.assertEqual(CaseInsensitiveStringSet(["a", "b"]), cis1 & cis2)

    def test_union(self) -> None:
        cis1 = CaseInsensitiveStringSet(["a", "B", "c"])
        cis2 = CaseInsensitiveStringSet(["A", "b", "d"])
        self.assertEqual(CaseInsensitiveStringSet(["a", "b", "c", "d"]), cis1 | cis2)

    def test_difference(self) -> None:
        cis1 = CaseInsensitiveStringSet(["a", "B", "c"])
        cis2 = CaseInsensitiveStringSet(["A", "b", "d"])
        self.assertEqual(["c"], list(cis1 - cis2))
        self.assertEqual(["d"], list(cis2 - cis1))

    def test_symmetric_difference(self) -> None:
        cis1 = CaseInsensitiveStringSet(["a", "B", "c"])
        cis2 = CaseInsensitiveStringSet(["A", "b", "d"])
        self.assertEqual(CaseInsensitiveStringSet(["c", "d"]), cis1 ^ cis2)
        self.assertEqual(CaseInsensitiveStringSet(["c", "d"]), cis2 ^ cis1)

    def test_isdisjoint(self) -> None:
        cis1 = CaseInsensitiveStringSet(["a", "B", "c"])
        cis2 = CaseInsensitiveStringSet(["A", "b", "d"])
        self.assertFalse(cis1.isdisjoint(cis2))
        cis3 = CaseInsensitiveStringSet(["e", "f", "g"])
        self.assertTrue(cis1.isdisjoint(cis3))

    def test_issubset(self) -> None:
        cis1 = CaseInsensitiveStringSet(["a", "B"])
        cis2 = CaseInsensitiveStringSet(["A", "b", "d"])
        self.assertTrue(cis1 <= cis2)
        self.assertFalse(cis2 <= cis1)

    def test_issuperset(self) -> None:
        cis1 = CaseInsensitiveStringSet(["a", "B", "c"])
        cis2 = CaseInsensitiveStringSet(["A", "b"])
        self.assertTrue(cis1 >= cis2)
        self.assertFalse(cis2 >= cis1)

    def test_copy(self) -> None:
        cis1 = CaseInsensitiveStringSet(["a", "B", "c"])
        cis2 = cis1.copy()
        self.assertEqual(["a", "B", "c"], list(cis2))
        self.assertIsNot(cis1, cis2)
        self.assertEqual(cis1, cis2)
