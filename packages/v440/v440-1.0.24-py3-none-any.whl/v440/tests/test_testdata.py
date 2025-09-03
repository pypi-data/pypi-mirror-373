import enum
import functools
import operator
import tomllib
import unittest
from importlib import resources
from typing import *

import iterprod
import packaging.version

from v440.core.Version import Version
from v440.core.VersionError import VersionError


class Util(enum.Enum):
    util = None

    @functools.cached_property
    def data(self: Self) -> dict:
        text: str = resources.read_text("v440.tests", "testdata.toml")
        data: dict = tomllib.loads(text)
        return data


class TestVersionReleaseAttrs(unittest.TestCase):

    def test_0(self: Self) -> None:
        k: str
        v: dict
        for k, v in Util.util.data["release_attr"].items():
            self.release(**v, key=k)

    def release(
        self: Self,
        key: str,
        query: list,
        attrname: Optional[str] = None,
        args: list | tuple = (),
        kwargs: dict | tuple = (),
        target: Optional[list] = None,
        solution: Any = None,
    ) -> None:
        # Test the append method of the release list-like object
        version: Version = Version()
        version.release = query
        if attrname is not None:
            attr: Any = getattr(version.release, attrname)
            ans: Any = attr(*args, **dict(kwargs))
            self.assertEqual(ans, solution)
        if target is not None:
            self.assertEqual(version.release, target)


class TestVersionReleaseVersionError(unittest.TestCase):

    def test_0(self: Self) -> None:
        k: str
        v: dict
        for k, v in Util.util.data["release_VersionError"].items():
            self.release(**v, key=k)

    def release(
        self: Self,
        key: str,
        query: list,
    ) -> None:
        version: Version = Version()
        with self.assertRaises(VersionError):
            version.release = query


class TestVersionLocalVersionError(unittest.TestCase):

    def test_0(self: Self) -> None:
        k: str
        v: dict
        for k, v in Util.util.data["local_VersionError"].items():
            self.local(**v, key=k)

    def local(
        self: Self,
        key: str,
        query: list,
    ) -> None:
        version: Version = Version()
        with self.assertRaises(VersionError):
            version.local = query


class TestVersionLocal(unittest.TestCase):
    def test_0(self: Self) -> None:
        k: str
        v: dict
        for k, v in Util.util.data["local_attr"].items():
            self.local(**v, key=k)

    def local(
        self: Self,
        key: str,
        query: list,
        attrname: Optional[str] = None,
        args: list | tuple = (),
        kwargs: dict | tuple = (),
        target: Optional[list] = None,
        solution: Any = None,
    ) -> None:
        version: Version = Version()
        version.local = query
        if attrname is not None:
            attr: Any = getattr(version.local, attrname)
            ans: Any = attr(*args, **dict(kwargs))
            self.assertEqual(ans, solution)
        if target is not None:
            self.assertEqual(version.local, target)


class TestVersionEpoch(unittest.TestCase):
    def epoch(
        self: Self,
        full: Any,
        part: Any,
        query: Any = None,
        key: str = "",
    ) -> None:
        msg: str = "epoch %r" % key
        v: Version = Version("1.2.3")
        v.epoch = query
        self.assertEqual(str(v), full, msg=msg)
        self.assertIsInstance(v.epoch, int, msg=msg)
        self.assertEqual(v.epoch, part, msg=msg)

    def test_0(self: Self) -> None:
        k: str
        v: dict
        for k, v in Util.util.data["epoch"].items():
            self.epoch(**v, key=k)


class TestSlicing(unittest.TestCase):

    def test_slicing_2(self: Self) -> None:
        v = Version("1.2.3.4.5.6.7.8.9.10")
        try:
            v.release[-8:15:5] = 777
        except Exception as e:
            error = e
        else:
            error = None
        self.assertNotEqual(error, None)

    def slicingmethod(
        self: Self,
        query: Any,
        change: Any,
        solution: str,
        start: Any = None,
        stop: Any = None,
        step: Any = None,
        key: str = "",
    ) -> None:
        v = Version(query)
        v.release[start:stop:step] = change
        self.assertEqual(str(v), solution, "slicingmethod %s" % key)

    def test_slicing_3(self: Self) -> None:
        sli: dict = Util.util.data["slicingmethod"]
        k: str
        v: dict
        for k, v in sli.items():
            self.slicingmethod(**v, key=k)

    def test_slicing_7(self: Self) -> None:
        # test_slicing_7
        v: Version = Version("1.2.3.4.5.6.7.8.9.10")
        del v.release[-8:15:5]
        self.assertEqual(str(v), "1.2.4.5.6.7.9.10")


class TestDataProperty(unittest.TestCase):
    def test_data(self: Self) -> None:
        self.v = Version()
        for k, v in Util.util.data["data_property"].items():
            self.data(**v, key=k)
        self.data(query=None, solution="0")

    def data(
        self: Self,
        query: Any,
        solution: str,
        key: str = "",
    ) -> None:
        msg: str = "data_property %r" % key
        self.v.data = query
        self.assertEqual(solution, str(self.v), msg=msg)
        self.assertEqual(self.v.data, str(self.v), msg=msg)
        self.assertEqual(type(self.v.data), str, msg=msg)


