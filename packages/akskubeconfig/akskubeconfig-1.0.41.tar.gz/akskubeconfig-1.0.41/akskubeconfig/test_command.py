#!/usr/bin/env python3
import sys
import unittest
import pytest
import argparse
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
from akskubeconfig.errors import RequiredArgumentException
from akskubeconfig.command import (
    parse_args,
    set_defaults,
    get_cluster_credentials_for_targeted_cluster,
)


class DictToObject:
    def __init__(self, data):
        if isinstance(data, dict):
            for key, value in data.items():
                setattr(
                    self,
                    key,
                    self.__class__(value) if isinstance(value, (dict, list)) else value,
                )
        elif isinstance(data, list):
            # Handle lists by converting elements if they are dictionaries
            return [
                self.__class__(item) if isinstance(item, dict) else item
                for item in data
            ]
        else:
            # For non-dict/list values, just return the value itself
            return data

    def __new__(cls, data):
        # This method allows us to return a different type if data is not a dict
        if not isinstance(data, dict):
            return data
        return super().__new__(cls)


# Test for parse_args function
def test_parse_args():
    sys.argv = [
        "akskubeconfig",
        "--verbose",
        "--subscriptions",
        "sub1,sub2",
        "--client-id",
        "test-client-id",
        "--tenant-id",
        "test-tenant-id",
        "--json",
        "--cluster-name",
        "test-cluster",
    ]
    parsed_args = parse_args([sys.argv])

    assert parsed_args.verbose is True
    assert parsed_args.subscriptions == "sub1,sub2"
    assert parsed_args.client_id == "test-client-id"
    assert parsed_args.tenant_id == "test-tenant-id"
    assert parsed_args.json is True
    assert parsed_args.yaml is False
    assert parsed_args.cluster_name == "test-cluster"


# Test for set_defaults function
def test_set_defaults():
    args = argparse.Namespace(
        subscriptions="sub1,sub2",
        json=False,
        yaml=False,
        client_id=None,
        tenant_id=None,
    )
    args = set_defaults(args)

    assert args.subscriptions == ["sub1", "sub2"]
    assert args.yaml is True  # Default output format should be yaml


class TestArgs(unittest.TestCase):
    # Test parse_args function
    def test_parse_args(self):
        # test short form arguments
        sys.argv = [
            "py",
            "-v",
            "-s",
            "sub1,sub2",
            "--json",
            "-m",
            "5",
            "-o",
            "output.txt",
        ]
        args = parse_args([sys.argv])
        assert args.verbose == True
        assert args.subscriptions == "sub1,sub2"
        assert args.json == True
        assert args.yaml == False
        assert args.max_threads == 5
        assert args.outfile == "output.txt"
        # test long form arguments
        sys.argv = [
            "py",
            "--verbose",
            "--subscriptions",
            "sub1,sub2",
            "--yaml",
            "--max-threads",
            "5",
            "--outfile",
            "output.txt",
        ]
        args = parse_args([sys.argv])
        assert args.verbose == True
        assert args.subscriptions == "sub1,sub2"
        assert args.json == False
        assert args.yaml == True
        assert args.max_threads == 5
        assert args.outfile == "output.txt"
        # test mutually exclusive arguments
        sys.argv = ["py", "--json", "--yaml"]
        self.assertRaises(SystemExit, parse_args, [sys.argv])


# class TestListSubscriptions(unittest.TestCase):
#     @patch("akskubeconfig.SubscriptionClient")
#     def test_no_incorrect_args(self, mock_sub_client):
#         mock_sub_client.return_value.subscriptions.list.return_value = []
#         with self.assertRaises(Exception):
#             list_subscriptions(DefaultAzureCredential())

#     @patch("akskubeconfig.SubscriptionClient")
#     def test_all_subscriptions(self, mock_sub_client):
#         mock_subs = [MagicMock(spec=Subscription) for _ in range(3)]
#         mock_sub_client.return_value.subscriptions.list.return_value = mock_subs
#         result = list_subscriptions(DefaultAzureCredential(), [], False)
#         self.assertEqual(len(result), 3)

