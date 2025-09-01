# noinspection SpellCheckingInspection
"""
AssetRPC module for Evrmore CLI asset operations.

This class provides a high-level wrapper for asset-related commands
using `evrmore-cli`, including transfers and asset issuance functions.
"""

from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json


# noinspection DuplicatedCode,SpellCheckingInspection,GrazieInspection
class AssetsRPC:
    """
    AssetRPC provides an interface for interacting with the Evrmore blockchain assets via the `evrmore-cli` command-line tool.

    This class wraps common asset-related RPC commands and parses their responses, allowing you to manage, query, and transfer assets on the Evrmore blockchain. It handles command construction, execution, and result parsing, with support for both mainnet and testnet modes.

    Attributes:
        cli_path (str): Path to the `evrmore-cli` binary.
        datadir (str): Path to the Evrmore node data directory.
        rpc_user (str): RPC authentication username.
        rpc_pass (str): RPC authentication password.
        testnet (bool): Run commands on testnet if True; mainnet otherwise.

    Example:
        rpc = AssetRPC(
            cli_path="/path/to/evrmore-cli",
            datadir="/path/to/data",
            rpc_user="user",
            rpc_pass="password",
            testnet=True
        )

        asset_info = rpc.getassetdata("ASSETNAME")

    Methods provide access to:
        - Checking if an address has a specified asset balance.
        - Querying asset metadata.
        - Getting burn addresses.
        - Retrieving cache information.
        - Calculating tolls for asset transactions.
        - Issuing, reissuing, transferring, and updating asset metadata.
        - Listing assets and balances.
        - Other asset operations supported by Evrmore CLI.
    """


    def __init__(self, cli_path, datadir, rpc_user, rpc_pass, testnet=True):
        """
        Initialize a new AssetRPC client instance with connection and authentication details.

        Parameters:
            cli_path (str): Full path to the `evrmore-cli` executable.
            datadir (str): Path to the Evrmore node's data directory.
            rpc_user (str): Username for RPC authentication.
            rpc_pass (str): Password for RPC authentication.`
            testnet (bool, optional): If True, use Evrmore testnet; uses mainnet by default.
        """

        self.cli_path = cli_path     # Path to the Evrmore CLI executable binary
        self.datadir = datadir       # Directory where Evrmore blockchain data is stored
        self.rpc_user = rpc_user     # Username for RPC authentication with the node
        self.rpc_pass = rpc_pass     # Password for RPC authentication with the node
        self.testnet = testnet       # Boolean indicating whether to use testnet mode


    def _build_command(self):
        """
        Create the base command-line argument list to invoke `evrmore-cli` with the current client configuration.

        Returns:
            list: Command-line arguments representing the base CLI call, including authentication and network mode.
        """

        # Build and return the base command-line argument list for Evrmore CLI,
        # using the stored configuration parameters from the instance
        return build_base_command(
            self.cli_path,   # Path to the Evrmore CLI executable
            self.datadir,    # Blockchain data directory
            self.rpc_user,   # RPC username for authentication
            self.rpc_pass,   # RPC password for authentication
            self.testnet     # Boolean to indicate testnet usage
        )


    def addresshasasset(self, address, asset_name, required_quantity=1):
        """
        Check whether a given address holds at least a specified quantity of a particular asset.

        Args:
            address (str): Address to query for asset balance.
            asset_name (str): Name of the asset to check the balance for.
            required_quantity (int or float, optional): The minimum quantity required. Defaults to 1.

        Returns:
            bool: True if the address holds at least the required quantity of the asset, False otherwise.

        """

        command = self._build_command() + [
            "listassetbalancesbyaddress",
            address
        ]

        try:
            # Execute the command and capture the output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Parse the output JSON into a Python dictionary of asset balances
            balances = json.loads(result.stdout.strip())

            # Return True if the specified asset meets or exceeds required_quantity, else False
            return float(balances.get(asset_name, 0)) >= float(required_quantity)
        except Exception as e:
            # Print and handle any errors during execution or parsing
            print(f"Error checking asset balance: {e}")
            return False  # On error, treat as asset not present


    def getassetdata(self, asset_name):
        """
        Retrieve metadata for a specified asset.

        Queries the Evrmore blockchain for metadata about the given asset name.
        Returns a dictionary of all asset fields if the asset exists.

        Parameters:
            asset_name (str): The name of the asset to query.

        Returns:
            dict: Asset metadata with keys such as 'version', 'name', 'amount', 'units',
                  'reissuable', 'has_ipfs', 'ipfs_hash', 'txid_hash', 'verifier_string',
                  'permanent_ipfs_hash', 'permanent_txid_hash', 'toll_amount_mutability',
                  'toll_amount', 'toll_address_mutability', 'toll_address', 'remintable',
                  'total_burned', 'currently_burned', 'reminted_total'.

        Raises:
            RuntimeError: If the asset does not exist or if the command fails.

        Example:
            >>> rpc = AssetRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> data = rpc.getassetdata("NEUBTRINO")
        """

        # Build the command-line argument list to query asset data using the CLI tool
        command = self._build_command() + [
            "getassetdata",
            asset_name
        ]

        try:
            # Execute the constructed command using subprocess, capturing stdout and stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Attempt to parse the CLI's stdout as JSON and return the parsed result
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    # Handle (and report) the case where output is not valid JSON
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # If stdout is empty, the asset was likely not found or wallet is missing data
                return {
                    "error": f"No asset data available for {asset_name}. Verify the asset exists and is in your wallet."}
        except Exception as e:
            # Catch all exceptions (including command errors) and return as an error dictionary
            return {"error": str(e)}


    def getburnaddresses(self):
        # noinspection PyShadowingNames
        """
                Retrieve the list of all Evrmore burn addresses.

                Queries the Evrmore blockchain for all burn addresses currently recognized by the network.
                Returns a dictionary or list mapping nickname(s) to burn addresses.

                Returns:
                    dict or list: Burn addresses in the format {nickname: address, ...}.

                Example:
                    >>> rpc = AssetRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
                    ... testnet=True)
                    >>> result = rpc.getburnaddresses()
                """

        # Build the CLI command to fetch a list of burn addresses from the Evrmore node
        command = self._build_command() + [
            "getburnaddresses"
        ]

        try:
            # Run the command-line process, capturing standard output and error
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                # If output is present, parse the response as JSON and return the data
                return json.loads(result.stdout.strip())
            else:
                # If no output, return an error indicating possible node issues or missing data
                return {"error": "No burn address data returned. Ensure your node is running and synced."}
        except Exception as e:
            # Catch any subprocess or parsing errors and return the error as a dictionary
            return {"error": str(e)}


    def getcacheinfo(self):
        """
        Retrieve general cache information from the Evrmore node.

        Calls the `getcacheinfo` RPC method, which returns cache and system statistics
        related to assets (as plain text).

        Returns:
            str: Cache information output from the node.

        Example:
            >>> rpc = AssetRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> info = rpc.getcacheinfo()
        """

        # Compose the CLI command to fetch node cache information
        command = self._build_command() + [
            "getcacheinfo"
        ]

        try:
            # Execute the CLI command, capturing its standard output and error streams
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                # If output is present, return the trimmed result as a string
                return result.stdout.strip()
            else:
                # If there's no output, return a message indicating the RPC command failed silently
                return "No information available, the getcacheinfo rpc command failed without throwing an Exception"
        except Exception as e:
            # If an error occurs during execution, return the error details as a string
            return f"Error: {e}"


    def getcalculatedtoll(self, asset_name="", amount=100, change_amount=0, overwrite_toll_fee=""):
        """
        Calculate the toll fee and details for transferring an asset.

        This method calls the `getcalculatedtoll` RPC command to determine
        the toll requirements for asset transfers.

        Parameters:
            asset_name (str): The name of the asset. Use "" for default toll calculation.
            amount (float): Amount of the asset being sent.
            change_amount (float): Amount returned as change to the sender.
            overwrite_toll_fee (float): Optional. If supplied, this value will be used as the toll fee.

        Returns:
            dict: Details including toll asset, amount, address, and calculated fee.

        Example:
            >>> rpc = AssetRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> toll = rpc.getcalculatedtoll("ASSET_NAME", 100, 10, 0.05)
        """

        # Build the command to fetch calculated toll information for an asset transfer
        command = self._build_command() + [
            "getcalculatedtoll",
            asset_name,          # Name of the asset being transferred
            str(amount),         # Amount of the asset to transfer (as string)
            str(change_amount),  # Change amount (as string)
            str(overwrite_toll_fee) # Fee override (as string)
        ]

        try:
            # Execute the CLI command and capture output and error
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Parse and return the response as a dictionary (parsed JSON)
                    return json.loads(result.stdout.strip())
                except json.JSONDecodeError as json_err:
                    # If parsing to JSON fails, return a descriptive error
                    return {"error": f"Failed to parse toll data as JSON: {json_err}"}
            else:
                # If there is no output, return an error describing the situation
                return {"error": "No toll data returned."}
        except Exception as e:
            # Catch any runtime errors and return the error message
            return {"error": str(e)}


    def issue(self, asset_name, quantity=1, to_address="", change_address="", units=0, reissuable=True, has_ipfs=False,
              ipfs_hash="", permanent_ipfs_hash="", toll_amount=0, toll_address="", toll_amount_mutability=False,
              toll_address_mutability=False, remintable=True):
        """
        Issue a new asset, subasset, or unique asset on the Evrmore network.

        Calls the `issue` RPC method with the specified parameters to create a new asset.
        Parameters are mostly optional, with defaults provided by the Evrmore node.

        Parameters:
            asset_name (str): The unique asset name (required).
            quantity (int|float): Number of units to issue.
            to_address (str): (Optional) Recipient address for the asset.
            change_address (str): (Optional) Address for EVR change.
            units (int): (Optional) Number of decimal places allowed.
            reissuable (bool): (Optional) If True, allows future issuance.
            has_ipfs (bool): (Optional) Attach an IPFS hash.
            ipfs_hash (str): (Optional) The IPFS hash (required if it has_ipfs is True).
            permanent_ipfs_hash (str): (Optional) Permanent IPFS hash.
            toll_amount (float): (Optional) Amount of toll fee assigned.
            toll_address (str): (Optional) Address to receive the toll fee.
            toll_amount_mutability (bool): (Optional) If True, can change the toll amount.
            toll_address_mutability (bool): (Optional) If True, can change the toll address.
            remintable (bool): (Optional) If True, allows reminting burned assets.

        Returns:
            str: Transaction ID as returned by the Evrmore node, or an error message.

        Example:
            >>> rpc = AssetRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> txid = rpc.issue("ASSET_NAME", 1000, "", "", 0, True, False, "", "", 0, "", False, False, True)
        """

        # Build the command to issue a new asset with all specified parameters
        command = self._build_command() + [
            "issue",
            str(asset_name),                     # Asset name to issue
            str(quantity),                       # Quantity to issue (as string)
            str(to_address),                     # Receiving address for the asset
            str(change_address),                 # Address to send any change to
            str(units),                          # Decimal units (divisibility)
            str(reissuable).lower(),             # Whether the asset can be reissued (converted to lower-case string)
            str(has_ipfs).lower(),               # Whether the asset has an IPFS hash (lower-case string)
            str(ipfs_hash),                      # The IPFS hash (or empty if not used)
            str(permanent_ipfs_hash),            # Permanent IPFS hash (if any)
            str(toll_amount),                    # Toll amount as string
            str(toll_address),                   # Address to receive the toll
            str(toll_amount_mutability).lower(), # Whether the toll amount can be changed (lower-case string)
            str(toll_address_mutability).lower(),# Whether the toll address can be changed (lower-case string)
            str(remintable).lower()              # Whether the asset is remintable (lower-case string)
        ]

        try:
            # Execute the constructed CLI command for asset issuance
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            if result.stdout:
                try:
                    # Attempt to parse returned output as JSON (expects a list of transaction IDs)
                    txids = json.loads(result.stdout.strip())
                    if isinstance(txids, list):
                        # Join transaction IDs into a single comma-separated string if it's a list
                        return ", ".join(txids)
                    else:
                        # Otherwise, return the string representation
                        return str(txids)
                except json.JSONDecodeError:
                    # If parsing as JSON fails, return the raw output
                    return result.stdout.strip()
            else:
                # If there is no output, return an appropriate message
                return "No information available"
        except Exception as e:
            # Catch any errors raised during command execution and return the error message
            return f"Error: {e}"


    def issueunique(self, root_name, asset_tags, ipfs_hashes, to_address="", change_address="",
                    permanent_ipfs_hashes="", toll_address="", toll_amount=0, toll_amount_mutability=False,
                    toll_address_mutability=False):
        """
        Issue one or more unique assets under an existing root asset.

        Calls the `issueunique` RPC command to create unique assets,
        each tagged with a unique identifier. Additional data such as IPFS hashes and
        permanent hashes can be associated with each tag if desired.

        Parameters:
            root_name (str): The root asset name (must be owned by the caller).
            asset_tags (list of str): Unique tags for each issued asset (required).
            ipfs_hashes (list of str, optional): IPFS hashes or txid hashes for each tag (must match asset_tags in length if given).
            to_address (str, optional): Address for assets to be sent to (a new address is generated if not provided).
            change_address (str, optional): Address for EVR change (a new address is generated if not provided).
            permanent_ipfs_hashes (list of str, optional): Permanent IPFS hashes, one for each asset tag.
            toll_address (str, optional): Address for tolls to be paid to.
            toll_amount (float, optional): Toll amount to be paid when the asset is transferred.
            toll_amount_mutability (bool, optional): If True, allows changing the toll amount in the future.
            toll_address_mutability (bool, optional): If True, allows changing the toll address in the future.

        Returns:
            str: Transaction ID as returned by the Evrmore node, or an error message.

        Example:
            >>> rpc = AssetRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> txid = rpc.issueunique(root_name="MY_ASSET", asset_tags=["primo", "secundo"],
            ... ipfs_hashes=["QmFirst", "QmSecond"], to_address="", change_address="")
        """

        # Build the command to issue unique (NFT-like) assets under a root asset name
        command = self._build_command() + [
            "issueunique",
            str(root_name),                           # Root asset under which unique assets will be created
            json.dumps(asset_tags),                   # List of unique asset tags (JSON-encoded)
            json.dumps(ipfs_hashes),                  # Corresponding IPFS hashes for each unique asset (JSON-encoded)
            str(to_address),                          # Destination address for all issued unique assets
            str(change_address),                      # Change address for leftover EVR
            json.dumps(permanent_ipfs_hashes),        # (Optional) permanent IPFS hashes (JSON-encoded)
            str(toll_address),                        # Address to receive the toll (fee)
            str(toll_amount),                         # The toll amount to pay for the issue
            str(toll_amount_mutability).lower(),      # Whether toll amount can be changed (as a string, lower case)
            str(toll_address_mutability).lower()      # Whether toll address can be changed (as a string, lower case)
        ]

        try:
            # Execute the CLI command and capture output (stdout, stderr)
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            if result.stdout:
                try:
                    # Try to parse the output as JSON (expecting a list of txids)
                    txids = json.loads(result.stdout.strip())
                    if isinstance(txids, list):
                        # If a list, combine the transaction IDs into a comma-separated string
                        return ", ".join(txids)
                    else:
                        # For any other JSON result, just return its string representation
                        return str(txids)
                except json.JSONDecodeError:
                    # If the output isn’t valid JSON, return the raw text output
                    return result.stdout.strip()
            else:
                # Standard case for no output from the CLI tool
                return "No information available"
        except Exception as e:
            # Provide a helpful error message if command execution fails at any point
            return f"Error: {e}"



    def listaddressesbyasset(self, asset_name, only_total=False, count=50000, start=0):
        """
        Returns a list of all addresses that own the given asset (with balances),
        or, if only_total is True, returns the number of addresses who own the asset.

        Arguments:
            asset_name (str): Name of the asset to query.
            only_total (bool): If True, return only the number of addresses.
            count (int): Maximum number of results to return (max 50000).
            start (int): Offset to start the results from (can be negative to count from the end).

        Returns:
            dict: {address: balance, ...}
            or
            int: count of addresses (if only_total is True)

        Examples:
            >>> rpc = AssetRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> address_balances = rpc.listaddressesbyasset(asset_name="ASSET_NAME", only_total=False, count=2, start=0)
            >>> total_count = rpc.listaddressesbyasset(asset_name="ASSET_NAME", only_total=True)

        """

        # Build command to list addresses associated with a particular asset
        command = self._build_command() + [
            "listaddressesbyasset",
            str(asset_name),                # The asset for which to list addresses
            str(only_total).lower(),        # Whether to only return the total (as a lower-case string)
            str(count),                     # How many results to include
            str(start)                      # Result offset for paging
        ]

        try:
            # Execute the command and capture the result
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            if result.stdout:
                data = result.stdout.strip()

                try:
                    # Try to parse output as JSON (expected for address lists)
                    parsed = json.loads(data)
                    return parsed
                except json.JSONDecodeError:
                    # If JSON decoding fails, check if it’s a single integer (for only_total=True)
                    try:
                        return int(data)
                    except ValueError:
                        # Unexpected output format; return as error
                        return {"error": f"Unexpected format: {data}"}
            else:
                # No output was returned
                return {"error": "No information available."}
        except Exception as e:
            # Handle any execution error and return as error message
            return {"error": str(e)}


    def listassetbalancesbyaddress(self, address, onlytotal=False, count=50000, start=0):
        """
        Returns a list of all asset balances for a given Evrmore address,
        or, if only_total is True, returns the number of assets held at the address.

        Arguments:
            address (str): Evrmore address to query.
            onlytotal (bool): If True, return only the number of asset types held by the address.
            count (int): Maximum number of results to return (max 50000).
            start (int): Result offset (can be negative to count from end).

        Returns:
            dict: {asset_name: quantity, ...}
            or
            int: count of asset types (if only_total is True)

        Examples:
            >>> rpc = AssetRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> variable1 = rpc.listassetbalancesbyaddress("myaddress", onlytotal=False, count=2, start=0)
            >>> variable2 = rpc.listassetbalancesbyaddress("myaddress", onlytotal=True)
            >>> variable3 = rpc.listassetbalancesbyaddress("myaddress")
            >>> variable4 = rpc.listassetbalancesbyaddress("address-does-not-exist")
        """

        # Build the command to list asset balances for a specific address
        command = self._build_command() + [
            "listassetbalancesbyaddress",
            str(address),                # The address to query
            str(onlytotal).lower(),      # Whether to return only the total count (as string)
            str(count),                  # How many results to return
            str(start)                   # Result offset, for paging
        ]

        try:
            # Execute the CLI command and capture standard output/error
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            if result.stdout:
                data = result.stdout.strip()

                try:
                    # Attempt to parse the output as JSON, for normal queries
                    parsed = json.loads(data)
                    return parsed
                except json.JSONDecodeError:
                    # If onlytotal is True, the output could be a single integer as a string
                    try:
                        return int(data)
                    except ValueError:
                        # Unexpected output format, return an error
                        return {"error": f"Unexpected format: {data}"}
            else:
                # Handle empty output case
                return {"error": "No information available"}
        except Exception as e:
            # Any error during command execution is caught and returned as an error message
            return {"error": str(e)}

    def listassets(self, asset="*", verbose=False, count=None, start=0):
        """
        Returns a list of all assets, optionally filtered and with metadata.

        This method calls the `listassets` RPC command to retrieve asset names,
        or, if `verbose` is True, detailed metadata for each asset. Filtering
        by asset name or prefix is supported. Pagination via count and start
        is also supported.

        Arguments:
            asset (str): Asset name filter (wildcard `*` allowed, default matches all).
            verbose (bool): If True, return metadata per asset; if False, return list of asset names.
            count (int|None): Maximum number of results to return (default: all).
            start (int): Index to start from (can be negative for offset from end).

        Returns:
            list: List of asset names if verbose=False.
            dict: {asset_name: {amount, units, reissuable, ...}, ...} if verbose=True.
            dict: Error object in case of failure.

        Examples:
            >>> rpc = AssetRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> variable1 = rpc.listassets("MYASSET")
            >>> variable2 = rpc.listassets("MYASSET*", verbose=True)
            >>> variable3 = rpc.listassets()
            >>> variable4 = rpc.listassets("*", verbose=True, count=2, start=1)
            >>> variable5 = rpc.listassets("NOEXISTENTASSET")
        """

        # Build the CLI command to list assets
        command = self._build_command() + [
            "listassets",
            str(asset),                  # Asset name or a pattern to filter results
            str(verbose).lower(),        # Whether verbose output is desired (as a lowercase string)
            str(count),                  # Maximum number of results to return
            str(start)                   # Result offset (for paging)
        ]

        try:
            # Execute the command and capture output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                data = result.stdout.strip()
                try:
                    # Parse the output as JSON and return it
                    return json.loads(data)
                except json.JSONDecodeError:
                    # If output isn't valid JSON, return an error with raw data
                    return {"error": f"Unexpected format: {data}"}
            else:
                # If no output, return a standard error message
                return {"error": "No information available"}
        except Exception as e:
            # Handle any error during the command execution
            return {"error": str(e)}


    def listmyassets(self, asset="*", verbose=False, count=None, start=0, confs=0):
        """
        Returns a list of all assets owned by this wallet, optionally with balances and outpoints.

        This method calls the `listmyassets` RPC command to list owned assets, optionally filtered
        by asset name (supports wildcards), with pagination and confirmation controls.

        Arguments:
            asset (str): Asset name filter (wildcard '*' allowed; default matches all owned assets).
            verbose (bool): If True, returns detailed outpoints per asset; if False, returns only asset balances.
            count (int or None): Truncate results to include only the first `count` assets (default: all).
            start (int): Skip this many assets at the start (can be negative for offset from end).
            confs (int): Minimum confirmations required for asset outputs (default: 0).

        Returns:
            dict: If verbose is False, {asset_name: balance, ...}
            dict: If verbose is True,
                {
                    asset_name: {
                        'balance': balance,
                        'outpoints': [
                            {'txid': str, 'vout': int, 'amount': float},
                            ...
                        ]
                    },
                    ...
                }
            dict: Error object if the call fails.

        Examples:
            >>> rpc = AssetRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> variable1 = rpc.listmyassets('MYASSET*', verbose=True, count=2, start=0, confs=1)

        Notes:
            - This call only returns assets held (owned) by *this wallet's* addresses.
            - Use `verbose=True` to fetch transaction-level detail for each asset balance.
            - Filtering with wildcards is allowed, but can be expensive if too broad.
        """

        # Build the command to list the caller's assets matching filters
        command = self._build_command() + [
            "listmyassets",              # Command to list assets owned by the calling wallet
            str(asset),                  # Optional: filter by asset name or pattern
            str(verbose).lower(),        # Whether to show detailed output ("true"/"false")
            str(count),                  # Maximum number of results to return
            str(start),                  # Result offset for paging
            str(confs)                   # Minimum required confirmations for assets
        ]

        try:
            # Execute the CLI command and collect the output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            if result.stdout:
                # Return the trimmed output string if available
                return result.stdout.strip()
            else:
                # No output means no information was retrieved
                return "No information available"
        except Exception as e:
            # Catch and return any errors that occurred during execution
            return f"Error: {e}"


    def reissue(self, asset_name, qty, to_address, change_address, reissuable=True, new_units=-1, new_ipfs="",
                new_permanent_ipfs_hash="", change_toll_amount=False, new_toll_amount=0, new_toll_address="",
                new_toll_amount_mutability=True, new_toll_address_mutability=True):
        # noinspection PyRedeclaration
        """
                Reissue an asset you own to a given address, with optional updates to asset parameters.

                This command allows increasing the supply of an owned asset, and can update properties like
                reissuable flag, units, IPFS hash, and any toll settings if supported by the protocol.

                Arguments:
                    asset_name (str): Name of the asset to reissue (must own the Owner Token).
                    qty (float|int): Amount of asset to reissue.
                    to_address (str): Address to send the new assets.
                    change_address (str): (Optional) Address to send any transaction change.
                    reissuable (bool): (Optional, default=True) If new units can be reissued in future.
                    new_units (int): (Optional, default=-1) New decimal places for asset, or -1 to keep existing.
                    new_ipfs (str): (Optional, default="") Set a new IPFS hash (will overwrite existing if set).
                    new_permanent_ipfs_hash (str): (Optional, default="") New permanent IPFS hash (RIP5/standardization).
                    change_toll_amount (bool): (Optional, default=False) Whether toll amount is being changed.
                    new_toll_amount (float|int): (Optional, default=0) New toll amount, if change_toll_amount is true.
                    new_toll_address (str): (Optional, default="") New toll address, if changing.
                    new_toll_amount_mutability (bool): (Optional, default=True) If new toll amount may be changed in future.
                    new_toll_address_mutability (bool): (Optional, default=True) If new toll address may be changed in future.

                Returns:
                    str: The transaction ID ("txid") on success, or an error message string on failure.

                Examples:
                    >>> rpc = AssetRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
                    ... testnet=True)
                    >>> txid = rpc.reissue("MYASSET", 20, "n2rx...abcd", "n2rx...abcd")
                    >>> txid = rpc.reissue("MYASSET", 10, "n2rx...abcd", "n2rx...abcd", reissuable=False, new_units=4)
                    >>> txid = rpc.reissue("MYASSET", 5, "n2rx...abcd", "n2rx...abcd", new_ipfs="Qm...",
                    ... new_permanent_ipfs_hash="Qp...")
                    >>> txid =  rpc.reissue("MYASSET", 50, "n2rx...abcd", "n2rx...abcd", change_toll_amount=True,
                    ... new_toll_amount=0.5, new_toll_address="n1toll...xyz", new_toll_amount_mutability=False, new_toll_address_mutability=False)
                    >>> txid =  rpc.reissue("NOT_OWNED_ASSET", 10, "n2rx...a", "n2rx...a")

                Notes:
                    - You must own the Owner Token for the asset to perform a reissue.
                    - Not all fields are supported for all assets/protocol versions; see Evrmore asset spec.
                    - Some fields (like toll changes) are only relevant to special asset types or evolutions.
                    - 'change_address' is frequently set to your own receiving address for most scenarios.
                """

        # Build the command to reissue an asset with updated parameters.
        command = self._build_command() + [
            "reissue",                                  # Command to reissue the asset
            str(asset_name),                            # Name of the asset to reissue
            str(qty),                                   # Quantity to add
            str(to_address),                            # Recipient address for reissued asset
            str(change_address),                        # Change address for EVR change
            str(reissuable).lower(),                    # Whether further reissuance is allowed ("true"/"false")
            str(new_units),                             # New decimal units for the asset
            str(new_ipfs),                              # New IPFS/metadata hash (if updating)
            str(new_permanent_ipfs_hash),               # Optionally set a permanent IPFS hash
            str(change_toll_amount).lower(),            # Whether to change the toll amount
            str(new_toll_amount),                       # New toll amount if applicable
            str(new_toll_address),                      # New address to receive tolls
            str(new_toll_amount_mutability).lower(),    # If toll amount can be changed in future
            str(new_toll_address_mutability).lower()    # If toll address can be changed in future
        ]

        try:
            # Execute the command and capture output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            if result.stdout:
                # Attempt to parse output as JSON (which should be a list of transaction IDs)
                txids = json.loads(result.stdout.strip())

                if isinstance(txids, list):
                    # If the result is a list, join all TXIDs into a comma-separated string
                    return ", ".join(txids)
                else:
                    # Otherwise, return the string representation directly
                    return str(txids)
            else:
                # No transaction or output was returned
                return "No transaction returned."
        except Exception as e:
            # If an error occurs, return an error message
            return f"Error: {e}"


    def remint(self, asset_name, qty, to_address, change_address="", update_remintable=True):
        # noinspection PyRedeclaration
        """
                Remint previously burned units of an asset if you own the Owner Token.

                This command allows the asset Owner to remint (restore) asset units that have been burned,
                and optionally lock further reminting (by disabling the 'remintable' flag).

                Args:
                    asset_name (str): Name of the asset to remint.
                    qty (float|int): Number of units to remint.
                    to_address (str): Address to receive the reminted assets.
                    change_address (str): (Optional) Address for EVR change from the transaction.
                    update_remintable (bool): (Optional, default=True) If False, disables future reminting.

                Returns:
                    str: The transaction ID (txid) on success, or a string starting with "Error: ..." on failure.

                Examples:
                    >>> rpc = AssetRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
                    ... testnet=True)
                    >>> txid = rpc.remint("MYASSET", 10, "n2rx...abcd", "n2rx...abcd")
                    >>> txid = rpc.remint("MYASSET", 25, "n2rx...abcd", "n2rx...abcd", update_remintable=False)
                    >>> txid = rpc.remint("NOT_OWNED_ASSET", 1, "n2rx...a", "n2rx...a", False)


                Notes:
                    - You must own the Owner Token for the asset to remint supplies.
                    - Use update_remintable=False to permanently disable further reminting for this asset.
                    - The amount reminted cannot exceed the amount previously burned.
                    - change_address is usually one of your own addresses.
                """

        # Build the command to remint additional units of an existing asset.
        command = self._build_command() + [
            "remint",                          # Command for reminting an asset
            str(asset_name),                   # Asset name being reminted
            str(qty),                          # Quantity to add
            str(to_address),                   # Recipient address for the reminted units
            str(change_address),               # Address for any change returned
            str(update_remintable).lower()     # Specifies if remintability flag is updated ("true"/"false")
        ]

        try:
            # Execute the CLI command and capture output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            if result.stdout:
                # Parse command output as JSON (expecting a list of transaction IDs)
                txids = json.loads(result.stdout.strip())

                if isinstance(txids, list):
                    # If output is a list, join all TXIDs as a comma-separated string
                    return ", ".join(txids)
                else:
                    # Otherwise, just convert to string and return
                    return str(txids)
            else:
                # No output was returned
                return "No transaction returned."
        except Exception as e:
            # Return a string describing any error that occurred
            return f"Error: {e}"

    def transfer(self, asset_name, qty, to_address, message="", expire_time="", change_address="", asset_change_address=""):
        # noinspection PyRedeclaration
        """
                Transfer a quantity of an asset you own to a specified address.

                This method sends a selected amount of the asset to a target address.
                Optionally, you may attach a message/hash and set change addresses.

                Args:
                    asset_name (str): The asset to transfer.
                    qty (int|float): Quantity of asset to send.
                    to_address (str): Recipient's address.
                    message (str, optional): Message or hash (default: "").
                    expire_time (int, optional): UTC timestamp when message expires (default: 0).
                    change_address (str, optional): Address for Evrmore (EVR) change (default: "").
                    asset_change_address (str, optional): Address for asset change (default: "").

                Returns:
                    str: Transaction ID (txid), or error string.

                Examples:
                    # Basic asset transfer from wallet
                    >>> rpc = AssetRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
                    ... testnet=True)
                    >>> txid = rpc.transfer("MYASSET",5,"miAddrDest...")
                    >>> txid = rpc.transfer("MYASSET",20,"miAddrDest...",message="QmAbc...xyz",expire_time=1675334200)
                    >>> txid = rpc.transfer("MYASSET",1,"miAddrDest...",change_address="miMyChange...",
                    ... asset_change_address="miMyChange...")
                    >>> txid = rpc.transfer("NOASSET",50,"miAddrDest...")  # doctest: +ELLIPSIS
                """

        # Build the command to transfer an asset to the specified address.
        command = self._build_command() + [
            "transfer",                        # Command to execute an asset transfer
            str(asset_name),                   # Name of the asset being transferred
            str(qty),                          # Amount to transfer
            str(to_address),                   # Destination address for the transfer
            str(message),                      # Optional message to include with the transfer
            str(expire_time),                  # Expiration time for the transfer (if applicable)
            str(change_address),               # Address to receive change from EVR funds, if any
            str(asset_change_address)          # Address to receive asset change, if any
        ]

        try:
            # Execute the CLI command and capture the result
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            if result.stdout:
                # Parse the output (expecting a JSON string with transaction IDs)
                txids = json.loads(result.stdout.strip())

                if isinstance(txids, list):
                    # If the result is a list, join TXIDs into a comma-separated string
                    return ", ".join(txids)
                else:
                    # Otherwise, just return the result as a string
                    return str(txids)
            else:
                # No output returned, inform the user
                return "No transaction returned."
        except Exception as e:
            # Return a string error message on failure
            return f"Error: {e}"

    def transferfromaddress(self, asset_name, from_address, quantity, to_address,
                            message="", expire_time="", evr_change_address="", asset_change_address=""):
        # noinspection PyRedeclaration
        """
                Transfer a quantity of an asset from a specific address you control to another address.

                Allows you to specify which "from_address" the asset comes from, and supports sending
                a message (IPFS, txid, or other), setting an expiration, and explicit EVR/asset change addresses.

                Args:
                    asset_name (str): The asset to transfer.
                    from_address (str): The funding address for the asset.
                    quantity (int|float): The quantity of asset to send.
                    to_address (str): The recipient address.
                    message (str, optional): Message or hash to attach (default: "").
                    expire_time (int, optional): UTC timestamp expiration (default: 0 = none).
                    evr_change_address (str, optional): Address for EVR change (default: "").
                    asset_change_address (str, optional): Address for asset change (default: "").

                Returns:
                    str: Transaction ID (txid), or an error string if failed.

                Examples:
                    >>> rpc = AssetRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
                    ... testnet=True)
                    >>> txid = rpc.transferfromaddress("MYASSET", "miAddr1...", 1, "miAddr2...")
                    >>> txid = rpc.transferfromaddress("MYASSET", "miAddr1...", 2, "miAddr2...", "SomeNote", 0,
                    ... evr_change_address="miAddr1...", asset_change_address="miAddr1...")
                    >>> txid = rpc.transferfromaddress("FAKEASSET", "miAddrX...", 100, "miAddrY...")


                Notes:
                    - from_address must have sufficient asset balance.
                    - If a message is non-empty, it is included if protocol allows (e.g., after RIP5).
                    - EVR and asset change addresses may be left blank for auto-selection.
                """

        # Construct the command to transfer assets from a specific address.
        command = self._build_command() + [
            "transferfromaddress",              # Command to transfer from a specified address
            str(asset_name),                    # Name of the asset to be transferred
            str(from_address),                  # Source address
            str(quantity),                      # Quantity to transfer
            str(to_address),                    # Recipient address
            str(message),                       # Optional message for the transaction
            str(expire_time),                   # Transaction expiration time
            str(evr_change_address),            # Address for any EVR change
            str(asset_change_address)           # Address for any asset change
        ]

        try:
            # Run the CLI command and capture its output.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            if result.stdout:
                try:
                    # Attempt to parse the output as JSON. Expecting a list of transaction IDs.
                    txids = json.loads(result.stdout.strip())
                    if isinstance(txids, list):
                        # If output is a list, combine TXIDs into a comma-separated string.
                        return ", ".join(txids)
                    else:
                        # If not a list, just return as string.
                        return str(txids)
                except json.JSONDecodeError:
                    # If output is not valid JSON, return it as stripped text.
                    return result.stdout.strip()
            else:
                # Output is empty or missing.
                return "No information available"
        except Exception as e:
            # Handle and return any error that occurs.
            return f"Error: {e}"


    def transferfromaddresses(self, asset_name, from_addresses, qty, to_address, message="", expire_time="",
                              evr_change_address="", asset_change_address=""):
        # noinspection PyRedeclaration
        """
                Transfer a quantity of an owned asset from one or more specific addresses to a target address.

                This method sends a specified quantity of your asset(s) to a given address,
                sourcing the asset only from the provided list of "from" addresses.
                Attach an optional message or hash, and specify change addresses if desired.

                Args:
                    asset_name (str): Name of the asset to send.
                    from_addresses (list[str]): List of addresses to send from.
                    qty (int|float): Quantity of asset to send.
                    to_address (str): Address to send to.
                    message (str, optional): Message or hash (default: "").
                    expire_time (int, optional): UTC expiration timestamp for message (default: 0).
                    evr_change_address (str, optional): Send EVR change here (default: "").
                    asset_change_address (str, optional): Send leftover asset here (default: "").

                Returns:
                    str: Transaction ID if successful, or error message.

                Examples:
                    >>> rpc = AssetRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
                    ... testnet=True)
                    >>> txid = rpc.transferfromaddresses("MYASSET", ["miSender1..."], 3, "miDestAddr...")
                    >>> txid = rpc.transferfromaddresses("MYASSET", ["miSender1...", "miSender2..."], 15,"miDestAddr...",
                    ... message="Qm...", expire_time=1700000000)
                    >>> txid = rpc.transferfromaddresses("MYASSET", ["miSender1..."], 2,"miDestAddr...",
                    ... evr_change_address="miEvR...", asset_change_address="miAssetChg...")
                    >>> txid = rpc.transferfromaddresses("NOASSET", ["miSender..."], 50, "miDestAddr...")  # doctest: +ELLIPSIS

                Notes:
                    - Asset must be present in all the provided addresses.
                    - If change addresses are blank, the system will choose one.
                    - Message feature requires protocol support.
                """

        # Build the command to transfer an asset from multiple addresses.
        command = self._build_command() + [
            "transferfromaddresses",                # Command for transferring from multiple addresses
            str(asset_name),                        # Asset to be transferred
            json.dumps(from_addresses),             # List of source addresses (serialized to JSON)
            str(qty),                              # Quantity to transfer
            str(to_address),                       # Recipient address
            str(message),                          # Optional message for the transaction
            str(expire_time),                      # Transaction expiration time (if applicable)
            str(evr_change_address),               # Address to receive EVR change (if any)
            str(asset_change_address)              # Address to receive asset change (if any)
        ]

        try:
            # Run the CLI command and capture its output.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            if result.stdout:
                # Parse the output as JSON, expecting a list of transaction IDs (TXIDs).
                txids = json.loads(result.stdout.strip())

                if isinstance(txids, list):
                    # Return the TXIDs as a comma-separated string if output is a list.
                    return ", ".join(txids)
                else:
                    # Otherwise, return the result as a string.
                    return str(txids)
            else:
                # If no output, notify that no transaction was returned.
                return "No transaction returned."
        except Exception as e:
            # Return an error message if something goes wrong.
            return f"Error: {e}"

    def updatemetadata(self, asset_name, change_address="", ipfs_hash="", permanent_ipfs="", toll_address="",
                       change_toll_amount=False, new_toll_amount=-1, toll_amount_mutability=True,
                       toll_address_mutability=True):
        # noinspection PyRedeclaration
        """
                Update the metadata of an asset on the Evrmore blockchain.

                This operation allows alteration of an asset's metadata, such as IPFS hashes or toll configuration.
                Requires the owner token, and after execution returns the transaction id if successful.

                Args:
                    asset_name (str): Name of the asset to update.
                    change_address (str, optional): Address for change outputs (default: "").
                    ipfs_hash (str, optional): New IPFS hash (default: "").
                    permanent_ipfs (str, optional): New permanent IPFS hash (irreversible; default: "").
                    toll_address (str, optional): Address to receive toll fees (default: "").
                    change_toll_amount (bool, optional): Whether to modify toll amount (default: False).
                    new_toll_amount (int|float, optional): New toll amount (default: -1).
                    toll_amount_mutability (bool, optional): If the toll amount can be changed after this update (default: True).
                    toll_address_mutability (bool, optional): If the toll address can be changed after this update (default: True).

                Returns:
                    str: The transaction ID if successful, or an error message.

                Examples:
                    >>> rpc = AssetRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
                    ... testnet=True)
                    >>> txid = rpc.updatemetadata("MYASSET")
                    >>> txid = rpc.updatemetadata("MYASSET", ipfs_hash="QmTestHash123")
                    >>> txid = rpc.updatemetadata("MYASSET", permanent_ipfs="QmPermHashXYZ")
                    >>> txid = rpc.updatemetadata("MYASSET", toll_address="miToll...", change_toll_amount=True,
                    ... new_toll_amount=100,toll_amount_mutability=False, toll_address_mutability=False)
                    >>> txid = rpc.updatemetadata("MYASSET", change_address="miChange...")


                Notes:
                    - The asset owner token must be held in your wallet to perform updates.
                    - Setting a permanent IPFS hash is irreversible.
                    - Use toll options to manage paid access to asset transfers.
                    - If parameters are omitted (empty string or defaults), their value is not changed.
                    - Returns an error string on failure.
                """

        # Build the command to update metadata for an asset.
        command = self._build_command() + [
            "updatemetadata",                           # Command for updating asset metadata
            str(asset_name),                            # Name of the asset to update
            str(change_address),                        # Address for transaction change
            str(ipfs_hash),                             # New IPFS hash for the asset metadata
            str(permanent_ipfs),                        # Indicates if the IPFS hash is permanent
            str(toll_address),                          # Toll address, if used
            str(change_toll_amount).lower(),            # Whether the toll amount is changing, as a lowercase string
        ]

        # If toll amount change is requested, include new toll settings in the command.
        if change_toll_amount:
            command += [
                str(new_toll_amount),                   # New toll amount
                str(toll_amount_mutability).lower(),    # Is the toll amount mutable?
                str(toll_address_mutability).lower()    # Is the toll address mutable?
            ]

        try:
            # Execute the command and capture its output.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            if result.stdout:
                # Parse output (expecting a JSON list of transaction IDs).
                txids = json.loads(result.stdout.strip())
                if isinstance(txids, list):
                    # Return TXIDs as a comma-separated string if a list.
                    return ", ".join(txids)
                else:
                    # Else, return the string representation.
                    return str(txids)
            else:
                # If no output, notify the user.
                return "No transaction returned."
        except Exception as e:
            # Return an error message if something goes wrong.
            return f"Error: {e}"

