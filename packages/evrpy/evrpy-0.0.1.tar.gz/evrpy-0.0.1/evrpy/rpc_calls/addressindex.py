from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json


class AddressindexRPC:
    """
    A client for interacting with the Evrmore node's address index RPC commands via the `evrmore-cli` command-line interface.

    This class provides functions for querying indexed blockchain data by address, such as balance, UTXO sets, mempool data,
    and transaction IDs associated with given addresses. It is designed to work with an Evrmore node that has address index
    functionality enabled.

    Attributes:
        cli_path (str): Path to the `evrmore-cli` binary.
        datadir (str): Directory containing the Evrmore blockchain data.
        rpc_user (str): RPC username for node authentication.
        rpc_pass (str): RPC password for node authentication.
        testnet (bool): If True, connects to Evrmore testnet instead of mainnet.

    Typical usage example:
        rpc = AddressindexRPC(
            cli_path="/usr/bin/evrmore-cli",
            datadir="/home/user/.evrmore",
            rpc_user="rpcusername",
            rpc_pass="rpcpassword",
            testnet=True
        )
        balance = rpc.getaddressbalance("EVRaddress")
    """

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
            self.cli_path,   # Path to the Evrmore CLI binary
            self.datadir,    # Directory where blockchain data is stored
            self.rpc_user,   # RPC username
            self.rpc_pass,   # RPC password
            self.testnet     # Boolean: use testnet or not
        )

    def getaddressbalance(self, address, includeassets=False):
        """
        Retrieve the current balance and total received amount for a given Evrmore address.

        Queries the Evrmore node (with addressindex enabled) for basic balance information.
        Only base58check-encoded addresses are supported.

        Parameters:
            address (str): The Evrmore address to check.
            includeassets (bool): Return asset balances

        Returns:
            dict: A dictionary containing:
                - "balance" (str): The current balance of the address in satoshis.
                - "received" (str): The total amount received by the address, in satoshis (includes change).
            If an error occurs or the address is invalid, the dictionary will contain an "error" key.

        Example:
            >>> rpc = AddressindexRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> result = rpc.getaddressbalance("12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX", True)
        """

        # Prepare a JSON string with the address to be queried
        query = json.dumps({
            "addresses": [address]
        })

        # Build the command-line arguments for calling `getaddressbalance`
        command = self._build_command() + [
            "getaddressbalance",    # RPC command
            query,                  # JSON-encoded address list
            str(includeassets).lower()   # Boolean flag as a lowercase string
        ]

        try:
            # Execute the command using subprocess.run, capturing stdout/stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Attempt to parse the response from stdout as JSON
                    parsed = json.loads(result.stdout.strip())
                    return parsed      # Return the parsed Python object
                except json.JSONDecodeError:
                    # If output is not valid JSON, return a descriptive error
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # Handle the case where stdout is empty (no data for address)
                return {"error": f"No data available for address {address}.  Verify the address exists"}
        except Exception as e:
            # Catch all other exceptions and return them as errors
            return {"error": str(e)}



    def getaddressdeltas(self, address, start=None, end=None, chaininfo=False, assetname=""):
        """
        Retrieve all change deltas (additions and subtractions) for a given Evrmore address.

        Queries the Evrmore blockchain for a detailed history of balance changes for a specific address,
        optionally filtered by block height range and asset type. Requires the node to be running with
        `addressindex` enabled.

        Parameters:
            address (str): The base58check-encoded address to query deltas for.
            start (int, optional): The starting block height for filtering results (inclusive). If None, includes from genesis.
            end (int, optional): The ending block height for filtering results (inclusive). If None, includes up to the tip.
            chaininfo (bool, optional): If True, includes chain information in the results (applies only when start and end are both specified).
            assetname (str, optional): If given, filters for deltas related to the specified asset name (default is EVR).

        Returns:
            list of dict: Each dictionary describes a change ("delta") with the following keys:
                - "assetName" (str): The asset associated with the delta (e.g., "EVR" for native coin)
                - "satoshis" (int): The difference in satoshis (can be negative or positive)
                - "txid" (str): The transaction ID related to the change
                - "index" (int): The input or output index in the transaction
                - "height" (int): The block height at which this change occurred
                - "address" (str): The base58check-encoded address (same as queried)
            If no data is found or an error occurs, returns a dictionary with an "error" key.

        Example:
            >>> rpc = AddressindexRPC(cli_path="evrmore-cli", datadir="/path", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> deltas1 = rpc.getaddressdeltas("12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX")
            >>> deltas2 = rpc.getaddressdeltas("12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX", start=100000, end=150000, chaininfo=True)
            >>> deltas3 = rpc.getaddressdeltas("12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX", assetname="MY_ASSET")
        """

        # Construct a JSON-encoded string with parameters for the RPC call
        query = json.dumps({
            "addresses": [address],              # List of addresses to query
            "start": start,                      # Block height to start from (must be >= 1)
            "end": end,                          # Block height to end at
            "chainInfo": str(chaininfo).lower(), # Include chain info as 'true'/'false' string
            "assetName": assetname               # Filter deltas by asset name
        })

        # Append the RPC command and parameters to the base CLI command
        command = self._build_command() + [
            "getaddressdeltas",  # The requested RPC method
            query                # JSON string of parameters
        ]

        try:
            # Run the CLI command, capturing standard output and errors
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            if result.stdout:
                try:
                    # Attempt to load the JSON response from stdout
                    parsed = json.loads(result.stdout.strip())
                    return parsed  # Return the parsed data structure
                except json.JSONDecodeError:
                    # Return raw output if JSON parsing failed
                    return {"error": "Recevied non-JSON output", "raw": result.stdout.strip()}
            else:
                # Handle the case where no data was returned (empty output)
                return {"error": f"No data available for address {address}.  Verify address exists"}
        except Exception as e:
            # If there was an error running the command, return the error message
            return {"error": str(e)}


    def getaddressmempool(self, address, includeassets=False):
        """
        Returns all mempool deltas for the specified address.

        Queries the Evrmore node using the `getaddressmempool` RPC command.
        This command requires the `addressindex` to be enabled on the node.

        Parameters:
            address (str): The base58check-encoded Evrmore address to query.
            includeassets (bool, optional): If True, include asset deltas in the response.
                Defaults to False.

        Returns:
            list[dict] or dict:
                If successful, returns a list of dictionaries―each containing:
                    - "address" (str): Queried address
                    - "assetName" (str): Name of associated asset ("EVR" for Evrmore)
                    - "txid" (str): Related transaction ID
                    - "index" (int): Input or output index
                    - "satoshis" (int): Satoshi difference (amount)
                    - "timestamp" (int): Time tx entered the mempool (unix seconds)
                    - "prevtxid" (str, optional): Previous transaction ID (if spending)
                    - "prevout" (str, optional): Previous transaction output index (if spending)

                If there is an error or no data, returns a dictionary containing an "error" key
                and related error info.

        Example:
            >>> rpc = AddressindexRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> mempool1 = rpc.getaddressmempool("12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX")
            >>> mempool2 = rpc.getaddressmempool("12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX", includeassets=True)

        Note:
            - Requires the `addressindex` feature enabled on your Evrmore node.
            - Only supports base58check encoded addresses.
        """

        # Create a JSON object with the address to query the mempool for
        query = json.dumps({
            "addresses": [address]  # List of addresses to search in the mempool
        })

        # Build the command-line arguments for the external tool call
        command = self._build_command() + [
            "getaddressmempool",          # RPC method name
            query,                        # The address parameter as a JSON string
            str(includeassets).lower()    # Optional flag for asset inclusion, as 'true' or 'false'
        ]

        try:
            # Execute the command and capture output and errors
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            if result.stdout:
                try:
                    # Try to parse the standard output as JSON
                    parsed = json.loads(result.stdout.strip())
                    return parsed  # Return the parsed Python object
                except json.JSONDecodeError:
                    # If the output isn't valid JSON, return the error and raw output
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # Handle the case when no data was returned for the address
                return {"error": f"No data available for address {address}.  Verify address exists"}
        except Exception as e:
            # Catch and report any exception that occurs during command execution
            return {"error": str(e)}


    def getaddresstxids(self, address, includeassets=False):
        """
        Returns the transaction IDs (txids) for the specified address.

        This method queries the Evrmore node using the `getaddresstxids` RPC command and requires that addressindex is enabled.

        Arguments:
            address (str): The base58check encoded address to query for transaction IDs.
            includeassets (bool, optional):
                If True, will return an expanded result that includes asset transactions.
                Defaults to False.

        Returns:
            list: A list of transaction IDs (str) associated with the given address.
            dict: If an error occurs, returns a dictionary with an "error" key and a descriptive message.

        Example:
            >>> rpc = AddressindexRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> result1 = rpc.getaddresstxids("12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX", includeassets=True)

        Note:
            This method only takes one address per call, wrapped as a list for compatibility with the underlying API.
        """

        # Construct the JSON query with the target address (must be a list as required by the underlying API)
        query = json.dumps({
            "addresses": [address]
        })

        # Build the full CLI command to call 'getaddresstxids' with the query and includeassets flag
        command = self._build_command() + [
            "getaddresstxids",
            query,
            str(includeassets).lower()  # Converts the Python boolean to "true"/"false" for CLI
        ]

        try:
            # Run the CLI command, capturing stdout and stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            if result.stdout:
                try:
                    # Attempt to parse the command output as JSON and return the parsed data
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    # Handle cases where output is not valid JSON
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # If there's no output, likely no transactions exist for the given address
                return {"error": f"No data available for address {address}.  Verify address exists"}
        except Exception as e:
            # Catch and return any exceptions that occurred during execution
            return {"error": str(e)}



    def getaddressutxos(self, address, chaininfo=False, assetname='*'):
        """
                Returns all unspent outputs (UTXOs) for a given address.

                Requires the Evrmore node to be running with addressindex enabled.

                Parameters:
                    address (str):
                        The base58check encoded address to query for UTXOs.

                    chaininfo (bool, optional):
                        If True, also include chain info with results (default: False).

                    assetname (str, optional):
                        An asset name string to filter UTXOs by a specific asset instead of EVR.
                        Use '*' to fetch for all assets (default: '*').

                Returns:
                    list of dict:
                        Each dict contains:
                            - 'address': The address queried.
                            - 'assetName': The name of the asset for the UTXO (EVR for regular coins).
                            - 'txid': The output transaction ID.
                            - 'height': The block height of the UTXO.
                            - 'outputIndex': The output index in the transaction.
                            - 'script': The script in hex encoding.
                            - 'satoshis': The value of the UTXO in satoshis.

                    dict:
                        In case of an error, a dictionary with an 'error' description and (optionally) the raw output.

                Example:
                >>> rpc = AddressindexRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
                >>> utxos1 = rpc.getaddressutxos("12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX")
                >>> utxos2 = rpc.getaddressutxos("12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX", assetname="MY_ASSET")
                >>> utxos3 = rpc.getaddressutxos("invalid_address")
                """

        # Prepare the request payload as a JSON string
        query = json.dumps({
            "addresses": [address],              # List of addresses to query
            "chainInfo": str(chaininfo).lower(), # Include chain info as 'true'/'false' string
            "assetName": assetname               # Filter UTXOs by asset name
        })

        # Build the full CLI command, specifying the method and the JSON parameters
        command = self._build_command() + [
            "getaddressutxos",   # RPC method name
            query                # JSON parameters as a string
        ]

        try:
            # Execute the command as a subprocess, capturing standard output and error
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            if result.stdout:
                try:
                    # Parse the output as JSON if possible
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    # If output isn't valid JSON, return an error dict with raw output
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # If there's no output, return an error indicating no data is available
                return {"error": f"No data available for address {address}.  Verify address exists"}
        except Exception as e:
            # If command execution fails, return the exception string as an error
            return {"error": str(e)}