#     @patch("akskubeconfig.SubscriptionClient")
#     def test_specified_subscriptions_verbose_off(self, mock_sub_client):
#         mock_subs = [
#             MagicMock(spec=Subscription, subscription_id="sub1", display_name="sub1"),
#             MagicMock(spec=Subscription, subscription_id="sub2", display_name="sub2"),
#         ]
#         mock_sub_client.return_value.subscriptions.list.return_value = mock_subs
#         result = list_subscriptions(DefaultAzureCredential(), ["sub1"], False)
#         self.assertEqual(len(result), 1)
#         self.assertEqual(result[0].subscription_id, "sub1")

#     @patch("akskubeconfig.SubscriptionClient")
#     @patch("builtins.print")
#     def test_specified_subscriptions_verbose_on(self, mock_print, mock_sub_client):
#         mock_subs = [
#             MagicMock(spec=Subscription, subscription_id="sub1", display_name="sub1"),
#             MagicMock(spec=Subscription, subscription_id="sub2", display_name="sub2"),
#         ]
#         mock_sub_client.return_value.subscriptions.list.return_value = mock_subs
#         result = list_subscriptions(DefaultAzureCredential(), ["sub1"], True)
#         self.assertEqual(len(result), 1)
#         self.assertEqual(result[0].subscription_id, "sub1")
#         mock_print.assert_called()

#     @patch("akskubeconfig.SubscriptionClient")
#     def test_invalid_subscriptions(self, mock_sub_client):
#         mock_subs = [
#             MagicMock(spec=Subscription, subscription_id="sub1", display_name="sub1"),
#             MagicMock(spec=Subscription, subscription_id="sub2", display_name="sub2"),
#         ]
#         mock_sub_client.return_value.subscriptions.list.return_value = mock_subs
#         result = list_subscriptions(DefaultAzureCredential(), ["sub3"], False)
#         self.assertEqual(len(result), 0)


class TestSetDefaults(unittest.TestCase):
    def test_default_output_format(self):
        args = SimpleNamespace(json=False, yaml=False, subscriptions=None)
        modified_args = set_defaults(args)
        self.assertTrue(modified_args.yaml)
        self.assertFalse(modified_args.json)

    def test_json_flag(self):
        args = SimpleNamespace(json=True, yaml=False, subscriptions=None)
        modified_args = set_defaults(args)
        self.assertTrue(modified_args.json)
        self.assertFalse(modified_args.yaml)

    def test_yaml_flag(self):
        args = SimpleNamespace(json=False, yaml=True, subscriptions=None)
        modified_args = set_defaults(args)
        self.assertTrue(modified_args.yaml)
        self.assertFalse(modified_args.json)

    def test_subscriptions_list_splitting(self):
        args = SimpleNamespace(json=False, yaml=False, subscriptions="sub1,sub2,sub3")
        modified_args = set_defaults(args)
        self.assertEqual(modified_args.subscriptions, ["sub1", "sub2", "sub3"])

    def test_subscriptions_none(self):
        args = SimpleNamespace(json=False, yaml=False, subscriptions=None)
        modified_args = set_defaults(args)
        self.assertIsNone(modified_args.subscriptions)


@pytest.fixture
def mock_args():
    args = argparse.Namespace(
        verbose=True,
        server_id=None,
        client_id=None,
        tenant_id=None,
        client_secret=None,
        certificate_path=None,
        environment=None,
        cluster_name="mycluster",
    )
    return args


