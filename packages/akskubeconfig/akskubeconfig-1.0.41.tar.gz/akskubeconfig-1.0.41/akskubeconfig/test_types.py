#!/usr/bin/env python3
import unittest
from akskubeconfig.types import Kubelogin, ClassicLogin


class TestKubelogin(unittest.TestCase):
    def setUp(self):
        self.kubelogin = Kubelogin()

    def test_initial_data_setup(self):
        expected_data = {
            "exec": {
                "command": "kubelogin",
                "apiVersion": "client.authentication.k8s.io/v1beta1",
                "installHint": """
        kubelogin is not installed which is required to connect to AAD enabled cluster.
        
        To learn more, please go to https://aka.ms/aks/kubelogin
        """,
                "provideClusterInfo": False,
            }
        }
        self.assertEqual(self.kubelogin.data, expected_data)

    def test_NewDeviceCodeFlow(self):
        self.kubelogin.NewDeviceCodeFlow("prod", "server123", "client456", "tenant789")
        expected_args = [
            "get-token",
            "--environment",
            "prod",
            "--server-id",
            "server123",
            "--client-id",
            "client456",
            "--tenant-id",
            "tenant789",
        ]
        self.assertEqual(self.kubelogin.data["exec"]["args"], expected_args)

    def test_NewWebBrowserFlow(self):
        self.kubelogin.NewWebBrowserFlow("dev", "server321", "client654", "tenant987")
        expected_args = [
            "get-token",
            "--login",
            "interactive",
            "--environment",
            "dev",
            "--server-id",
            "server321",
            "--client-id",
            "client654",
            "--tenant-id",
            "tenant987",
        ]
        self.assertEqual(self.kubelogin.data["exec"]["args"], expected_args)

    def test_NewSpSecretFlow(self):
        self.kubelogin.NewSpSecretFlow(
            "test", "server111", "client222", "tenant333", "secret444"
        )
        expected_args = [
            "get-token",
            "--login",
            "spn",
            "--environment",
            "test",
            "--server-id",
            "server111",
            "--client-id",
            "client222",
            "--client-secret",
            "secret444",
            "--tenant-id",
            "tenant333",
        ]
        self.assertEqual(self.kubelogin.data["exec"]["args"], expected_args)
        self.assertIsNone(self.kubelogin.data["exec"]["env"])

    def test_NewSpPFXFlow(self):
        self.kubelogin.NewSpPFXFlow(
            "prod", "server555", "client666", "tenant777", "/path/to/cert"
        )
        expected_args = [
            "get-token",
            "--login",
            "spn",
            "--environment",
            "prod",
            "--server-id",
            "server555",
            "--client-id",
            "client666",
            "--client-certificate",
            "/path/to/cert",
            "--tenant-id",
            "tenant777",
        ]
        self.assertEqual(self.kubelogin.data["exec"]["args"], expected_args)
        self.assertIsNone(self.kubelogin.data["exec"]["env"])

    def test_NewMSIFlow(self):
        self.kubelogin.NewMSIFlow("server999")
        expected_args = ["get-token", "--login", "msi", "--server-id", "server999"]
        self.assertEqual(self.kubelogin.data["exec"]["args"], expected_args)

    def test_NewMSIClientIdFlow(self):
        self.kubelogin.NewMSIClientIdFlow("server123", "client321")
        expected_args = [
            "get-token",
            "--login",
            "msi",
            "--server-id",
            "server123",
            "--client-id",
            "client321",
        ]
        self.assertEqual(self.kubelogin.data["exec"]["args"], expected_args)

    def test_NewAzureCliFlow(self):
        self.kubelogin.NewAzureCliFlow("serverCLI")
        expected_args = ["get-token", "--login", "azurecli", "--server-id", "serverCLI"]
        self.assertEqual(self.kubelogin.data["exec"]["args"], expected_args)
        self.assertIsNone(self.kubelogin.data["exec"]["env"])

    def test_NewWorkLoadIdentityFlow(self):
        self.kubelogin.NewWorkLoadIdentityFlow("serverWorkload")
        expected_args = [
            "get-token",
            "--login",
            "workloadidentity",
            "--server-id",
            "serverWorkload",
        ]
        self.assertEqual(self.kubelogin.data["exec"]["args"], expected_args)
        self.assertIsNone(self.kubelogin.data["exec"]["env"])


class TestClassicLogin(unittest.TestCase):
    def test_initial_data_setup(self):
        login = ClassicLogin("token123", "certDataABC", "keyDataXYZ")
        expected_data = {
            "token": "token123",
            "client-certificate-data": "certDataABC",
            "client-key-data": "keyDataXYZ",
        }
        self.assertEqual(login.data, expected_data)


if __name__ == "__main__":
    unittest.main()
