from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json


class RestrictedRPC:

    def __init__(self, cli_path, datadir, rpc_user, rpc_pass, testnet=True):
        """
                        Initialize a new AssetRPC client instance with connection and authentication details.

                        Parameters:
                            cli_path (str): Full path to the `evrmore-cli` executable.
                            datadir (str): Path to the Evrmore node's data directory.
                            rpc_user (str): Username for RPC authentication.
                            rpc_pass (str): Password for RPC authentication.
                            testnet (bool, optional): If True, use Evrmore testnet; uses mainnet by default.
                        """

        # Store the path to the Evrmore CLI executable
        self.cli_path = cli_path

        # Store the directory where blockchain data is located
        self.datadir = datadir

        # Store the RPC username for authentication
        self.rpc_user = rpc_user

        # Store the RPC password for authentication
        self.rpc_pass = rpc_pass

        # Specify whether to use the testnet network
        self.testnet = testnet


    def _build_command(self):
        """
        Create the base command-line argument list to invoke `evrmore-cli` with the current client configuration.

        Returns:
            list: Command-line arguments representing the base CLI call, including authentication and network mode.
        """

        # Call the function to construct the base CLI command for Evrmore,
        # passing in all required configuration parameters from the instance
        return build_base_command(
            self.cli_path,  # Path to the Evrmore CLI binary
            self.datadir,  # Directory where blockchain data is stored
            self.rpc_user,  # RPC username
            self.rpc_pass,  # RPC password
            self.testnet  # Boolean: use testnet or not
        )

    def viewmyrestrictedaddresses(self):
        """
        Lists all wallet-owned addresses that have a restriction event (restricted or derestricted).

        Invokes the `viewmyrestrictedaddresses` RPC and returns the wallet’s addresses that have
        experienced a restriction status change. For each address, the **most recent** event
        (restriction or derestriction) is returned along with the asset name and the UTC timestamp.

        Mirrors native help:

            viewmyrestrictedaddresses

        Result (array of objects):
            {
              "Address:"                   (string) The address that was restricted
              "Asset Name:"                (string) The asset that the restriction applies to
              "[Restricted|Derestricted]:" (string) UTC datetime of the event in the format "YY-mm-dd HH:MM:SS"
                                            (Only the most recent restriction/derestriction event will be returned for each address)
            }, ...

        Returns:
            list[dict] | str:
                - On success: a list of dictionaries, each containing:
                    * "Address:" (str)
                    * "Asset Name:" (str)
                    * Either "Restricted:" or "Derestricted:" (str, UTC timestamp "YY-mm-dd HH:MM:SS")
                - If output is not valid JSON, returns the raw string.
                - On error, returns "Error: <message>".

        Notes:
            - The third key is mutually exclusive: you will get **either** "Restricted:" **or**
              "Derestricted:" for each object, indicating the most recent event type.
            - Timestamps are UTC and use a two-digit year format ("YY-mm-dd HH:MM:SS").
            - No arguments; this inspects the **current wallet** only.

        Example:
            >>> rpc = RestrictedRPC(cli_path="evrmore-cli", datadir="/evrmore",rpc_user="user", rpc_pass="pass", testnet=True)
            >>> rows = rpc.viewmyrestrictedaddresses()
        """

        # Build the CLI command with auth/network flags + RPC name (no parameters).
        command = self._build_command() + [
            "viewmyrestrictedaddresses",
        ]

        try:
            # Execute the RPC; capture stdout/stderr. Non-zero exit codes raise CalledProcessError.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout; guard against None and strip whitespace/newlines for parsing.
            out = (result.stdout or "").strip()
            if not out:
                # The RPC returned nothing (unexpected on success). Bubble up an informative message.
                return "No restricted address events found."

            # Attempt to parse JSON. Expected form is a list of objects.
            try:
                parsed = json.loads(out)
                # Return parsed JSON as-is (list[dict] or dict). Callers can iterate or serialize further.
                return parsed
            except json.JSONDecodeError:
                # Node returned non-JSON (rare). Surface raw string for transparency.
                return out

        except Exception as e:
            # Concise error reporting (matches your preferred style).
            return f"Error: {e}"

    def viewmytaggedaddresses(self):
        """
        Lists all wallet-owned addresses that have a tag assignment event (assigned or removed).

        Invokes the `viewmytaggedaddresses` RPC and returns the wallet’s addresses that have
        experienced a tag status change. For each address, the **most recent** event
        (tag assigned or tag removed) is returned along with the tag (asset) name and the UTC timestamp.

        Mirrors native help:

            viewmytaggedaddresses

        Result (array of objects):
            {
              "Address:"               (string) The address that was tagged
              "Tag Name:"              (string) The asset name (qualifier tag, typically starts with '#')
              "[Assigned|Removed]:"    (string) UTC datetime of the event in the format "YY-mm-dd HH:MM:SS"
                                       (Only the most recent tagging/untagging event will be returned for each address)
            }, ...

        Returns:
            list[dict] | str:
                - On success: a list of dictionaries, each containing:
                    * "Address:" (str)
                    * "Tag Name:" (str)
                    * Either "Assigned:" or "Removed:" (str, UTC timestamp "YY-mm-dd HH:MM:SS")
                - If output is not valid JSON, returns the raw string.
                - On error, returns "Error: <message>".

        Notes:
            - The third key is mutually exclusive per object: you will get **either** "Assigned:"
              **or** "Removed:", indicating the most recent event type for that address.
            - Timestamps are UTC and use a two-digit year format ("YY-mm-dd HH:MM:SS").
            - No arguments; this inspects the **current wallet** only.
            - “Tag Name:” refers to a qualifier-asset tag (e.g., "#KYC").

        Example:
            >>> rpc = RestrictedRPC(cli_path="evrmore-cli", datadir="/evrmore",rpc_user="user", rpc_pass="pass", testnet=True)
            >>> rows = rpc.viewmytaggedaddresses()
        """

        # Build the CLI command with auth/network flags + RPC name (no parameters).
        command = self._build_command() + [
            "viewmytaggedaddresses",
        ]

        try:
            # Execute the RPC; capture stdout/stderr. Non-zero exit codes raise CalledProcessError.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout; guard against None and trim whitespace/newlines for parsing.
            out = (result.stdout or "").strip()
            if not out:
                # The RPC returned nothing (unexpected on success). Bubble up an informative message.
                return "No tagged address events found."

            # Attempt to parse JSON. Expected form is a list of objects (one per address).
            try:
                parsed = json.loads(out)
                return parsed
            except json.JSONDecodeError:
                # Node returned non-JSON (rare). Surface raw string for transparency.
                return out

        except Exception as e:
            # Concise error reporting (matches your preferred style).
            return f"Error: {e}"