@patch("akskubeconfig.command.ContainerServiceClient")
@patch("akskubeconfig.command.yaml.safe_load")
def test_get_cluster_credentials_for_targeted_cluster_default_flow(
    mock_yaml_load, mock_aks_client, mock_args
):
    # Setup mocks
    mock_credentials = MagicMock()
    mock_subscription = MagicMock(subscription_id="subid", display_name="subdisp")
    mock_aks_client.return_value.managed_clusters.list.return_value = [
        DictToObject(
            {
                "name": "mycluster",
                "id": "/subscriptions/subid/resourceGroups/myrg/providers/Microsoft.ContainerService/managedClusters/mycluster",
            }
        )
    ]
    mock_kubeconfig = MagicMock()
    mock_kubeconfig.value = b"fake"
    mock_aks_client.return_value.managed_clusters.list_cluster_user_credentials.return_value.kubeconfigs = [
        mock_kubeconfig
    ]
    mock_yaml_load.return_value = {
        "clusters": [{"name": "mycluster"}],
        "contexts": [{"name": "context1"}],
        "users": [{"user": {"auth-provider": {"config": {}}}}],
    }

    result = get_cluster_credentials_for_targeted_cluster(
        mock_credentials, mock_subscription, "default", mock_args
    )
    assert result["clusters"] == [{"name": "mycluster"}]
    assert result["contexts"] == [{"name": "context1"}]
    assert isinstance(result["users"], list)


@patch("akskubeconfig.command.ContainerServiceClient")
@patch("akskubeconfig.command.yaml.safe_load")
@patch("akskubeconfig.command.Kubelogin")
@patch("akskubeconfig.command.pluckAuth")
def test_get_cluster_credentials_for_targeted_cluster_device_flow(
    mock_pluckAuth, mock_Kubelogin, mock_yaml_load, mock_aks_client, mock_args
):
    mock_args.server_id = None
    mock_args.client_id = None
    mock_args.tenant_id = None
    mock_args.client_secret = None
    mock_args.certificate_path = None
    mock_args.environment = None

    mock_credentials = MagicMock()
    mock_subscription = MagicMock(subscription_id="subid", display_name="subdisp")
    mock_aks_client.return_value.managed_clusters.list.return_value = [
        DictToObject(
            {
                "name": "mycluster",
                "id": "/subscriptions/subid/resourceGroups/myrg/providers/Microsoft.ContainerService/managedClusters/mycluster",
            }
        )
    ]
    mock_kubeconfig = MagicMock()
    mock_kubeconfig.value = b"fake"
    mock_aks_client.return_value.managed_clusters.list_cluster_user_credentials.return_value.kubeconfigs = [
        mock_kubeconfig
    ]
    mock_yaml_load.return_value = {
        "clusters": [{"name": "mycluster"}],
        "contexts": [{"name": "context1"}],
        "users": [{"user": {"auth-provider": {"config": {}}}}],
    }
    mock_pluckAuth.return_value = ("env", "srv", "cid", "tid", None, None)
    mock_kl = MagicMock()
    mock_Kubelogin.return_value = mock_kl

    # Should call NewDeviceCodeFlow
    get_cluster_credentials_for_targeted_cluster(
        mock_credentials, mock_subscription, "device_flow", mock_args
    )
    mock_kl.NewDeviceCodeFlow.assert_called_once_with("env", "srv", "cid", "tid")


@patch("akskubeconfig.command.ContainerServiceClient")
@patch("akskubeconfig.command.yaml.safe_load")
def test_get_cluster_credentials_for_targeted_cluster_cluster_not_found(
    mock_yaml_load, mock_aks_client, mock_args
):
    mock_credentials = MagicMock()
    mock_subscription = MagicMock(subscription_id="subid", display_name="subdisp")
    mock_aks_client.return_value.managed_clusters.list.return_value = []
    mock_args.cluster_name = "missingcluster"
    with pytest.raises(Exception) as excinfo:
        get_cluster_credentials_for_targeted_cluster(
            mock_credentials,
            mock_subscription,
            "default",
            mock_args,
        )
    assert "Cluster 'missingcluster' not found" in str(excinfo.value)


