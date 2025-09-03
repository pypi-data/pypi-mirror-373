import unittest
from typing import *

from v440.core.Version import Version
from v440.core.VersionError import VersionError


class TestVersionManipulation(unittest.TestCase):

    def test_version_modification(self: Self) -> None:
        # Create an instance of the v440.Version class
        v = Version("1.2.3")

        # Modify individual parts of the version
        v.release.major = 2
        v.release.minor = 5
        v.pre = "beta.1"
        v.local = "local.7.dev"

        # Verify the expected output
        self.assertEqual(str(v), "2.5.3b1+local.7.dev")


class TestVersionLocal(unittest.TestCase):

    def test_version_operations(self: Self) -> None:
        v = Version("1.2.3")
        backup = v.local
        v.local = "local.1.2.3"
        self.assertEqual(str(v), "1.2.3+local.1.2.3")
        self.assertEqual(str(v.local), "local.1.2.3")
        v.local.append("extra")
        self.assertEqual(str(v), "1.2.3+local.1.2.3.extra")
        self.assertEqual(str(v.local), "local.1.2.3.extra")
        v.local.remove(1)
        self.assertEqual(str(v), "1.2.3+local.2.3.extra")
        self.assertEqual(str(v.local), "local.2.3.extra")
        self.assertEqual(v.local[0], "local")
        self.assertEqual(v.local[-1], "extra")
        v.local.sort()
        self.assertEqual(str(v), "1.2.3+extra.local.2.3")
        self.assertEqual(str(v.local), "extra.local.2.3")
        v.local.clear()
        self.assertEqual(str(v), "1.2.3")
        self.assertEqual(str(v.local), "")
        v.local = "reset.1.2"
        self.assertEqual(str(v), "1.2.3+reset.1.2")
        self.assertEqual(str(v.local), "reset.1.2")
        self.assertTrue(v.local is backup)


class TestVersion(unittest.TestCase):

    def test_version_pre(self: Self) -> None:
        v = Version("1.2.3")
        backup = v.pre

        # Initial version, no pre-release version
        self.assertEqual(str(v), "1.2.3")
        self.assertEqual(v.pre, [None, None])

        # Set pre-release version to "a1"
        v.pre = "a1"
        self.assertEqual(str(v), "1.2.3a1")
        self.assertEqual(str(v.pre), "a1")

        # Modify pre-release phase to "preview"
        v.pre.phase = "preview"
        self.assertEqual(str(v), "1.2.3rc1")
        self.assertEqual(str(v.pre), "rc1")

        # Modify subphase to "42"
        v.pre.subphase = "42"
        self.assertEqual(str(v), "1.2.3rc42")
        self.assertEqual(str(v.pre), "rc42")

        # Change phase to a formatted string "BeTa"
        v.pre.phase = """
        BeTa
        """
        self.assertEqual(str(v), "1.2.3b42")
        self.assertEqual(str(v.pre), "b42")

        self.assertEqual(v.pre, backup)

        # Set pre-release to None
        v.pre = None
        self.assertEqual(str(v), "1.2.3")
        self.assertEqual(v.pre, [None, None])


