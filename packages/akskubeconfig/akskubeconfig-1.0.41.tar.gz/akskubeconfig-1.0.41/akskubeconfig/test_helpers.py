#!/usr/bin/env python3
import unittest
import argparse
from akskubeconfig.helpers import (
    nextListItem,
    pluckAuth,
    getNext,
    overrideDefaults,
    merge,
    flatten,
    write,
    determine_auth_flow,
    print_json,
    print_yaml,
)
import tempfile
import os


class TestFunctions(unittest.TestCase):
    def test_nextListItem(self):
        # Test getting next item
        self.assertEqual(nextListItem(["a", "b", "c"], "a"), "b")
        # Test last item (no next item)
        self.assertIsNone(nextListItem(["a", "b", "c"], "c"))
        # Test item not in list
        self.assertIsNone(nextListItem(["a", "b", "c"], "d"))

    def test_pluckAuth(self):
        # Test with all keys present
        data = {
            "environment": "env1",
            "apiserver-id": "api1",
            "client-id": "client1",
            "tenant-id": "tenant1",
            "client-secret": "secret1",
            "certificate-path": "path1",
        }
        expected = ["env1", "api1", "client1", "tenant1", "secret1", "path1"]
        self.assertEqual(pluckAuth(data), expected)

        # Test with some keys missing
        data = {"environment": "env1", "client-id": "client1", "tenant-id": "tenant1"}
        expected = ["env1", None, "client1", "tenant1", None, None]
        self.assertEqual(pluckAuth(data), expected)

    def test_getNext(self):
        lst = ["a", "b", "c", "d"]
        self.assertEqual(getNext(lst, "a", "b", "c"), ["b", "c", "d"])
        self.assertEqual(getNext(lst, "a", "d"), ["b", None])
        self.assertEqual(getNext(lst, "x"), [None])

    def test_overrideDefaults(self):
        args = argparse.Namespace(env="env1", id="id1")
        self.assertEqual(overrideDefaults(args, env="env2", id=""), ["env2", "id1"])
        self.assertEqual(overrideDefaults(args, env="", id="id2"), ["env1", "id2"])

    def test_merge(self):
        self.assertEqual(merge([1, 2, 3], [3, 4, 5]), [1, 2, 3, 4, 5])
        self.assertEqual(merge([1, 2], [2, 3], 4), [1, 2, 3, 4])
        self.assertEqual(merge(1, 2, 3), [1, 2, 3])

    def test_flatten(self):
        self.assertEqual(flatten([1, [2, 3]], [4, 5]), [1, [2, 3], 4, 5])
        self.assertEqual(flatten([[1, 2], [3, 4]]), [1, 2, 3, 4])

    def test_write(self):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            filename = temp_file.name
        try:
            # Test successful write
            self.assertTrue(write(filename, "Test content"))
            with open(filename, "r") as file:
                self.assertEqual(file.read(), "Test content")
            # Test write failure with invalid path
            self.assertFalse(write("/invalid_path/file.txt", "Test"))
        finally:
            os.remove(filename)

    def test_determine_auth_flow(self):
        args = argparse.Namespace(
            default=True,
            device_flow=False,
            interactive=False,
            sp_secret=False,
            sp_pfx=False,
            managed_identity=False,
            managed_identity_id=False,
            az_cli=False,
            workload_identity=False,
        )
        self.assertEqual(determine_auth_flow(args), "default")

        args.default = False
        args.device_flow = True
        self.assertEqual(determine_auth_flow(args), "device_flow")

    def test_print_json(self):
        # Test printing JSON to console
        clusters = [{"name": "cluster1"}, {"name": "cluster2"}]
        self.assertTrue(print_json(clusters))

        # Test writing JSON to file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            filename = temp_file.name
        try:
            self.assertTrue(print_json(clusters, outfile=filename))
            with open(filename, "r") as file:
                content = file.read()
                self.assertIn("cluster1", content)
                self.assertIn("cluster2", content)
        finally:
            os.remove(filename)

    def test_print_yaml(self):
        # Test printing YAML to console
        clusters = [{"name": "cluster1"}, {"name": "cluster2"}]
        self.assertTrue(print_yaml(clusters))

        # Test writing YAML to file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            filename = temp_file.name
        try:
            self.assertTrue(print_yaml(clusters, outfile=filename))
            with open(filename, "r") as file:
                content = file.read()
                self.assertIn("cluster1", content)
                self.assertIn("cluster2", content)
        finally:
            os.remove(filename)


if __name__ == "__main__":
    unittest.main()