@patch("akskubeconfig.command.ContainerServiceClient")
@patch("akskubeconfig.command.yaml.safe_load")
@patch("akskubeconfig.command.getNext")
@patch("akskubeconfig.command.Kubelogin")
def test_get_cluster_credentials_for_targeted_cluster_exec_flow(
    mock_Kubelogin, mock_getNext, mock_yaml_load, mock_aks_client, mock_args
):
    mock_credentials = MagicMock()
    mock_subscription = MagicMock(subscription_id="subid", display_name="subdisp")
    mock_aks_client.return_value.managed_clusters.list.return_value = [
        DictToObject(
            {
                "name": "mycluster",
                "id": "/subscriptions/subid/resourceGroups/myrg/providers/Microsoft.ContainerService/managedClusters/mycluster",
            }
        )
    ]
    mock_kubeconfig = MagicMock()
    mock_kubeconfig.value = b"fake"
    mock_aks_client.return_value.managed_clusters.list_cluster_user_credentials.return_value.kubeconfigs = [
        mock_kubeconfig
    ]
    mock_yaml_load.return_value = {
        "clusters": [{"name": "mycluster"}],
        "contexts": [{"name": "context1"}],
        "users": [{"user": {"exec": {"args": []}}}],
    }
    mock_getNext.return_value = ("env", "srv", "cid", "tid", None, None)
    mock_kl = MagicMock()
    mock_Kubelogin.return_value = mock_kl

    get_cluster_credentials_for_targeted_cluster(
        mock_credentials, mock_subscription, "interactive", mock_args
    )
    mock_kl.NewWebBrowserFlow.assert_called_once_with("env", "srv", "cid", "tid")


@patch("akskubeconfig.command.ContainerServiceClient")
@patch("akskubeconfig.command.yaml.safe_load")
@patch("akskubeconfig.command.Kubelogin")
@patch("akskubeconfig.command.pluckAuth")
def test_get_cluster_credentials_for_targeted_cluster_missing_required_args(
    mock_pluckAuth, mock_Kubelogin, mock_yaml_load, mock_aks_client, mock_args
):
    mock_credentials = MagicMock()
    mock_subscription = MagicMock(subscription_id="subid", display_name="subdisp")
    mock_aks_client.return_value.managed_clusters.list.return_value = [
        DictToObject(
            {
                "name": "mycluster",
                "id": "/subscriptions/subid/resourceGroups/myrg/providers/Microsoft.ContainerService/managedClusters/mycluster",
            }
        )
    ]
    mock_kubeconfig = MagicMock()
    mock_kubeconfig.value = b"fake"
    mock_aks_client.return_value.managed_clusters.list_cluster_user_credentials.return_value.kubeconfigs = [
        mock_kubeconfig
    ]
    mock_yaml_load.return_value = {
        "clusters": [{"name": "mycluster"}],
        "contexts": [{"name": "context1"}],
        "users": [{"user": {"auth-provider": {"config": {}}}}],
    }
    # All required values are None
    mock_pluckAuth.return_value = (None, None, None, None, None, None)
    mock_kl = MagicMock()
    mock_Kubelogin.return_value = mock_kl

    with pytest.raises(RequiredArgumentException):
        get_cluster_credentials_for_targeted_cluster(
            mock_credentials, mock_subscription, "device_flow", mock_args
        )


# class TestInitFunction(unittest.TestCase):
#     # Test init function
#     @patch("akskubeconfig.auth")
#     @patch("akskubeconfig.parse_args")
#     def test_init_with_defaults(self, mock_parse_args, mock_auth):
#         # Mocking parse_args to return default arguments
#         mock_args = argparse.Namespace(
#             verbose=False,
#             subscriptions=None,
#             json=False,
#             yaml=True,
#             max_threads=10,
#             outfile="",
#         )
#         mock_parse_args.return_value = mock_args

#         # Mocking auth to return a mock ChainedTokenCredential object
#         mock_credential = MagicMock()
#         mock_auth.return_value = mock_credential

#         args, credentials = init()

