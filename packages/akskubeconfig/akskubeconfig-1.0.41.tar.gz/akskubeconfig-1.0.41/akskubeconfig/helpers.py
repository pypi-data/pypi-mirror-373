#!/usr/bin/env python3
import argparse
import json
import yaml


# get the next item in a list after a string match
def nextListItem(lst: list, item: str) -> str:
    """
    This Python function `nextListItem` takes a list and an item as input, and returns the next item in
    the list after the specified item, or None if the item is not found or is the last item in the list.

    :param lst: A list of items in which you want to find the next item after the specified item
    :type lst: list
    :param item: The `item` parameter in the `nextListItem` function is the element in the list `lst`
    for which you want to find the next element in the list
    :type item: str
    :return: The function `nextListItem` is returning the item in the list `lst` that comes immediately
    after the specified `item`. If the specified `item` is not found in the list or if it is the last
    item in the list, the function returns `None`.
    """
    try:
        return lst[lst.index(item) + 1]
    except (IndexError, ValueError):
        return None  # type: ignore


def pluckAuth(d: dict) -> list:
    """
    This Python function pluckAuth takes a dictionary as input and extracts specific keys from it,
    returning a list of corresponding values.

    :param d: A dictionary containing information related to authentication, such as environment,
    apiserver-id, client-id, tenant-id, client-secret, and certificate-path
    :type d: dict
    :return: The `pluckAuth` function returns a list containing the values corresponding to the keys
    "environment", "apiserver-id", "client-id", "tenant-id", "client-secret", and "certificate-path"
    from the input dictionary `d`. If a key is not present in the dictionary, `None` is appended to the
    list instead.
    """
    ans = []
    keys = [
        "environment",
        "apiserver-id",
        "client-id",
        "tenant-id",
        "client-secret",
        "certificate-path",
    ]
    for k in keys:
        ans.append(d.get(k, None))
    return ans


def getNext(lst: list, *args) -> list:
    """
    The function `getNext` takes a list and variable number of arguments, and returns a list of the next
    items in the list corresponding to the provided arguments.

    :param lst: The `lst` parameter in the `getNext` function is expected to be a list
    :type lst: list
    :return: The function `getNext` is returning a list of values obtained by calling the function
    `nextListItem(lst, val)` on each value passed as arguments after the initial list `lst`.
    """
    ans = []
    for _, val in enumerate(args):
        ans.append(nextListItem(lst, val))
    return ans


def overrideDefaults(args: argparse.Namespace, **kwargs) -> list:
    """
    The function `overrideDefaults` takes in arguments and keyword arguments, and returns a list of
    values based on the keyword arguments or default values from the arguments.

    :param args: argparse.Namespace object containing parsed arguments from the command line
    :type args: argparse.Namespace
    """
    ans = []
    for var, val in kwargs.items():
        if val:
            ans.append(val)
        else:
            ans.append(getattr(args, var))
    return ans


# merge multiple lists
def merge(*lists: list) -> list:
    """
    The function `merge` takes in multiple lists and non-list elements, removes duplicates, and returns
    a new list with unique elements from all inputs.

    :param : The `merge` function takes in multiple lists as arguments and combines them into a single
    list, removing any duplicate elements. If a non-list argument is provided, it will be added to the
    final list if it is not already present
    :type : list
    :return: The `merge` function returns a new list that contains all unique elements from the input
    lists.
    """
    new = []
    for l in lists:
        if isinstance(l, list):
            for i in l:
                if i not in new:
                    new.append(i)
        else:
            if l not in new:
                new.append(l)
    return new


# flatten and merge multiple lists
def flatten(*lists: list) -> list:
    """
    The `flatten` function takes in multiple lists as arguments and returns a single flattened list by
    recursively merging nested lists.

    :param : It looks like you have a function named `flatten` that takes in variable number of lists as
    arguments. The function aims to flatten nested lists into a single list. The function checks the
    type of elements in the input lists and raises an exception if it encounters an invalid type
    :type : list
    :return: The `flatten` function is returning the result of calling the `merge` function with the
    unpacked elements of the input lists.
    """
    if lists == []:
        return lists  # type: ignore
    if isinstance(lists[0], list):
        for l in lists:
            if isinstance(l[0], list):
                return flatten(merge(*l))
            if isinstance(l[0], str) or isinstance(l[0], int) or isinstance(l[0], dict):
                pass
            else:
                raise Exception(TypeError("Invalid type in list"))
    return merge(*lists)  # type: ignore


