#!/usr/bin/env python3
import argparse
import sys
import yaml
from typing import Tuple
from akskubeconfig.types import Kubelogin, ClassicLogin
from akskubeconfig.errors import RequiredArgumentException, UnrecognizedDataStructure
from akskubeconfig.helpers import (
    pluckAuth,
    getNext,
    flatten,
    determine_auth_flow,
    print_json,
    print_yaml,
)
from multiprocessing import Pool
from azure.identity import DefaultAzureCredential, ChainedTokenCredential
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.subscription.models import Subscription
from azure.mgmt.containerservice import ContainerServiceClient


# Parse CLI args as a function to make testing easier
def parse_args(args) -> argparse.Namespace:
    """
    The function `parse_args` defines a command-line argument parser using argparse in Python.

    :param args: The code you provided is a Python function that uses the `argparse` module to define
    and parse command-line arguments. The function `parse_args` takes in a list of arguments (`args`)
    and returns a `argparse.Namespace` object containing the parsed arguments
    :return: The function `parse_args` returns an `argparse.Namespace` object containing the parsed
    arguments provided in the `args` parameter.
    """
    parser = argparse.ArgumentParser()
    formatGroup = parser.add_mutually_exclusive_group()
    loginGroup = parser.add_mutually_exclusive_group()
    parser.add_argument(
        "-v", "--verbose", help="Increase output verbosity", action="store_true"
    )
    parser.add_argument(
        "-s",
        "--subscriptions",
        help="A comma separated list of subscription to use. If omitted, all subscriptions will be checked.",
        type=str,
    )
    parser.add_argument(
        "--client-id",
        help="Override the client id to write into the kubeconfig. Only applicable if required by the selected authentication flow.",
        type=str,
    )
    parser.add_argument(
        "--tenant-id",
        help="Override the tenant id to write into the kubeconfig. Only applicable if required by the selected authentication flow.",
        type=str,
    )
    parser.add_argument(
        "--client-secret",
        help="Override the client secret to write into the kubeconfig. Only applicable if required by the selected authentication flow.",
        type=str,
    )
    parser.add_argument(
        "--certificate-path",
        help="Override the certificate path to write into the kubeconfig. Only applicable if required by the selected authentication flow.",
        type=str,
    )
    parser.add_argument(
        "--server-id",
        help="Override the server id to write into the kubeconfig.",
        type=str,
    )
    parser.add_argument(
        "--environment",
        help="Override the environment to write into the kubeconfig.",
        type=str,
        default="AzurePublicCloud",
    )
    loginGroup.add_argument(
        "--default",
        help="Use the default flow authenticate within the generated kubeconfig (default)",
        action="store_true",
    )
    loginGroup.add_argument(
        "--device-flow",
        help="Use device flow to authenticate within the generated kubeconfig",
        action="store_true",
    )
    loginGroup.add_argument(
        "--interactive",
        help="Use the interactive web browser flow to authenticate within the generated kubeconfig",
        action="store_true",
    )
    loginGroup.add_argument(
        "--sp-secret",
        help="Use a service principal secret to authenticate within the generated kubeconfig",
        action="store_true",
    )
    loginGroup.add_argument(
        "--sp-pfx",
        help="Use a service principal pfx certificate to authenticate within the generated kubeconfig",
        action="store_true",
    )
    loginGroup.add_argument(
        "--managed-identity",
        help="Use a managed identity to authenticate within the generated kubeconfig",
        action="store_true",
    )
    loginGroup.add_argument(
        "--managed-identity-id",
        help="Use a managed identity to authenticate within the generated kubeconfig",
        action="store_true",
    )
    loginGroup.add_argument(
        "--az-cli",
        help="Use the Azure CLI to authenticate within the generated kubeconfig",
        action="store_true",
    )
    loginGroup.add_argument(
        "--workload-identity",
        help="Use a workload identity to authenticate within the generated kubeconfig",
        action="store_true",
    )
    formatGroup.add_argument("--json", help="Output as JSON", action="store_true")
    formatGroup.add_argument(
        "--yaml", help="Output as YAML (default)", action="store_true"
    )
    parser.add_argument(
        "-m",
        "--max-threads",
        help="Maximum number of threads to use",
        type=int,
        default=10,
    )
    parser.add_argument("-o", "--outfile", help="Output file", type=str, default="")
    parser.add_argument(
        "--cluster-name",
        help="Name of the specific cluster to target. If not specified, all clusters in the subscription will be used.",
        type=str,
    )

    return parser.parse_args()