class TestExample(unittest.TestCase):

    def test_example_1(self: Self) -> None:
        v = Version("v1.0.0")
        self.assertEqual(str(v), "1")  # Initial version
        self.assertEqual(v.format("3"), "1.0.0")  # Initial version formatted

    def test_example_2(self: Self) -> None:
        v = Version("2.5.3")
        self.assertEqual(str(v), "2.5.3")  # Modified version
        v.release[1] = 64
        v.release.micro = 4
        self.assertEqual(str(v), "2.64.4")  # Further modified version

    def test_example_3(self: Self) -> None:
        v1 = Version("1.6.3")
        v2 = Version("1.6.4")
        self.assertEqual(str(v1), "1.6.3")  # v1
        self.assertEqual(str(v2), "1.6.4")  # v2
        self.assertFalse(v1 == v2)  # v1 == v2 gives False
        self.assertTrue(v1 != v2)  # v1 != v2 gives True
        self.assertFalse(v1 >= v2)  # v1 >= v2 gives False
        self.assertTrue(v1 <= v2)  # v1 <= v2 gives True
        self.assertFalse(v1 > v2)  # v1 > v2 gives False
        self.assertTrue(v1 < v2)  # v1 < v2 gives True

    def test_example_3a(self: Self) -> None:
        v1 = Version("1.6.3")
        v2 = "1.6.4"
        self.assertEqual(str(v1), "1.6.3")  # v1
        self.assertEqual(str(v2), "1.6.4")  # v2
        self.assertFalse(v1 == v2)  # v1 == v2 gives False
        self.assertTrue(v1 != v2)  # v1 != v2 gives True
        self.assertFalse(v1 >= v2)  # v1 >= v2 gives False
        self.assertTrue(v1 <= v2)  # v1 <= v2 gives True
        self.assertFalse(v1 > v2)  # v1 > v2 gives False
        self.assertTrue(v1 < v2)  # v1 < v2 gives True

    def test_example_3b(self: Self) -> None:
        v1 = "1.6.3"
        v2 = Version("1.6.4")
        self.assertEqual(str(v1), "1.6.3")  # v1
        self.assertEqual(str(v2), "1.6.4")  # v2
        self.assertFalse(v1 == v2)  # v1 == v2 gives False
        self.assertTrue(v1 != v2)  # v1 != v2 gives True
        self.assertFalse(v1 >= v2)  # v1 >= v2 gives False
        self.assertTrue(v1 <= v2)  # v1 <= v2 gives True
        self.assertFalse(v1 > v2)  # v1 > v2 gives False
        self.assertTrue(v1 < v2)  # v1 < v2 gives True

    def test_example_4(self: Self) -> None:
        v = Version("2.5.3.9")
        self.assertEqual(str(v), "2.5.3.9")  # before sorting
        v.release.sort()
        self.assertEqual(str(v), "2.3.5.9")  # after sorting

    def test_example_5(self: Self) -> None:
        v = Version("2.0.0-alpha.1")
        self.assertEqual(str(v), "2a1")  # Pre-release version
        v.pre = "beta.2"
        self.assertEqual(str(v), "2b2")  # Modified pre-release version
        v.pre[1] = 4
        self.assertEqual(str(v), "2b4")  # Further modified pre-release version
        v.pre.phase = "PrEvIeW"
        self.assertEqual(str(v), "2rc4")  # Even further modified pre-release version

    def test_example_6(self: Self) -> None:
        v = Version("1.2.3")
        v.post = "post1"
        v.local = "local.7.dev"
        self.assertEqual(str(v), "1.2.3.post1+local.7.dev")  # Post-release version
        self.assertEqual(v.format("-1"), "1.2.post1+local.7.dev")  # Formatted version
        v.post = "post.2"
        self.assertEqual(str(v), "1.2.3.post2+local.7.dev")  # Modified version
        v.post = None
        self.assertEqual(str(v), "1.2.3+local.7.dev")  # Modified without post
        v.post = "post", 3
        v.local.sort()
        self.assertEqual(str(v), "1.2.3.post3+dev.local.7")  # After sorting local
        v.local.append(8)
        self.assertEqual(str(v), "1.2.3.post3+dev.local.7.8")  # Modified with new local
        v.local = "3.test.19"
        self.assertEqual(str(v), "1.2.3.post3+3.test.19")  # Modified local again

    def test_example_7(self: Self) -> None:
        v = Version("5.0.0")
        self.assertEqual(str(v), "5")  # Original version
        v.data = None
        self.assertEqual(str(v), "0")  # After reset
        v.base = "4!5.0.1"
        self.assertEqual(str(v), "4!5.0.1")  # Before error
        with self.assertRaises(Exception) as context:
            v.base = "9!x"
        self.assertTrue(
            "not a valid numeral segment" in str(context.exception)
        )  # Error
        self.assertEqual(str(v), "4!5.0.1")  # After error