#         # Assertions
#         mock_parse_args.assert_called_once()
#         mock_auth.assert_called_once()
#         self.assertEqual(args, mock_args)
#         self.assertEqual(credentials, mock_credential)

#     @patch("akskubeconfig.auth")
#     @patch("akskubeconfig.parse_args")
#     def test_init_with_custom_args(self, mock_parse_args, mock_auth):
#         # Mocking parse_args to return custom arguments
#         custom_args = argparse.Namespace(
#             verbose=True,
#             subscriptions="sub1,sub2",
#             json=True,
#             yaml=False,
#             max_threads=5,
#             outfile="output.txt",
#         )
#         mock_parse_args.return_value = custom_args

#         # Mocking auth to return a mock ChainedTokenCredential object
#         mock_credential = MagicMock()
#         mock_auth.return_value = mock_credential

#         args, credentials = init()

#         # Assertions
#         mock_parse_args.assert_called_once()
#         mock_auth.assert_called_once()
#         self.assertEqual(args, custom_args)
#         self.assertEqual(credentials, mock_credential)


# class TestMainFunction(unittest.TestCase):
#     @patch("akskubeconfig.init")
#     @patch("akskubeconfig.list_subscriptions")
#     @patch("akskubeconfig.get_cluster_credentials")
#     @patch("akskubeconfig.flatten")
#     @patch("akskubeconfig.print_json")
#     @patch("akskubeconfig.print_yaml")
#     @patch("akskubeconfig.Pool")
#     def test_main(
#         self,
#         mock_pool,
#         mock_print_yaml,
#         mock_print_json,
#         mock_flatten,
#         mock_get_cluster_credentials,
#         mock_list_subscriptions,
#         mock_init,
#     ):
#         # Mocking the init function to return test args and credentials
#         mock_args = argparse.Namespace(
#             verbose=False,
#             subscriptions=None,
#             json=False,
#             yaml=True,
#             max_threads=10,
#             outfile="",
#             service_principal=False,
#         )
#         mock_credentials = MagicMock()
#         mock_init.return_value = (mock_args, mock_credentials)

#         # Mocking list_subscriptions to return a list of mock subscriptions
#         mock_subs = [MagicMock(spec=Subscription) for _ in range(3)]
#         mock_list_subscriptions.return_value = mock_subs

#         # Mocking Pool and its methods
#         mock_pool_instance = MagicMock()
#         mock_pool.return_value = mock_pool_instance
#         mock_pool_instance.apply_async.return_value = MagicMock(
#             wait=MagicMock(),
#             get=MagicMock(return_value={"clusters": [], "contexts": [], "users": []}),
#         )

#         # Mocking flatten to return a flattened list
#         mock_flatten.return_value = [{"clusters": [], "contexts": [], "users": []}]

#         # Running the main function
#         main()

#         # Assertions
#         mock_init.assert_called_once()
#         mock_list_subscriptions.assert_called_once_with(mock_credentials, None, False)
#         self.assertEqual(mock_pool.call_count, 1)
#         self.assertEqual(mock_pool_instance.apply_async.call_count, 3)
#         mock_pool_instance.close.assert_called_once()
#         mock_flatten.assert_called_once()
#         mock_print_yaml.assert_called_once_with(
#             {
#                 "apiVersion": "v1",
#                 "kind": "Config",
#                 "clusters": [],
#                 "contexts": [],
#                 "current-context": "",
#                 "users": [],
#             },
#             outfile="",
#         )
#         mock_print_json.assert_not_called()

#     @patch("akskubeconfig.init")
#     @patch("akskubeconfig.list_subscriptions")
#     @patch("akskubeconfig.get_cluster_credentials")
#     @patch("akskubeconfig.flatten")
#     @patch("akskubeconfig.print_json")
#     @patch("akskubeconfig.print_yaml")
#     @patch("akskubeconfig.Pool")
#     def test_main_with_json_output(
#         self,
#         mock_pool,
#         mock_print_yaml,
#         mock_print_json,
#         mock_flatten,
#         mock_get_cluster_credentials,
#         mock_list_subscriptions,
#         mock_init,
#     ):
#         # Mocking the init function to return test args and credentials
#         mock_args = argparse.Namespace(
#             verbose=False,
#             subscriptions=None,
#             json=True,
#             yaml=False,
#             max_threads=10,
#             outfile="",
#             service_principal=False,
#         )
#         mock_credentials = MagicMock()
#         mock_init.return_value = (mock_args, mock_credentials)