# auth with DefaultAzureCredential
def auth() -> ChainedTokenCredential:
    """
    The function `auth` returns a `ChainedTokenCredential` object using the `DefaultAzureCredential`.

    :return: The function `auth` is returning an instance of `DefaultAzureCredential`.
    """
    return DefaultAzureCredential()


# get subscriptions to test the credential
def list_subscriptions(
    credentials: ChainedTokenCredential, subscriptions: list, verbose: bool
) -> list[Subscription]:
    """
    The function `list_subscriptions` takes in credentials, a list of subscriptions, and a boolean flag
    for verbosity, then retrieves a list of subscriptions based on the input criteria.

    :param credentials: ChainedTokenCredential - An object that represents a chain of credentials used
    for authentication
    :type credentials: ChainedTokenCredential
    :param subscriptions: The `subscriptions` parameter in the `list_subscriptions` function is expected
    to be a list containing either subscription IDs or display names of subscriptions that you want to
    work with. If this parameter is provided, the function will filter the list of subscriptions
    obtained from the SubscriptionClient based on the provided subscription IDs
    :type subscriptions: list
    :param verbose: The `verbose` parameter in the `list_subscriptions` function is a boolean flag that
    indicates whether additional information or messages should be displayed during the execution of the
    function. When `verbose` is set to `True`, the function will print out messages or details to
    provide more information about the process
    :type verbose: bool
    :return: The function `list_subscriptions` returns a list of `Subscription` objects based on the
    input parameters provided. If subscriptions are specified, it filters the subscriptions based on the
    subscription IDs or display names provided in the `subscriptions` list. If no subscriptions are
    specified, it returns all subscriptions available in the `sub_list`.
    """
    sub_client = SubscriptionClient(credentials)
    sub_list = sub_client.subscriptions.list()
    # Raise an exception if no subscriptions are found
    if sub_list is None:
        raise Exception("No subscriptions found")

    # Build a List of subscriptions to work with
    if subscriptions:
        if verbose:
            print(f"Using subscriptions: {subscriptions}")
        return [
            sub
            for sub in sub_list
            if sub.subscription_id in subscriptions or sub.display_name in subscriptions
        ]
    else:
        return [sub for sub in sub_list]


