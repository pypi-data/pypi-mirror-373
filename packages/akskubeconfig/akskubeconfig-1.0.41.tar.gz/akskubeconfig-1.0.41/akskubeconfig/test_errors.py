#!/usr/bin/env python3
import unittest
from io import StringIO
import sys

from akskubeconfig.errors import RequiredArgumentException, UnrecognizedDataStructure


class TestRequiredArgumentException(unittest.TestCase):
    def setUp(self):
        # Redirect stdout to capture print statements
        self.held_stdout = StringIO()
        sys.stdout = self.held_stdout

    def tearDown(self):
        # Reset stdout
        sys.stdout = sys.__stdout__

    def test_no_missing_arguments(self):
        exception = RequiredArgumentException(
            environment="prod",
            server_id="123",
            client_id="456",
            tenant_id="789",
            client_secret="abc",
            certificate_path="/path",
        )
        self.assertEqual(exception.flags, [])
        self.assertIn(
            "Please try again with the following flags", self.held_stdout.getvalue()
        )

    def test_some_missing_arguments(self):
        exception = RequiredArgumentException(
            environment=None, client_id="456", tenant_id=None
        )
        self.assertIn("--environment", exception.flags)
        self.assertIn("--tenant-id", exception.flags)
        self.assertNotIn("--client-id", exception.flags)

    def test_all_missing_arguments(self):
        exception = RequiredArgumentException(
            environment=None,
            server_id=None,
            client_id=None,
            tenant_id=None,
            client_secret=None,
            certificate_path=None,
        )
        expected_flags = [
            "--environment",
            "--server-id",
            "--client-id",
            "--tenant-id",
            "--client-secret",
            "--certificate-path",
        ]
        self.assertEqual(exception.flags, expected_flags)

    def test_exception_message(self):
        RequiredArgumentException(environment=None)
        output = self.held_stdout.getvalue()
        self.assertIn(
            "Error: Unable to automatically determine all required values from Azure API.",
            output,
        )
        self.assertIn("--environment", output)


class TestUnrecognizedDataStructure(unittest.TestCase):
    def setUp(self):
        # Redirect stdout to capture print statements
        self.held_stdout = StringIO()
        sys.stdout = self.held_stdout

    def tearDown(self):
        # Reset stdout
        sys.stdout = sys.__stdout__

    def test_unrecognized_structure_message(self):
        struct_name = "CustomStruct"
        UnrecognizedDataStructure(struct_name)
        output = self.held_stdout.getvalue()
        self.assertIn(f"Unknown data structure: {struct_name}", output)


if __name__ == "__main__":
    unittest.main()
