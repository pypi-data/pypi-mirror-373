<!-- Space: CLDCOE -->
<!-- Parent: NIQ Managed Actions -->
<!-- Type: page -->
<!-- Layout: article -->
# akskubeconfig
<!-- Include: disclaimer.tmpl -->
<!-- Include: ac:toc -->

A utility to generate a kubeconfig file for all AKS clusters in one or more Azure subscriptions.

## Why

Managing and updating a Kubernetes configuration file for AKS clusters can be a
nightmare when you manage multiple clusters across multiple subscriptions. This
tool aims to simplify the process by generating a kubeconfig file for all AKS
clusters that you have access to in all subscriptions that you have access to.

While checking all subscriptions is default behavior, you can also specify a
list of subscriptions to check. This can be useful if you have access to a large
number of subscriptions and only want to check a subset of them.

It also supports generating that kubeconfig file using a number of different
authentication flows, including:

- Default (using the default authentication flow)
- Device Flow (using the device flow authentication flow)
- Interactive (using the interactive web browser authentication flow)
- Service Principal Secret (using a service principal secret to authenticate)
- Service Principal PFX (using a service principal pfx certificate to authenticate)
- Managed Identity (using a managed identity to authenticate)
- Managed Identity ID (using a managed identity to authenticate)
- Azure CLI (using the Azure CLI to authenticate)
- Workload Identity (using a workload identity to authenticate)

This can be useful for a number of reasons, such as generating a bulk kubeconfig
file on-the-fly for CI/CD pipelines, or for generating a kubeconfig file for a
specific cluster in a specific subscription.

## Installation

`akskubeconfig` is implemented in Python. Assuming you have a
Python interpreter and pip installed you should be able to install with:

```shell
pip install akskubeconfig
```

> This has not yet been widely tested and is currently in a _works on my
machine_ state.

## Usage

The simplest usage is to just run the tool and specify an output file for it to write to:

```shell
akskubeconfig -o ~/.kube/config
```

This will generate a set of schemas in a `schemas` directory. The tool
provides a number of options to modify the output:

```shell
akskubeconfig --help
usage: akskubeconfig [-h] [-v] [-s SUBSCRIPTIONS] [--client-id CLIENT_ID] [--tenant-id TENANT_ID] [--client-secret CLIENT_SECRET] [--certificate-path CERTIFICATE_PATH] [--server-id SERVER_ID]
                     [--environment ENVIRONMENT] [--default | --device-flow | --interactive | --sp-secret | --sp-pfx | --managed-identity | --managed-identity-id | --az-cli | --workload-identity]
                     [--json | --yaml] [-m MAX_THREADS] [-o OUTFILE] [--cluster-name CLUSTER_NAME]

options:
  -h, --help            show this help message and exit
  -v, --verbose         Increase output verbosity
  -s, --subscriptions SUBSCRIPTIONS
                        A comma separated list of subscription to use. If omitted, all subscriptions will be checked.
  --client-id CLIENT_ID
                        Override the client id to write into the kubeconfig. Only applicable if required by the selected authentication flow.
  --tenant-id TENANT_ID
                        Override the tenant id to write into the kubeconfig. Only applicable if required by the selected authentication flow.
  --client-secret CLIENT_SECRET
                        Override the client secret to write into the kubeconfig. Only applicable if required by the selected authentication flow.
  --certificate-path CERTIFICATE_PATH
                        Override the certificate path to write into the kubeconfig. Only applicable if required by the selected authentication flow.
  --server-id SERVER_ID
                        Override the server id to write into the kubeconfig.
  --environment ENVIRONMENT
                        Override the environment to write into the kubeconfig.
  --default             Use the default flow authenticate within the generated kubeconfig (default)
  --device-flow         Use device flow to authenticate within the generated kubeconfig
  --interactive         Use the interactive web browser flow to authenticate within the generated kubeconfig
  --sp-secret           Use a service principal secret to authenticate within the generated kubeconfig
  --sp-pfx              Use a service principal pfx certificate to authenticate within the generated kubeconfig
  --managed-identity    Use a managed identity to authenticate within the generated kubeconfig
  --managed-identity-id
                        Use a managed identity to authenticate within the generated kubeconfig
  --az-cli              Use the Azure CLI to authenticate within the generated kubeconfig
  --workload-identity   Use a workload identity to authenticate within the generated kubeconfig
  --json                Output as JSON
  --yaml                Output as YAML (default)
  -m, --max-threads MAX_THREADS
                        Maximum number of threads to use
  -o, --outfile OUTFILE
                        Output file
  --cluster-name CLUSTER_NAME
                        Name of the specific cluster to target (required when using --specific-cluster)
```

<!-- Include: footer.tmpl -->