# Get Kubeconfig for only for targeted cluster in the subscription
def get_cluster_credentials_for_targeted_cluster(
    credentials: ChainedTokenCredential,
    subscription: Subscription,
    authFlow: str,
    args: argparse.Namespace,
) -> dict:
    """
    The function `get_cluster_credentials_for_targeted_cluster` retrieves the kubeconfig for a specific
    cluster in a given subscription based on the provided authentication flow and arguments.

    :param credentials: The `credentials` parameter in the `get_cluster_credentials_for_targeted_cluster`
    function is expected to be of type `ChainedTokenCredential`. This parameter likely contains the
    necessary credentials for authenticating with the Azure services to retrieve cluster information
    :type credentials: ChainedTokenCredential
    :param subscription: Subscription is an object that likely contains information about a subscription
    in a cloud service provider, such as Azure. It may include details like subscription ID, display
    name, and other relevant information for managing resources within that subscription
    :type subscription: Subscription
    :param authFlow: The `authFlow` parameter in the `get_cluster_credentials_for_targeted_cluster`
    function represents the authentication flow that will be used to obtain credentials for accessing the
    Kubernetes cluster. It determines how the authentication will be performed based on the provided value.
    The function then proceeds to configure the authentication settings accordingly based on the specified
    :type authFlow: str
    :param args: The `args` parameter in the `get_cluster_credentials_for_targeted_cluster` function is an
    `argparse.Namespace` object that contains the parsed command-line arguments. It is used to retrieve various
    arguments passed to the script when it is executed. These arguments can be used to customize the behavior of
    the function based on user preferences or requirements
    :type args: argparse.Namespace
    """

    configs = {
        "apiVersion": "v1",
        "kind": "Config",
        "clusters": list(),
        "contexts": list(),
        "current-context": "",
        "users": list(),
    }

    if args.verbose:
        print(
            f"└──> Getting kubeconfig for {args.cluster_name} in {subscription.display_name}"
        )

    aks_client = ContainerServiceClient(credentials, subscription.subscription_id)  # type: ignore

    # First, find the cluster to get its resource group
    clusters = aks_client.managed_clusters.list()
    target_cluster = None
    for cluster in clusters:
        if args.verbose:
            print(f"└──> Found cluster: {cluster.name} in {subscription.display_name}")
        if cluster.name == args.cluster_name:
            target_cluster = cluster
            break

    if target_cluster is None:
        raise Exception(
            f"Cluster '{args.cluster_name}' not found in subscription '{subscription.display_name}'"
        )

    # Extract resource group name from cluster ID
    if target_cluster.id is None:
        raise Exception(
            f"Could not find cluster '{args.cluster_name}' or its ID in subscription '{subscription.display_name}'"
        )
    resource_group_name = target_cluster.id.split("/")[4]

    c = aks_client.managed_clusters.list_cluster_user_credentials(
        resource_group_name, args.cluster_name
    )
    if c.kubeconfigs is None or len(c.kubeconfigs) == 0:
        raise Exception(
            f"Could not retrieve kubeconfig for cluster '{args.cluster_name}' in subscription '{subscription.display_name}'"
        )
    result = c.kubeconfigs[0]
    if result.value is None:
        raise Exception(
            f"Could not retrieve kubeconfig for cluster '{args.cluster_name}' in subscription '{subscription.display_name}'"
        )
    config_str: str = result.value.decode("utf-8")
    config_yaml = yaml.safe_load(config_str)
    configs["clusters"].append(config_yaml["clusters"][0])  # type: ignore
    configs["contexts"].append(config_yaml["contexts"][0])  # type: ignore
    if authFlow != "default":
        kl = Kubelogin()
        if "auth-provider" in config_yaml["users"][0]["user"]:
            (
                environment,
                server_id,
                client_id,
                tenant_id,
                client_secret,
                certificate_path,
            ) = pluckAuth(config_yaml["users"][0]["user"]["auth-provider"]["config"])
        elif "exec" in config_yaml["users"][0]["user"]:
            (
                environment,
                server_id,
                client_id,
                tenant_id,
                client_secret,
                certificate_path,
            ) = getNext(
                config_yaml["users"][0]["user"]["exec"]["args"],
                "--environment",
                "--server-id",
                "--client-id",
                "--tenant-id",
                "--client-secret",
                "--certificate-path",
            )
        else:
            try:
                token = config_yaml["users"][0]["user"]["token"]
                client_certificate_data = config_yaml["users"][0]["user"][
                    "client-certificate-data"
                ]
                client_key_data = config_yaml["users"][0]["user"]["client-key-data"]
            except KeyError:
                raise UnrecognizedDataStructure(config_yaml["users"][0]["user"])
            authFlow = "classic"
        # Override values if they were passed as arguments
        if args.client_id:
            client_id = args.client_id
        if args.tenant_id:
            tenant_id = args.tenant_id
        if args.client_secret:
            client_secret = args.client_secret
        if args.certificate_path:
            certificate_path = args.certificate_path
        if args.environment:
            environment = args.environment

        match authFlow:
            case "device_flow":
                if None not in [environment, server_id, client_id, tenant_id]:
                    kl.NewDeviceCodeFlow(environment, server_id, client_id, tenant_id)
                else:
                    raise RequiredArgumentException(
                        environment=environment,
                        server_id=server_id,
                        client_id=client_id,
                        tenant_id=tenant_id,
                    )
            case "interactive":
                if None not in [environment, server_id, client_id, tenant_id]:
                    kl.NewWebBrowserFlow(environment, server_id, client_id, tenant_id)
                else:
                    raise RequiredArgumentException(
                        environment=environment,
                        server_id=server_id,
                        client_id=client_id,
                        tenant_id=tenant_id,
                    )
            case "sp_secret":
                if None not in [
                    environment,
                    server_id,
                    client_id,
                    tenant_id,
                    client_secret,
                ]:
                    kl.NewSpSecretFlow(
                        environment, server_id, client_id, tenant_id, client_secret
                    )
                else:
                    raise RequiredArgumentException(
                        environment=environment,
                        server_id=server_id,
                        client_id=client_id,
                        tenant_id=tenant_id,
                        client_secret=client_secret,
                    )
            case "sp_pfx":
                if None not in [
                    environment,
                    server_id,
                    client_id,
                    tenant_id,
                    certificate_path,
                ]:
                    kl.NewSpPFXFlow(
                        environment,
                        server_id,
                        client_id,
                        tenant_id,
                        certificate_path,
                    )
                else:
                    raise RequiredArgumentException(
                        environment=environment,
                        server_id=server_id,
                        client_id=client_id,
                        tenant_id=tenant_id,
                        certificate_path=certificate_path,
                    )
            case "managed_identity":
                if server_id:
                    kl.NewMSIFlow(server_id)
                else:
                    raise RequiredArgumentException(server_id=server_id)
            case "managed_identity_id":
                if None not in [server_id, client_id]:
                    kl.NewMSIClientIdFlow(server_id, client_id)
                else:
                    raise RequiredArgumentException(
                        server_id=server_id, client_id=client_id
                    )
            case "az_cli":
                if server_id:
                    kl.NewAzureCliFlow(server_id)
                else:
                    raise RequiredArgumentException(server_id=server_id)
            case "workload_identity":
                if server_id:
                    kl.NewWorkLoadIdentityFlow(server_id)
                else:
                    raise RequiredArgumentException(server_id=server_id)
            case "classic":
                if None not in [token, client_certificate_data, client_key_data]:
                    kl = ClassicLogin(
                        token=token,
                        client_certificate_data=client_certificate_data,
                        client_key_data=client_key_data,
                    )  # type: ignore
                else:
                    raise RequiredArgumentException(
                        token=token,
                        client_certificate_data=client_certificate_data,
                        client_key_data=client_key_data,
                    )
        config_yaml["users"][0]["user"] = kl.data
    configs["users"].append(config_yaml["users"][0])  # type: ignore
    return configs