class TestVersionRelease(unittest.TestCase):

    def setUp(self: Self) -> None:
        # Create a version class instance
        self.version = Version()

    def test_0(self: Self) -> None:
        k: str
        v: Any
        for k, v in Util.util.data["release"].items():
            self.release(key=k, **v)

    def release(self: Self, query: Any, solution: Any, key: str = "") -> None:
        self.version.release = query
        self.assertEqual(self.version.release, solution)


class TestDev(unittest.TestCase):

    def test_initial_none_dev(self: Self) -> None:
        v: Version = Version("1.2.3")
        self.assertEqual(str(v), "1.2.3")
        self.assertIsNone(v.dev)

    def test_dev_as_none(self: Self) -> None:
        v: Version = Version("1.2.3")
        v.dev = None
        self.assertEqual(str(v), "1.2.3")
        self.assertIsNone(v.dev)

    def test_dev_as_tuple(self: Self) -> None:
        self.dev(
            key="test_dev_as_tuple",
            v_version="1.2.3",
            v_dev=("dev", "5000"),
            v_str="1.2.3.dev5000",
            v_ans=5000,
        )

    def test_strings_a(self: Self) -> None:
        k: str
        v: dict
        for k, v in Util.util.data["devint"].items():
            self.dev(key=k, **v)

    def dev(
        self: Self,
        key: str,
        v_version: Any,
        v_str: Any,
        v_ans: Any,
        v_dev: Any = None,
        dev_type: type = int,
    ):
        msg: str = "dev %r" % key
        v: Version = Version(v_version)
        v.dev = v_dev
        self.assertEqual(str(v), v_str, msg=msg)
        self.assertIsInstance(v.dev, dev_type, msg=msg)
        self.assertEqual(v.dev, v_ans, msg=msg)


class TestVersionSpecifiers(unittest.TestCase):

    def test_version_with_invalid_specifiers(self: Self) -> None:
        # Test version with invalid specifiers that should raise an error
        with self.assertRaises(VersionError):
            Version("1.2.3--4")

        with self.assertRaises(VersionError):
            Version("1.2.3a1--4")

    def test_spec_toml(self: Self) -> None:
        k: str
        v: dict
        for k, v in Util.util.data["spec"].items():
            self.spec(**v, key=k)

    def spec(self: Self, string_a: str, string_b: str, key: str = "") -> None:
        msg: str = "spec %r" % key
        version: Version = Version(string_a)
        self.assertEqual(str(version), string_b, msg=msg)


class TestPackaging(unittest.TestCase):
    def test_strings_a(self: Self) -> None:
        a: packaging.version.Version
        b: str
        f: int
        g: str
        s: str
        x: str
        y: list
        for x, y in Util.util.data["strings"]["valid"].items():
            for s in y:
                a = packaging.version.Version(s)
                b = str(a)
                f = len(a.release)
                g = Version(s).format(f)
                self.assertEqual(b, g)

    def test_strings_b(self: Self) -> None:
        a: packaging.version.Version
        b: packaging.version.Version
        s: str
        msg: str
        x: str
        y: list
        for x, y in Util.util.data["strings"]["valid"].items():
            for s in y:
                a = packaging.version.Version(s)
                b = Version(s).packaging()
                msg = f"{s} should match packaging.version.Version"
                self.assertEqual(a, b, msg=msg)

    def test_strings_c(self: Self) -> None:
        pure: list = list()
        l: list
        for l in Util.util.data["strings"]["valid"].values():
            pure += l
        ops: list = [
            operator.eq,
            operator.ne,
            operator.gt,
            operator.ge,
            operator.le,
            operator.lt,
        ]
        a: packaging.version.Version
        b: packaging.version.Version
        c: packaging.version.Version
        d: packaging.version.Version
        native: bool
        convert: bool
        msg: str
        op: Any
        for x, y, op in iterprod.iterprod(pure, pure, ops):
            a = packaging.version.Version(x)
            b = Version(x).packaging()
            c = packaging.version.Version(y)
            d = Version(y).packaging()
            native = op(a, c)
            convert = op(b, d)
            msg = f"{op} should match for {x!r} and {y!r}"
            self.assertEqual(native, convert, msg=msg)

    def test_field(self: Self) -> None:
        versionable: list = list()
        l: list
        for l in Util.util.data["strings"]["valid"].values():
            versionable += l
        for l in Util.util.data["strings"]["incomp"].values():
            versionable += l
        version_obj: Version = Version()
        v: Version
        x: str
        for x in versionable:
            v = Version(x)
            self.assertEqual(v.isdevrelease(), v.packaging().is_devrelease)
            self.assertEqual(v.isprerelease(), v.packaging().is_prerelease)
            self.assertEqual(v.ispostrelease(), v.packaging().is_postrelease)
            self.assertEqual(str(v.base), v.packaging().base_version)
            self.assertEqual(str(v.public), v.packaging().public)
            version_obj.local = v.packaging().local
            self.assertEqual(str(v.local), str(version_obj.local))

    def test_exc(self: Self) -> None:
        l: list
        x: str
        for l in Util.util.data["strings"]["exc"].values():
            for x in l:
                with self.assertRaises(VersionError):
                    Version(x)

    def test_exc_pack(self: Self) -> None:
        impure: list = list()
        l: list
        for l in Util.util.data["strings"]["incomp"].values():
            impure += l
        for l in Util.util.data["strings"]["exc"].values():
            impure += l
        x: str
        for x in impure:
            with self.assertRaises(packaging.version.InvalidVersion):
                packaging.version.Version(x)


if __name__ == "__main__":
    unittest.main()