# write to a file
def write(file: str, data: str) -> bool:
    """
    The function `write` takes a file path and data as input, attempts to write the data to the file,
    and returns True if successful or False if an error occurs.

    :param file: The `file` parameter in the `write` function is a string that represents the file path
    where the data will be written to
    :type file: str
    :param data: The `data` parameter in the `write` function is a string that represents the content
    that you want to write to the file specified by the `file` parameter. When you call the `write`
    function, you provide the content you want to write to the file as the `data` argument
    :type data: str
    :return: The function `write` returns a boolean value - `True` if the data was successfully written
    to the file, and `False` if an error occurred during the writing process.
    """
    try:
        with open(file, "w") as f:
            f.write(data)
    except Exception as e:
        print(f"Error: {e}")
        return False
    return True


def determine_auth_flow(args: argparse.Namespace) -> str:
    """
    This Python function determines the authentication flow based on the arguments provided.

    :param args: The `determine_auth_flow` function takes in a namespace object `args` as input and
    determines the authentication flow based on the attributes of the `args` object. The function checks
    various attributes of the `args` object to determine the authentication flow and returns a string
    indicating the type of authentication flow
    :type args: argparse.Namespace
    :return: The function `determine_auth_flow` is returning a string based on the arguments provided.
    The string returned depends on the specific argument that is set to True. If none of the arguments
    are True, the function will return "default".
    """
    if args.default:
        return "default"
    if args.device_flow:
        return "device_flow"
    if args.interactive:
        return "interactive"
    if args.sp_secret:
        return "sp_secret"
    if args.sp_pfx:
        return "sp_pfx"
    if args.managed_identity:
        return "managed_identity"
    if args.managed_identity_id:
        return "managed_identity_id"
    if args.az_cli:
        return "az_cli"
    if args.workload_identity:
        return "workload_identity"
    return "default"


def print_json(clusters: list, **kwargs) -> bool:
    """
    The function `print_json` takes a list of clusters and optional keyword arguments, attempts to
    convert the data to JSON format, and either prints the JSON output or writes it to a file if an
    outfile is provided.

    :param clusters: The `clusters` parameter is expected to be a list that contains the data you want
    to convert to JSON format. This function will attempt to convert this list into a JSON string with
    an indentation of 2 spaces. If successful, it will either print the JSON string to the console or
    write it to
    :type clusters: list
    :return: The function `print_json` returns a boolean value - `True` if the JSON data was
    successfully printed or written to a file, and `False` if there was an error during the process.
    """
    outfile = kwargs.get("outfile", None)
    try:
        # attempt to marshal the data to JSON
        j = json.dumps(clusters, indent=2)
    except Exception as e:
        print(f"Error: {e}")
        return False
    if not outfile:
        print(j)
    # Write to a file if an outfile is provided
    if outfile:
        write(outfile, j)
    return True


def print_yaml(clusters: list, **kwargs) -> bool:
    """
    The function `print_yaml` takes a list of clusters and optional keyword arguments, attempts to
    convert the data to YAML format, and either prints the YAML output or writes it to a file based on
    the provided `outfile` argument.

    :param clusters: The `clusters` parameter is expected to be a list of data that you want to convert
    to YAML format. This function `print_yaml` takes this list as input and converts it to a YAML format
    string. If successful, it either prints the YAML string to the console or writes it to a file
    :type clusters: list
    :return: The function `print_yaml` returns a boolean value - `True` if the data was successfully
    marshaled to YAML and written to a file (if an outfile is provided), and `False` if there was an
    error during the marshaling process.
    """
    outfile = kwargs.get("outfile", None)
    try:
        # attempt to marshal the data to YAML
        y = yaml.dump(clusters)
    except Exception as e:
        print(f"Error: {e}")
        return False
    if not outfile:
        print(y)
    # Write to a file if an outfile is provided
    if outfile:
        write(outfile, y)
    return True