# Get kubeconfigs for each cluster in a subscription
def get_cluster_credentials(
    credentials: ChainedTokenCredential,
    subscription: Subscription,
    authFlow: str,
    args: argparse.Namespace,
) -> dict:
    """
    The function `get_cluster_credentials` retrieves cluster credentials based on the specified
    authentication flow and arguments.

    :param credentials: The `credentials` parameter in the `get_cluster_credentials` function is
    expected to be of type `ChainedTokenCredential`. This parameter likely contains the necessary
    credentials for authenticating with the Azure services to retrieve cluster information
    :type credentials: ChainedTokenCredential
    :param subscription: Subscription is an object that likely contains information about a subscription
    in a cloud service provider, such as Azure. It may include details like subscription ID, display
    name, and other relevant information for managing resources within that subscription
    :type subscription: Subscription
    :param authFlow: The `authFlow` parameter in the `get_cluster_credentials` function represents the
    authentication flow that will be used to obtain credentials for accessing the Kubernetes clusters.
    It determines the method of authentication to be used based on the provided value. The function then
    proceeds to configure the authentication settings accordingly based on the specified
    :type authFlow: str
    :param args: The `args` parameter in the `get_cluster_credentials` function is an
    `argparse.Namespace` object that contains the parsed command-line arguments. It is used to retrieve
    various arguments passed to the script when it is executed. These arguments can be used to customize
    the behavior of the function based on user
    :type args: argparse.Namespace
    """
    configs = {
        "apiVersion": "v1",
        "kind": "Config",
        "clusters": list(),
        "contexts": list(),
        "current-context": "",
        "users": list(),
    }

    if args.verbose:
        print(f"└──> Listing clusters in {subscription.display_name}")
    aks_client = ContainerServiceClient(credentials, subscription.subscription_id)  # type: ignore
    clusters = aks_client.managed_clusters.list()

    for cluster in clusters:
        if cluster.id is None or cluster.name is None:
            raise Exception(
                f"Could not retrieve kubeconfig for cluster '{args.cluster_name}' in subscription '{subscription.display_name}'"
            )
        c = aks_client.managed_clusters.list_cluster_user_credentials(
            cluster.id.split("/")[4], cluster.name
        )
        if c.kubeconfigs is None or len(c.kubeconfigs) == 0:
            raise Exception(
                f"Could not retrieve kubeconfig for cluster '{args.cluster_name}' in subscription '{subscription.display_name}'"
            )
        result = c.kubeconfigs[0]
        if result.value is None:
            raise Exception(
                f"Could not retrieve kubeconfig for cluster '{args.cluster_name}' in subscription '{subscription.display_name}'"
            )
        config_str: str = result.value.decode("utf-8")
        config_yaml = yaml.safe_load(config_str)
        configs["clusters"].append(config_yaml["clusters"][0])  # type: ignore
        configs["contexts"].append(config_yaml["contexts"][0])  # type: ignore
        if authFlow != "default":
            kl = Kubelogin()
            if "auth-provider" in config_yaml["users"][0]["user"]:
                (
                    environment,
                    server_id,
                    client_id,
                    tenant_id,
                    client_secret,
                    certificate_path,
                ) = pluckAuth(
                    config_yaml["users"][0]["user"]["auth-provider"]["config"]
                )
            elif "exec" in config_yaml["users"][0]["user"]:
                (
                    environment,
                    server_id,
                    client_id,
                    tenant_id,
                    client_secret,
                    certificate_path,
                ) = getNext(
                    config_yaml["users"][0]["user"]["exec"]["args"],
                    "--environment",
                    "--server-id",
                    "--client-id",
                    "--tenant-id",
                    "--client-secret",
                    "--certificate-path",
                )
            else:
                try:
                    token = config_yaml["users"][0]["user"]["token"]
                    client_certificate_data = config_yaml["users"][0]["user"][
                        "client-certificate-data"
                    ]
                    client_key_data = config_yaml["users"][0]["user"]["client-key-data"]
                except KeyError:
                    raise UnrecognizedDataStructure(config_yaml["users"][0]["user"])
                authFlow = "classic"
            # Override values if they were passed as arguments
            if args.server_id:
                server_id = args.server_id
            if args.client_id:
                client_id = args.client_id
            if args.tenant_id:
                tenant_id = args.tenant_id
            if args.client_secret:
                client_secret = args.client_secret
            if args.certificate_path:
                certificate_path = args.certificate_path
            if args.environment:
                environment = args.environment

            match authFlow:
                case "device_flow":
                    if None not in [environment, server_id, client_id, tenant_id]:
                        kl.NewDeviceCodeFlow(
                            environment, server_id, client_id, tenant_id
                        )
                    else:
                        raise RequiredArgumentException(
                            environment=environment,
                            server_id=server_id,
                            client_id=client_id,
                            tenant_id=tenant_id,
                        )
                case "interactive":
                    if None not in [environment, server_id, client_id, tenant_id]:
                        kl.NewWebBrowserFlow(
                            environment, server_id, client_id, tenant_id
                        )
                    else:
                        raise RequiredArgumentException(
                            environment=environment,
                            server_id=server_id,
                            client_id=client_id,
                            tenant_id=tenant_id,
                        )
                case "sp_secret":
                    if None not in [
                        environment,
                        server_id,
                        client_id,
                        tenant_id,
                        client_secret,
                    ]:
                        kl.NewSpSecretFlow(
                            environment, server_id, client_id, tenant_id, client_secret
                        )
                    else:
                        raise RequiredArgumentException(
                            environment=environment,
                            server_id=server_id,
                            client_id=client_id,
                            tenant_id=tenant_id,
                            client_secret=client_secret,
                        )
                case "sp_pfx":
                    if None not in [
                        environment,
                        server_id,
                        client_id,
                        tenant_id,
                        certificate_path,
                    ]:
                        kl.NewSpPFXFlow(
                            environment,
                            server_id,
                            client_id,
                            tenant_id,
                            certificate_path,
                        )
                    else:
                        raise RequiredArgumentException(
                            environment=environment,
                            server_id=server_id,
                            client_id=client_id,
                            tenant_id=tenant_id,
                            certificate_path=certificate_path,
                        )
                case "managed_identity":
                    if server_id:
                        kl.NewMSIFlow(server_id)
                    else:
                        raise RequiredArgumentException(server_id=server_id)
                case "managed_identity_id":
                    if None not in [server_id, client_id]:
                        kl.NewMSIClientIdFlow(server_id, client_id)
                    else:
                        raise RequiredArgumentException(
                            server_id=server_id, client_id=client_id
                        )
                case "az_cli":
                    if server_id:
                        kl.NewAzureCliFlow(server_id)
                    else:
                        raise RequiredArgumentException(server_id=server_id)
                case "workload_identity":
                    if server_id:
                        kl.NewWorkLoadIdentityFlow(server_id)
                    else:
                        raise RequiredArgumentException(server_id=server_id)
                case "classic":
                    if None not in [token, client_certificate_data, client_key_data]:
                        kl = ClassicLogin(
                            token=token,
                            client_certificate_data=client_certificate_data,
                            client_key_data=client_key_data,
                        )  # type: ignore
                    else:
                        raise RequiredArgumentException(
                            token=token,
                            client_certificate_data=client_certificate_data,
                            client_key_data=client_key_data,
                        )
            config_yaml["users"][0]["user"] = kl.data
        configs["users"].append(config_yaml["users"][0])  # type: ignore

    return configs