#         # Mocking list_subscriptions to return a list of mock subscriptions
#         mock_subs = [MagicMock(spec=Subscription) for _ in range(3)]
#         mock_list_subscriptions.return_value = mock_subs

#         # Mocking Pool and its methods
#         mock_pool_instance = MagicMock()
#         mock_pool.return_value = mock_pool_instance
#         mock_pool_instance.apply_async.return_value = MagicMock(
#             wait=MagicMock(),
#             get=MagicMock(return_value={"clusters": [], "contexts": [], "users": []}),
#         )

#         # Mocking flatten to return a flattened list
#         mock_flatten.return_value = [{"clusters": [], "contexts": [], "users": []}]

#         # Running the main function
#         main()

#         # Assertions
#         mock_init.assert_called_once()
#         mock_list_subscriptions.assert_called_once_with(mock_credentials, None, False)
#         self.assertEqual(mock_pool.call_count, 1)
#         self.assertEqual(mock_pool_instance.apply_async.call_count, 3)
#         mock_pool_instance.close.assert_called_once()
#         mock_flatten.assert_called_once()
#         mock_print_json.assert_called_once_with(
#             {
#                 "apiVersion": "v1",
#                 "kind": "Config",
#                 "clusters": [],
#                 "contexts": [],
#                 "current-context": "",
#                 "users": [],
#             },
#             outfile="",
#         )
#         mock_print_yaml.assert_not_called()

#     @patch("akskubeconfig.init")
#     @patch("akskubeconfig.list_subscriptions")
#     @patch("akskubeconfig.Pool")
#     def test_main_exception_handling(
#         self, mock_pool, mock_list_subscriptions, mock_init
#     ):
#         # Mocking the init function to return test args and credentials
#         mock_args = argparse.Namespace(
#             verbose=False,
#             subscriptions=None,
#             json=False,
#             yaml=True,
#             max_threads=10,
#             outfile="",
#             service_principal=False,
#         )
#         mock_credentials = MagicMock()
#         mock_init.return_value = (mock_args, mock_credentials)

#         # Mocking list_subscriptions to raise an exception
#         mock_list_subscriptions.side_effect = Exception("Test Exception")

#         with self.assertRaises(SystemExit) as cm:
#             main()

#         self.assertEqual(cm.exception.code, 1)
#         mock_init.assert_called_once()
#         mock_list_subscriptions.assert_called_once_with(mock_credentials, None, False)
#         mock_pool.assert_not_called()


# class TestGetClusterCredentials(unittest.TestCase):
#     @patch("akskubeconfig.ContainerServiceClient")
#     @patch("yaml.safe_load")
#     def test_get_cluster_credentials(self, mock_safe_load, mock_aks_client):
#         # Mocking the credentials and subscription
#         mock_credentials = MagicMock()
#         mock_subscription = MagicMock(
#             subscription_id="sub1", display_name="Subscription 1"
#         )

#         # Mocking the AKS client and its methods
#         mock_cluster = MagicMock(
#             id="/subscriptions/sub1/resourceGroups/rg1/providers/Microsoft.ContainerService/managedClusters/cluster1",
#             name="cluster1",
#         )
#         mock_aks_client.return_value.managed_clusters.list.return_value = [mock_cluster]
#         mock_kubeconfig = MagicMock(
#             value=b"apiVersion: v1\nclusters:\n- name: cluster1\ncontexts:\n- name: context1\nusers:\n- name: user1\n"
#         )
#         mock_aks_client.return_value.managed_clusters.list_cluster_user_credentials.return_value.kubeconfigs = [
#             mock_kubeconfig
#         ]

