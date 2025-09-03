#!/usr/bin/env python3


class RequiredArgumentException(Exception):
    """
    The `RequiredArgumentException` class is designed to handle missing required arguments by generating
    corresponding flags for Azure API authentication.
    """

    def __init__(self, **kwargs) -> None:
        self.flags = []
        for name, value in kwargs.items():
            if value is None:
                match name:
                    case "environment":
                        self.flags.append("--environment")
                    case "server_id":
                        self.flags.append("--server-id")
                    case "client_id":
                        self.flags.append("--client-id")
                    case "tenant_id":
                        self.flags.append("--tenant-id")
                    case "client_secret":
                        self.flags.append("--client-secret")
                    case "certificate_path":
                        self.flags.append("--certificate-path")
        self.message = print(
            "Error: Unable to automatically determine all required values from Azure API. Please try again with the following flags or specify a different authentication flow: %s",
            self.flags,
        )

    def __str__(self):
        return self.message


class UnrecognizedDataStructure(Exception):
    """
    The `UnrecognizedDataStructure` class is designed to handle exceptions related to unrecognized data
    structures encountered during processing.
    """

    def __init__(self, struct: str) -> None:
        self.message = print(f"Unknown data structure: {struct}", struct)

    def __str__(self):
        return self.message