# Set default values on arguments
def set_defaults(args: argparse.Namespace) -> argparse.Namespace:
    """
    The function `set_defaults` processes command line arguments, allowing subscriptions to be a
    comma-separated list and setting the default output format to YAML if neither JSON nor YAML is
    specified.

    :param args: The `args` parameter in the `set_defaults` function is an instance of
    `argparse.Namespace`, which is typically used to store command-line arguments parsed by the
    `argparse` module in Python. This function is designed to set default values for certain arguments
    if they are not provided by the user
    :type args: argparse.Namespace
    :return: The function `set_defaults` is returning the modified `args` object after setting default
    values and processing the subscriptions to be a list.
    """
    # Allow subscriptions to be a comma separated list
    if args.subscriptions is not None:
        args.subscriptions = [s.strip() for s in args.subscriptions.split(",")]
    # Set default output format to yaml
    if not args.json and not args.yaml:
        args.yaml = True
    return args


# Initialize the script
def init() -> Tuple[argparse.Namespace, ChainedTokenCredential]:
    """
    The function `init` parses command line arguments, sets default values, and returns the parsed
    arguments along with an authentication object.
    :return: A tuple containing a `argparse.Namespace` object and a `ChainedTokenCredential` object is
    being returned.
    """
    args = set_defaults(parse_args(sys.argv[1:]))
    return args, auth()