#         # Mocking yaml.safe_load to return a parsed kubeconfig
#         mock_safe_load.return_value = {
#             "clusters": [{"name": "cluster1"}],
#             "contexts": [{"name": "context1"}],
#             "users": [{"name": "user1"}],
#         }

#         # Calling the function
#         result = get_cluster_credentials(
#             mock_credentials, mock_subscription, sp=False, verbose=False
#         )

#         # Assertions
#         self.assertEqual(result["clusters"], [{"name": "cluster1"}])
#         self.assertEqual(result["contexts"], [{"name": "context1"}])
#         self.assertEqual(result["users"], [{"name": "user1"}])
#         mock_aks_client.return_value.managed_clusters.list.assert_called_once()
#         mock_aks_client.return_value.managed_clusters.list_cluster_user_credentials.assert_called_once()
#         mock_safe_load.assert_called_once()

#     @patch("akskubeconfig.ContainerServiceClient")
#     @patch("yaml.safe_load")
#     def test_get_cluster_credentials_service_principal(
#         self, mock_safe_load, mock_aks_client
#     ):
#         # Mocking the credentials and subscription
#         mock_credentials = MagicMock()
#         mock_subscription = MagicMock(
#             subscription_id="sub1", display_name="Subscription 1"
#         )

#         # Mocking the AKS client and its methods
#         mock_cluster = MagicMock(
#             id="/subscriptions/sub1/resourceGroups/rg1/providers/Microsoft.ContainerService/managedClusters/cluster1",
#             name="cluster1",
#         )
#         mock_aks_client.return_value.managed_clusters.list.return_value = [mock_cluster]
#         mock_kubeconfig = MagicMock(
#             value=b"apiVersion: v1\nclusters:\n- name: cluster1\ncontexts:\n- name: context1\nusers:\n- name: user1\n"
#         )
#         mock_aks_client.return_value.managed_clusters.list_cluster_user_credentials.return_value.kubeconfigs = [
#             mock_kubeconfig
#         ]

#         # Mocking yaml.safe_load to return a parsed kubeconfig
#         mock_safe_load.return_value = {
#             "clusters": [{"name": "cluster1"}],
#             "contexts": [{"name": "context1"}],
#             "users": [{"name": "user1"}],
#         }

#         # Calling the function with service principal flag
#         result = get_cluster_credentials(
#             mock_credentials, mock_subscription, sp=True, verbose=False
#         )

#         # Assertions
#         self.assertEqual(result["clusters"], [{"name": "cluster1"}])
#         self.assertEqual(result["contexts"], [{"name": "context1"}])
#         self.assertEqual(result["users"], [{"name": "user1"}])
#         mock_aks_client.return_value.managed_clusters.list.assert_called_once()
#         mock_aks_client.return_value.managed_clusters.list_cluster_user_credentials.assert_called_once()
#         mock_safe_load.assert_called_once()

#     @patch("akskubeconfig.ContainerServiceClient")
#     @patch("yaml.safe_load")
#     def test_get_cluster_credentials_exception(self, mock_safe_load, mock_aks_client):
#         # Mocking the credentials and subscription
#         mock_credentials = MagicMock()
#         mock_subscription = MagicMock(
#             subscription_id="sub1", display_name="Subscription 1"
#         )

#         # Mocking the AKS client to raise an exception
#         mock_aks_client.return_value.managed_clusters.list.side_effect = Exception(
#             "Test Exception"
#         )

#         # Calling the function and expecting an exception
#         with self.assertRaises(Exception) as context:
#             get_cluster_credentials(
#                 mock_credentials, mock_subscription, sp=False, verbose=False
#             )

#         # Assertions
#         self.assertTrue("Test Exception" in str(context.exception))
#         mock_aks_client.return_value.managed_clusters.list.assert_called_once()