class TestVersionRelease(unittest.TestCase):

    def setUp(self: Self) -> None:
        # Create a version class instance
        self.version = Version()

    def test_release_invalid_value(self: Self) -> None:
        # Test that invalid values raise an appropriate error
        with self.assertRaises(VersionError):
            self.version.release = ["a", 2, "3"]

    def test_major_minor_micro_aliases(self: Self) -> None:
        # Test major, minor, and micro aliases for the first three indices
        self.version.release = [1, 2, 3]
        self.assertEqual(self.version.release.major, 1)
        self.assertEqual(self.version.release.minor, 2)
        self.assertEqual(self.version.release.micro, 3)
        self.assertEqual(self.version.release.patch, 3)  # 'patch' is an alias for micro

    def test_release_modify_aliases(self: Self) -> None:
        # Test modifying the release via major, minor, and micro properties
        self.version.release = [1, 2, 3]
        self.version.release.major = 10
        self.version.release.minor = 20
        self.version.release.micro = 30
        self.assertEqual(self.version.release, [10, 20, 30])
        self.assertEqual(self.version.release.patch, 30)

    def test_release_with_tailing_zeros_simulation(self: Self) -> None:
        # Test that the release can simulate arbitrary high number of tailing zeros
        self.version.release = [1, 2]
        simulated_release = self.version.release[:5]
        self.assertEqual(simulated_release, [1, 2, 0, 0, 0])

    def test_release_empty_major(self: Self) -> None:
        # Test that an empty release still has valid major, minor, micro values
        self.version.release = []
        self.assertEqual(self.version.release.major, 0)
        self.assertEqual(self.version.release.minor, 0)
        self.assertEqual(self.version.release.micro, 0)
        self.assertEqual(self.version.release.patch, 0)

    def test_release_modify_with_alias_increase_length(self: Self) -> None:
        # Test that modifying an alias can extend the length of release
        self.version.release = [1]
        self.version.release.minor = 5  # This should make release [1, 5]
        self.assertEqual(self.version.release, [1, 5])
        self.version.release.micro = 3  # This should make release [1, 5, 3]
        self.assertEqual(self.version.release, [1, 5, 3])

    def test_release_modify_major_only(self: Self) -> None:
        # Test that setting just the major property works
        self.version.release.major = 10
        self.assertEqual(self.version.release, [10])

    def test_release_modify_minor_only(self: Self) -> None:
        # Test that setting just the minor property extends release
        self.version.release = []
        self.version.release.minor = 1
        self.assertEqual(self.version.release, [0, 1])

    def test_release_modify_micro_only(self: Self) -> None:
        # Test that setting just the micro (patch) property extends release
        self.version.release = []
        self.version.release.micro = 1
        self.assertEqual(self.version.release, [0, 0, 1])