# Main function
def main():
    """
    The main function initializes credentials, retrieves subscriptions, and processes them in parallel
    to obtain cluster credentials for Kubernetes configurations.
    """
    args, credentials = init()
    authFlow = determine_auth_flow(args)
    results = []
    try:
        subs = list_subscriptions(credentials, args.subscriptions, args.verbose)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    if len(subs) <= args.max_threads:
        if args.verbose:
            print(f"Running with {len(subs)} threads")
        p = Pool(processes=len(subs))
    else:
        if args.verbose:
            print(f"Running with {args.max_threads} threads")
        p = Pool(processes=args.max_threads)
    # if args.cluster_name is not None, then run only specific cluster function
    if args.cluster_name != "" and args.cluster_name is not None:
        results.append(
            p.apply_async(
                get_cluster_credentials_for_targeted_cluster,
                args=(credentials, subs[0], authFlow, args),
            )
        )
        p.close()
        p.join()
        clusters = {
            "apiVersion": "v1",
            "kind": "Config",
            "clusters": [],
            "contexts": [],
            "current-context": "",
            "users": [],
        }
        r = flatten([p.get() for p in results])
        for d in r:
            for i in d["clusters"]:
                if i not in clusters["clusters"]:
                    clusters["clusters"].append(i)
            for i in d["contexts"]:
                if i not in clusters["contexts"]:
                    clusters["contexts"].append(i)
            for i in d["users"]:
                if i not in clusters["users"]:
                    clusters["users"].append(i)
        if args.json:
            print_json(clusters, outfile=args.outfile)
        if args.yaml:
            print_yaml(clusters, outfile=args.outfile)
        return
    else:
        for sub in subs:
            result = p.apply_async(
                get_cluster_credentials, args=(credentials, sub, authFlow, args)
            )
            results.append(result)

        [result.wait() for result in results]
        p.close()
        clusters = {
            "apiVersion": "v1",
            "kind": "Config",
            "clusters": [],
            "contexts": [],
            "current-context": "",
            "users": [],
        }
        r = flatten([p.get() for p in results])
        for d in r:
            for i in d["clusters"]:
                if i not in clusters["clusters"]:
                    clusters["clusters"].append(i)
            for i in d["contexts"]:
                if i not in clusters["contexts"]:
                    clusters["contexts"].append(i)
            for i in d["users"]:
                if i not in clusters["users"]:
                    clusters["users"].append(i)
        if args.json:
            print_json(clusters, outfile=args.outfile)
        if args.yaml:
            print_yaml(clusters, outfile=args.outfile)


if __name__ == "__main__":
    main()
