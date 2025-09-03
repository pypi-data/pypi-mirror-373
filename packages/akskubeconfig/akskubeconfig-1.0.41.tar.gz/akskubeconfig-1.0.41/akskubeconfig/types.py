#!/usr/bin/env python3


# The `Kubelogin` class in Python defines methods for setting up different authentication flows with
# specific parameters for obtaining tokens in Kubernetes environments.
# structure source: https://azure.github.io/kubelogin/cli/get-token.html
class Kubelogin:
    def __init__(self):
        """
        The function initializes a dictionary with specific key-value pairs related to a Kubernetes login
        command.
        """
        self.data = dict()
        self.data["exec"] = dict()
        self.data["exec"]["command"] = "kubelogin"
        self.data["exec"]["apiVersion"] = "client.authentication.k8s.io/v1beta1"
        self.data["exec"][
            "installHint"
        ] = """
        kubelogin is not installed which is required to connect to AAD enabled cluster.
        
        To learn more, please go to https://aka.ms/aks/kubelogin
        """
        self.data["exec"]["provideClusterInfo"] = False

    def NewDeviceCodeFlow(
        self, environment: str, server_id: str, client_id: str, tenant_id: str
    ):
        """
        The function `NewDeviceCodeFlow` sets up arguments for getting a token with specific environment,
        server ID, client ID, and tenant ID.

        :param environment: The `environment` parameter in the `NewDeviceCodeFlow` function likely refers to
        the environment in which the device code flow is being initiated. This could be a development,
        testing, staging, or production environment, depending on the context in which the function is being
        used
        :type environment: str
        :param server_id: The `server_id` parameter typically refers to the identifier of the server or
        resource that the code is interacting with. It is used to specify the target server or resource for
        the operation being performed
        :type server_id: str
        :param client_id: Client ID is a unique identifier assigned to the client application that is
        requesting access to a resource server. It is typically obtained when registering the client
        application with an identity provider or authorization server
        :type client_id: str
        :param tenant_id: The `NewDeviceCodeFlow` function seems to be setting up some data for a
        command-line operation related to getting a token. The parameters passed to the function are
        `environment`, `server_id`, `client_id`, and `tenant_id`
        :type tenant_id: str
        """
        self.data["exec"]["args"] = [
            "get-token",
            "--environment",
            environment,
            "--server-id",
            server_id,
            "--client-id",
            client_id,
            "--tenant-id",
            tenant_id,
        ]

    def NewWebBrowserFlow(
        self, environment: str, server_id: str, client_id: str, tenant_id: str
    ):
        """
        The function `NewWebBrowserFlow` sets up arguments for obtaining a token using interactive login in
        a web browser.

        :param environment: The `environment` parameter typically refers to the specific environment or
        instance of the web application that the code is interacting with. This could be a development,
        staging, or production environment, for example. It is used to specify where the authentication
        token should be obtained from
        :type environment: str
        :param server_id: The `server_id` parameter typically refers to the identifier of the server or
        resource that the web browser flow is interacting with. It is used to specify the target server or
        resource for authentication and authorization purposes
        :type server_id: str
        :param client_id: The `client_id` parameter is typically a unique identifier assigned to the client
        application by the authorization server when the client is registered. It is used to identify the
        client when making requests to the authorization server for authentication and authorization
        purposes
        :type client_id: str
        :param tenant_id: The `tenant_id` parameter typically refers to the unique identifier for a tenant
        within a multi-tenant application or system. It is used to distinguish between different tenants who
        are using the same application or service. Each tenant would have its own separate data,
        configurations, and resources within the shared application environment
        :type tenant_id: str
        """
        self.data["exec"]["args"] = [
            "get-token",
            "--login",
            "interactive",
            "--environment",
            environment,
            "--server-id",
            server_id,
            "--client-id",
            client_id,
            "--tenant-id",
            tenant_id,
        ]

    def NewSpSecretFlow(
        self,
        environment: str,
        server_id: str,
        client_id: str,
        tenant_id: str,
        client_secret: str,
    ):
        """
        The function `NewSpSecretFlow` sets up a data structure with specific arguments for obtaining a
        token using a service principal secret flow.

        :param environment: The `NewSpSecretFlow` function seems to be setting up a secret flow for a
        service principal in a specific environment. The function takes the following parameters:
        :type environment: str
        :param server_id: The `server_id` parameter typically refers to the identifier of the server or
        service that the code is interacting with. It is used to uniquely identify the server within the
        context of the application or system. This identifier is often required when authenticating or
        authorizing access to the server
        :type server_id: str
        :param client_id: The `client_id` parameter is typically a unique identifier assigned to a client
        application when it is registered with an identity provider or authentication service. It is used to
        identify the client application when making requests for authentication tokens or accessing
        resources
        :type client_id: str
        :param tenant_id: The `tenant_id` parameter in the `NewSpSecretFlow` function refers to the unique
        identifier of the tenant (organization) for which the client application is requesting access. This
        identifier is used in the authentication process to ensure that the client is authorized to access
        resources on behalf of that specific tenant
        :type tenant_id: str
        :param client_secret: The `NewSpSecretFlow` function seems to be setting up a secret flow for a
        service principal in a specific environment. The `client_secret` parameter is a sensitive piece of
        information that should be kept confidential. It is typically a long string of characters that
        serves as a password for the client application
        :type client_secret: str
        """
        self.data["exec"]["env"] = None
        self.data["exec"]["args"] = [
            "get-token",
            "--login",
            "spn",
            "--environment",
            environment,
            "--server-id",
            server_id,
            "--client-id",
            client_id,
            "--client-secret",
            client_secret,
            "--tenant-id",
            tenant_id,
        ]

    def NewSpPFXFlow(
        self,
        environment: str,
        server_id: str,
        client_id: str,
        tenant_id: str,
        certificate_path: str,
    ):
        """
        The function `NewSpPFXFlow` sets up a new service principal flow with specified parameters.

        :param environment: The `NewSpPFXFlow` function seems to be setting up a new service principal flow
        with the provided parameters. The `environment` parameter likely refers to the environment in which
        the service principal will be used, such as "production", "development", etc
        :type environment: str
        :param server_id: The `server_id` parameter in the `NewSpPFXFlow` method likely refers to the
        identifier or name of the server for which the token is being requested. It is used as part of the
        arguments passed to the command line tool or function to specify the server ID
        :type server_id: str
        :param client_id: The `client_id` parameter in the `NewSpPFXFlow` method refers to the unique
        identifier assigned to the client application that is requesting access to a resource. It is
        typically used in authentication and authorization processes to identify the client application
        :type client_id: str
        :param tenant_id: The `tenant_id` parameter in the `NewSpPFXFlow` method refers to the unique
        identifier of the tenant in Azure Active Directory (AAD) to which the service principal belongs.
        This identifier is used to specify the AAD tenant when authenticating and authorizing access to
        resources
        :type tenant_id: str
        :param certificate_path: The `NewSpPFXFlow` method seems to be setting up a new service principal
        flow with the provided parameters. The `certificate_path` parameter likely refers to the path where
        the client certificate is stored on the file system. This certificate is used for authentication in
        the service principal flow
        :type certificate_path: str
        """
        self.data["exec"]["env"] = None
        self.data["exec"]["args"] = [
            "get-token",
            "--login",
            "spn",
            "--environment",
            environment,
            "--server-id",
            server_id,
            "--client-id",
            client_id,
            "--client-certificate",
            certificate_path,
            "--tenant-id",
            tenant_id,
        ]

    def NewMSIFlow(self, server_id: str):
        """
        The function `NewMSIFlow` sets the arguments for retrieving a token using Managed Service Identity
        (MSI) with a specified server ID.

        :param server_id: The `server_id` parameter in the `NewMSIFlow` method is a string that represents
        the ID of the server for which a token is being requested
        :type server_id: str
        """
        self.data["exec"]["args"] = [
            "get-token",
            "--login",
            "msi",
            "--server-id",
            server_id,
        ]

    def NewMSIClientIdFlow(self, server_id: str, client_id: str):
        """
        This function sets up a new MSI client ID flow with the specified server ID and client ID.

        :param server_id: The `server_id` parameter is a string that represents the identifier of the server
        for which the token is being requested in the `NewMSIClientIdFlow` method
        :type server_id: str
        :param client_id: The `client_id` parameter is a unique identifier assigned to the client
        application that is requesting access to a resource server. It is typically used in authentication
        and authorization processes to verify the identity of the client application
        :type client_id: str
        """
        self.data["exec"]["args"] = [
            "get-token",
            "--login",
            "msi",
            "--server-id",
            server_id,
            "--client-id",
            client_id,
        ]

    def NewAzureCliFlow(self, server_id: str):
        """
        This function sets up a new Azure CLI flow with a specified server ID to get a token for
        authentication.

        :param server_id: The `NewAzureCliFlow` function seems to be setting up a flow for executing a
        specific command in the Azure CLI. The `server_id` parameter is likely used to specify the server ID
        for which the token needs to be retrieved. This server ID will be passed as an argument to the Azure
        :type server_id: str
        """
        self.data["exec"]["env"] = None
        self.data["exec"]["args"] = [
            "get-token",
            "--login",
            "azurecli",
            "--server-id",
            server_id,
        ]

    def NewWorkLoadIdentityFlow(self, server_id: str):
        """
        The function `NewWorkLoadIdentityFlow` sets the `env` key to `None` and the `args` key to a list of
        arguments for getting a token with workload identity using the provided server ID.

        :param server_id: The `server_id` parameter is a string that represents the unique identifier of a
        server. It is used in the `NewWorkLoadIdentityFlow` method to set the `server_id` value in the
        `args` dictionary key of the `data` attribute
        :type server_id: str
        """
        self.data["exec"]["env"] = None
        self.data["exec"]["args"] = [
            "get-token",
            "--login",
            "workloadidentity",
            "--server-id",
            server_id,
        ]


# The `Kubelogin` class in Python defines methods for classic kubeconfig login with specific parameters
class ClassicLogin:
    def __init__(self, token: str, client_certificate_data: str, client_key_data: str):
        """
        The function initializes a dictionary with token, client certificate data, and client key data as
        key-value pairs.

        :param token: The `token` parameter is a string that represents an authentication token used for
        authorization purposes in a client-server communication. It is typically a unique identifier that
        grants access to certain resources or services
        :type token: str
        :param client_certificate_data: The `client_certificate_data` parameter in the `__init__` method is
        a string that represents the client certificate data. This data is typically used for client
        authentication in secure communication protocols like HTTPS. It contains information about the
        client's identity and public key
        :type client_certificate_data: str
        :param client_key_data: The `client_key_data` parameter in the `__init__` method is used to store
        the client key data in the `self.data` dictionary. This data could be related to client
        authentication or encryption in a client-server communication setup. It is typically used along with
        the `client_certificate_data`
        :type client_key_data: str
        """
        self.data = dict()
        self.data["token"] = token
        self.data["client-certificate-data"] = client_certificate_data
        self.data["client-key-data"] = client_key_data