class TestAdditionalVersionRelease(unittest.TestCase):

    def setUp(self: Self) -> None:
        # Initialize a fresh Version instance for every test
        self.version = Version()

    def test_release_inequality_with_list(self: Self) -> None:
        # Test inequality of release with a normal list
        self.version.release = [1, 2, 3]
        self.assertFalse(self.version.release == [1, 2, 4])

    def test_release_len(self: Self) -> None:
        # Test the length of the release list
        self.version.release = [1, 2, 3]
        self.assertEqual(len(self.version.release), 3)

    def test_release_slice_assignment(self: Self) -> None:
        # Test assigning a slice to release
        self.version.release = [1, 2, 3, 4, 5]
        self.version.release[1:4] = [20, 30, 40]
        self.assertEqual(self.version.release, [1, 20, 30, 40, 5])

    def test_release_invalid_assignment(self: Self) -> None:
        # Test assigning an invalid type to release (should raise an error)
        with self.assertRaises(VersionError):
            self.version.release = ["1", "invalid", "3"]

    def test_release_iterable(self: Self) -> None:
        # Test if release supports iteration
        self.version.release = [1, 2, 3]
        result = [x for x in self.version.release]
        self.assertEqual(result, [1, 2, 3])

    def test_release_repr(self: Self) -> None:
        # Test the repr of the release property
        self.version.release = [1, 2, 3]
        self.assertEqual(str(self.version.release), "1.2.3")

    def test_release_data_property(self: Self) -> None:
        # Test the 'data' property
        self.version.release = [1, 2, 3]
        self.assertEqual(self.version.release.data, [1, 2, 3])

    def test_release_data_setter(self: Self) -> None:
        # Test setting the 'data' property directly
        self.version.release.data = [10, 20, 30]
        self.assertEqual(self.version.release, [10, 20, 30])

    def test_release_contains(self: Self) -> None:
        # Test 'in' keyword with release
        self.version.release = [1, 2, 3]
        self.assertIn(2, self.version.release)
        self.assertNotIn(4, self.version.release)

    def test_release_mul(self: Self) -> None:
        # Test multiplying the release (list behavior)
        self.version.release = [1, 2]
        self.assertEqual(self.version.release * 3, [1, 2, 1, 2, 1, 2])

    def test_release_addition(self: Self) -> None:
        # Test adding another list to release
        self.version.release = [1, 2, 3]
        self.assertEqual(self.version.release + [4, 5], [1, 2, 3, 4, 5])


class TestVersionLocal(unittest.TestCase):

    def setUp(self: Self) -> None:
        # Initialize a fresh Version instance for every test
        self.version = Version()

    def test_local_len(self: Self) -> None:
        # Test the length of the local list
        self.version.local = [1, "dev", "build"]
        self.assertEqual(len(self.version.local), 3)

    def test_local_slice_assignment(self: Self) -> None:
        # Test assigning a slice to the local list
        self.version.local = [1, "dev", "build"]
        self.version.local[1:3] = ["alpha", "beta"]
        self.assertEqual(self.version.local, [1, "alpha", "beta"])

    def test_local_contains(self: Self) -> None:
        # Test 'in' keyword with local list
        self.version.local = [1, "dev", "build"]
        self.assertIn("dev", self.version.local)
        self.assertNotIn("alpha", self.version.local)

    def test_local_mul(self: Self) -> None:
        # Test multiplying the local list
        self.version.local = [1, "dev"]
        self.assertEqual(self.version.local * 3, [1, "dev", 1, "dev", 1, "dev"])

    def test_local_addition(self: Self) -> None:
        # Test adding another list to local
        self.version.local = [1, "dev"]
        self.assertEqual(self.version.local + ["build"], [1, "dev", "build"])

    def test_local_equality_with_list(self: Self) -> None:
        # Test equality of local with a normal list
        self.version.local = [1, "dev"]
        self.assertTrue(self.version.local == [1, "dev"])

    def test_local_inequality_with_list(self: Self) -> None:
        # Test inequality of local with a normal list
        self.version.local = [1, "dev"]
        self.assertFalse(self.version.local == [1, "build"])

    def test_local_repr(self: Self) -> None:
        # Test repr of local list
        self.version.local = [1, "dev", "build"]
        self.assertEqual(str(self.version.local), "1.dev.build")

    def test_local_data_property(self: Self) -> None:
        # Test that 'data' property correctly reflects local's internal list
        self.version.local = [1, "dev", "build"]
        self.assertEqual(self.version.local.data, [1, "dev", "build"])

    def test_local_data_setter(self: Self) -> None:
        # Test that 'data' property can be set directly
        self.version.local.data = ["custom", "data"]
        self.assertEqual(self.version.local, ["custom", "data"])

    def test_local_iterable(self: Self) -> None:
        # Test if local supports iteration
        self.version.local = "1.dev.build"
        result = [x for x in self.version.local]
        self.assertEqual(result, [1, "dev", "build"])


if __name__ == "__main__":
    unittest.main()
