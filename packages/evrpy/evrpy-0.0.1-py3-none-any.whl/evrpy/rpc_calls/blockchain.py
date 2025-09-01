from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json

class BlockchainRPC:

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


    def clearmempool(self):
        """
        Remove all transactions from the mempool.
        This method issues the `clearmempool` command via `evrmore-cli`, instructing the node to clear its in-memory transaction pool.
        Useful for developers, testing, or operational scenarios where you need to force a mempool reset.

        Returns:
            str: A message confirming the mempool has been cleared, or an error message if the operation failed.

        Examples:
            >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> result = rpc.clearmempool()
        """
        # Build the command by combining the base CLI arguments with the 'clearmempool' action
        command = self._build_command() + [
            "clearmempool"
        ]

        try:
            # Execute the command using subprocess, capturing standard output and errors
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Return the cleaned output message, or a default message if output is empty
            if result.stdout.strip():
                return result.stdout.strip()
            else:
                return {"message": "Mempool cleared with no output"}
        except Exception as e:
            # Return any exception error as a dictionary
            return {"error": str(e)}


    def decodeblock(self, blockhex):
        """
        Decode a hex-encoded Evrmore block and display its structured contents
        Equivalent to the `evrmore-cli decodeblock` command

        Args:
            blockhex (str): The block hex string to decode. This is a required argument

        Returns:
            dict: A dictionary containing block data fields, such as:
                - hash (str): The block hash (matches provided hash).
                - size (int): The block size in bytes.
                - strippedsize (int): The block size excluding witness data.
                - weight (int): The block weight as defined in BIP 141.
                - height (int): The block's height (index).
                - version (int): The block version.
                - versionHex (str): Hexadecimal representation of the version.
                - merkleroot (str): Merkle root hash.
                - tx (list of str): Transaction IDs in the block.
                - time (int): Block timestamp (seconds since epoch).
                - nonce (int): Block nonce.
                - bits (str): Compact target representation
            If an error occurs or the output is not valid JSON, an error dictionary is returned instead.

            Examples:
            >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> result = rpc.decodeblock("blockhex")
        """
        # Build the full command to call the 'decodeblock' RPC with the given block hex
        command = self._build_command() + [
            "decodeblock",
            str(blockhex)
        ]

        try:
            # Execute the command as a subprocess, capturing standard output and error
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Attempt to parse the output as JSON (should be a decoded block dictionary)
                    parsed = json.loads(result.stdout.strip())
                    return parsed  # Return the decoded block data as a Python dictionary
                except json.JSONDecodeError:
                    # Output was not valid JSON, so return an error dictionary with the raw output
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # No data was returned; likely the block hex was invalid or unknown
                return {"error": f"No data available for block hex {blockhex}.  Verify information"}
        except Exception as e:
            # Catch and return any exception that occurs during the subprocess execution as an error dictionary
            return {"error": str(e)}


    def getbestblockhash(self):
        """
        Returns the hash of the best (tip) block in the longest blockchain.

        This method calls the `getbestblockhash` RPC command, which is equivalent
        to running `evrmore-cli getbestblockhash`. It returns the block hash (hex encoded)
        of the current tip of the chain.

        Returns:
            str: The best block hash (hex encoded) representing the current tip of the blockchain.
            If the command fails, it raises an exception or logs an error message.


        Example:
            >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> result = rpc.getbestblockhash()
        """
        command = self._build_command() + [
            "getbestblockhash"
        ]

        try:
            # Execute the command using subprocess, capturing standard output and errors
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Return the cleaned output message, or a default message if output is empty
            if result.stdout.strip():
                return result.stdout.strip()
            else:
                return {"message": "No available best block hash"}
        except Exception as e:
            # Return any exception error as a dictionary
            return {"error": str(e)}


    def getblock(self, blockhash, verbosity=1):
        """
        Retrieve detailed information about a specific block in the blockchain.

        This method wraps the `getblock` RPC command for Evrmore, providing block information
        at three different verbosity levels:
        - verbosity=0: Returns the serialized, hex-encoded string for the block.
        - verbosity=1 (default): Returns a dictionary with basic block info.
        - verbosity=2: Returns a dictionary with block info and extended data for each transaction.

        Args:
            blockhash (str): The block hash to retrieve.
            verbosity (int, optional): Level of detail to return.
                - 0: Hex-encoded block data (as a string)
                - 1: JSON object with block details (default)
                - 2: JSON object with block details and full transaction data

        Returns:
            dict or str:
                - If verbosity=0: Returns a string of serialized, hex-encoded block data.
                - If verbosity=1: Returns a dictionary with the block's details (hash, confirmations, size, height, tx ids, etc).
                - If verbosity=2: As above, but `tx` field contains full transaction objects.
                - In case of errors or unexpected output, returns a dictionary with an "error" key.

        Example:
            >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
        ... testnet=True)
            >>> block = rpc.getblock("00000000c937983704a73af28acdec37b049d214adbda81d7e2a3dd146f6ed09")
        """

        # Build the command-line argument list to invoke `evrmore-cli getblock`.
        # Starts with the base command containing authentication and network settings (via _build_command).
        # Appends the 'getblock' command, the block hash as a string, and the verbosity as a string.
        # The final 'command' list is suitable to pass to subprocess for execution.
        command = self._build_command() + [
            "getblock",
            str(blockhash),
            str(verbosity)
        ]

        try:
            # Execute the command as a subprocess, capturing standard output and error
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Attempt to parse the output as JSON (should be a decoded block dictionary)
                    parsed = json.loads(result.stdout.strip())
                    return parsed  # Return the decoded block data as a Python dictionary
                except json.JSONDecodeError:
                    # Output was not valid JSON, so return an error dictionary with the raw output
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # No data was returned; likely the block hex was invalid or unknown
                return {"error": f"No data available for block hash {blockhash}.  Verify information"}
        except Exception as e:
            # Catch and return any exception that occurs during the subprocess execution as an error dictionary
            return {"error": str(e)}


    def getblockchaininfo(self):
        """
        Returns an object containing various state info regarding blockchain processing.

        This method invokes the `getblockchaininfo` RPC, which retrieves comprehensive details
        about the current state and configuration of the blockchain node.

        Returns:
            dict: An object containing the following fields:
                - chain (str): Current network name as defined in BIP70 (e.g., 'main', 'test', 'regtest').
                - blocks (int): Current number of blocks processed in the server.
                - headers (int): Current number of validated headers.
                - bestblockhash (str): Hash of the currently best block.
                - difficulty (float): The current difficulty.
                - mediantime (int): Median time for the current best block.
                - verificationprogress (float): Estimate of verification progress [0..1].
                - chainwork (str): Total amount of work in active chain, as a hexadecimal string.
                - size_on_disk (int): Estimated size of the block and undo files on disk.
                - pruned (bool): Whether blocks are subject to pruning.
                - pruneheight (int, optional): Lowest-height complete block stored (if pruning is enabled).
                - automatic_pruning (bool, optional): Whether automatic pruning is enabled (if applicable).
                - prune_target_size (int, optional): The target size used by pruning.
                - softforks (list): Status of softforks in progress.
                - bip9_softforks (dict): Status of BIP9 softforks in progress.
                - warnings (str): Any network and blockchain warnings.

        Example:
            >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> result = rpc.getblockchaininfo()

        """

        # Build the base Evrmore CLI command with authentication and network options,
        # then append the "getblockchaininfo" RPC method to the argument list.
        command = self._build_command() + [
            "getblockchaininfo"
        ]

        try:
            # Execute the command as a subprocess, capturing standard output and error
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Attempt to parse the output as JSON (should be a decoded block dictionary)
                    parsed = json.loads(result.stdout.strip())
                    return parsed  # Return the blockchain info data as a Python dictionary
                except json.JSONDecodeError:
                    # Output was not valid JSON, so return an error dictionary with the raw output
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # No data was returned
                return {"error": f"No data available from the blockchain.  Verify information"}
        except Exception as e:
            # Catch and return any exception that occurs during the subprocess execution as an error dictionary
            return {"error": str(e)}


    def getblockcount(self):
        """
        Returns the number of blocks in the longest blockchain.

        This RPC call executes 'getblockcount', returning the current block height.

        Returns:
            int: The current block count as an integer, representing the total number of blocks in the longest blockchain.
            If the call fails, it raises an exception or returns an error message as part of the logs.


        Example output:
            {
                "message": "123456"
            }

        Example:
            >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> result = rpc.getblockcount()
        """

        # Build the CLI command to query the current block count
        command = self._build_command() + [
            "getblockcount"
        ]

        try:
            # Execute the command using subprocess, capturing standard output and errors
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Return the cleaned output message, or a default message if output is empty
            if result.stdout.strip():
                return result.stdout.strip()
            else:
                return {"message": "No available blockcount"}
        except Exception as e:
            # Return any exception error as a dictionary
            return {"error": str(e)}


    def getblockhash(self, height):
        """
        Returns the hash of the block in the best-block-chain at the specified height.

        This method wraps the Evrmore 'getblockhash' RPC command. The returned value is the block hash at
        the given height in the active chain.

        Args:
            height (int): The height index of the block to query.

        Returns:
            str: The block hash as a hexadecimal string.

        Example:
            >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> result = rpc.getblockhash(1036542)
        """


        command = self._build_command() + [
            "getblockhash",
            str(height)
        ]

        try:
            # Execute the command using subprocess, capturing standard output and errors
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Return the cleaned output message, or a default message if output is empty
            if result.stdout.strip():
                return result.stdout.strip()
            else:
                return {"message": "No available height"}
        except Exception as e:
            # Return any exception error as a dictionary
            return {"error": str(e)}


    def getblockhashes(self, high, low, noOrphans=True, logicalTimes=True):
        """
        Returns hashes of blocks mined within the specified timestamp range.

        This method calls the Evrmore 'getblockhashes' RPC, which returns an array of block hashes
        or (if logicalTimes option is set) a dictionary with blockhash and logical timestamp fields.

        Args:
            high (int): The newer (upper) block timestamp.
            low (int): The older (lower) block timestamp.
            options (dict): A dictionary specifying options. Example:
                {
                    "noOrphans": True,       # Only include blocks on the main chain
                    "logicalTimes": True     # Include logical timestamps with each hash
                }

        Returns:
            list or dict:
                - If logicalTimes is False, returns a list of block hash strings.
                - If logicalTimes is True, returns a list of dictionaries with
                  'blockhash' and 'logicalts' fields.

        Example:
            >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> rpc.getblockhashes(1231614698, 1231024505, {"noOrphans": True})
        """

        query = json.dumps({
            "noOrphans": noOrphans,  # Option to include or exclude orphan blocks in the query
            "logicalTimes": logicalTimes  # Option to use logical timestamps in the results
        })

        command = self._build_command() + [
            "getblockhashes",  # RPC method to retrieve block hashes in a time range
            str(high),         # Upper (newest) block timestamp as a string
            str(low),          # Lower (oldest) block timestamp as a string
            query              # Query options encoded as a JSON string
        ]


        try:
            # Execute the command using subprocess, capturing standard output and errors
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Return the cleaned output message, or a default message if output is empty
            if result.stdout.strip():
                try:
                    parsed = json.loads(result.stdout)
                    return parsed
                except json.JSONDecodeError as err:
                    return {"error": f"Invalid JSON output: {err}", "raw": result.stdout}
            else:
                return {"message": "No available blockhashes"}
        except Exception as e:
            # Return any exception error as a dictionary
            return {"error": str(e)}


    def getblockheader(self, hash, verbose=True):
        """
        Retrieve information about a specific block header using the `getblockheader` RPC command.

        This method queries the Evrmore node for the block header identified by its hash.
        If `verbose` is True (default), the result is a dictionary with detailed block header information.
        If `verbose` is False, the result is a serialized, hex-encoded string for the block header.

        Args:
            hash (str): The block hash (required).
            verbose (bool, optional): If True (default), returns structured JSON info.
                If False, returns hex-encoded data as a string.

        Returns:
            dict or str:
                - If verbose=True: Returns a dictionary with block header details such as hash, height, confirmations, version, merkleroot, time, nonce, bits, difficulty, chainwork, previous/next block hash, etc.
                - If verbose=False: Returns a string that is serialized, hex-encoded data for the block header.
                - On error, returns a dictionary with an "error" key and details.

        Evrmore-cli CLI reference:
            getblockheader "hash" ( verbose )

            - "hash":          (string, required) The block hash
            - verbose:         (boolean, optional, default=true) true for a json object, false for the hex encoded data

        Example:
            >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> header = rpc.getblockheader("00000000c937983704a73af28acdec37b049d214adbda81d7e2a3dd146f6ed09")
        """

        # Compose the command to call 'evrmore-cli getblockheader' with the provided hash and verbosity.
        # The command list includes base CLI args, the RPC command name, the block hash, and the verbosity flag as a lowercase string.
        command = self._build_command() + [
            "getblockheader",
            str(hash),
            str(verbose).lower()
        ]

        try:
            # Execute the CLI command using subprocess, capturing standard output and error streams.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout.strip():
                try:
                    # If output is non-empty, attempt to parse as JSON.
                    parsed = json.loads(result.stdout)
                    return parsed
                except json.JSONDecodeError as err:
                    # If output is not valid JSON, return an error with the raw output.
                    return {"error": f"Invalid JSON output: {err}", "raw": result.stdout}
            else:
                # Handle case where there is no informational output from the command.
                return {"message": "No available information"}
        except Exception as e:
            # Catch any unexpected exceptions (including CLI or system errors) and return as an error message.
            return {"error": str(e)}


    def getchaintips(self):
        """
        Retrieve information about all known chain tips in the block tree using the `getchaintips` RPC command.

        This method queries the Evrmore node to list the tips of all known branches in the block tree. This includes:
            - the active main chain,
            - orphaned branches (forks),
            - and headers that have not yet been fully validated.

        Each tip provides its height, hash, length of the branch it represents, and status (e.g., active, valid-fork, etc.).

        Returns:
            dict:
                - On success: A dictionary containing a list of chain tip dictionaries.
                  Each tip includes:
                      - height (int): The height of the chain tip.
                      - hash (str): The block hash of the chain tip.
                      - branchlen (int): The number of blocks in the branch since it diverged from the main chain.
                      - status (str): The validation state of the branch. One of:
                            "active", "valid-fork", "valid-headers", "headers-only", "invalid".
                - On malformed JSON output: A dictionary with "error" and "raw" keys.
                - On failure: A dictionary with an "error" key containing exception details.

        Evrmore-cli CLI reference:
            getchaintips

            - Returns information about all known tips in the block tree.

            Possible `status` values:
                - "invalid"       – Contains at least one invalid block.
                - "headers-only"  – Only headers are known, full blocks unavailable.
                - "valid-headers" – Fully available blocks but not validated.
                - "valid-fork"    – Fully validated fork but not on main chain.
                - "active"        – Tip of the active main chain.

        Example:
            >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> tips = rpc.getchaintips()
        """

        # Construct the complete command by combining the base command (including authentication details)
        # with the specific "getchaintips" RPC call. This command, when executed, retrieves details about
        # the tips of all branches in the blockchain tree, including the active one and any forks.
        command = self._build_command() + [
            "getchaintips"
        ]

        try:
            # Execute the CLI command using subprocess, capturing standard output and error streams.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout.strip():
                try:
                    # If output is non-empty, attempt to parse as JSON.
                    parsed = json.loads(result.stdout)
                    return parsed
                except json.JSONDecodeError as err:
                    # If output is not valid JSON, return an error with the raw output.
                    return {"error": f"Invalid JSON output: {err}", "raw": result.stdout}
            else:
                # Handle case where there is no informational output from the command.
                return {"message": "No available information"}
        except Exception as e:
            # Catch any unexpected exceptions (including CLI or system errors) and return as an error message.
            return {"error": str(e)}


    def getchaintxstats(self, nblocks=43800, blockhash=None):
        """
        Compute statistics about the number and rate of transactions in the blockchain using the `getchaintxstats` RPC command.

        This method queries the Evrmore node for historical transaction statistics over a specified window of blocks.
        The window can be customized by setting the number of blocks (`nblocks`) and the block hash that ends the window (`blockhash`).
        If neither argument is provided, statistics are computed using the default window ending at the chain tip.

        Args:
            nblocks (int, optional): Size of the window in number of blocks. If None, the default is used (43800 blocks, approx. one month).
            blockhash (str, optional): Hash of the block that ends the window. If None, the chain tip is used.

        Returns:
            dict:
                - On success: A dictionary with chain transaction statistics, including:
                    - "time": Timestamp of the final block in the window.
                    - "txcount": Total number of transactions up to that point.
                    - "window_block_count": Number of blocks in the window.
                    - "window_tx_count": Number of transactions in the window (if block count > 0).
                    - "window_interval": Time in seconds between first and last block (if block count > 0).
                    - "txrate": Average transactions per second (if interval > 0).
                - On malformed JSON output: A dictionary with "error" and "raw" keys.
                - On failure: A dictionary with an "error" key containing exception details.

        Evrmore-cli CLI reference:
            getchaintxstats ( nblocks blockhash )

            - nblocks (optional): Window size in number of blocks. Default is approx. one month.
            - blockhash (optional): Hash of block that ends the window.

        Example:
            >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> stats = rpc.getchaintxstats()
        """

        # Construct the command based on which arguments were provided
        if blockhash == None and nblocks != None:
            # Case: only nblocks is provided; pass nblocks as the sole argument
            command = self._build_command() + [
                "getchaintxstats",
                str(nblocks)
            ]
        elif nblocks == None and blockhash != None:
            # Case: only blockhash is provided; use default nblocks (43800) and include blockhash
            command = self._build_command() + [
                "getchaintxstats",
                str(43800),
                str(blockhash)
            ]
        else:
            # Case: neither nblocks nor blockhash is provided; use no additional arguments
            command = self._build_command() + [
                "getchaintxstats"
            ]

        try:
            # Execute the CLI command using subprocess, capturing stdout and stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout.strip():
                try:
                    # If output is non-empty, attempt to parse it as JSON
                    parsed = json.loads(result.stdout)
                    return parsed
                except json.JSONDecodeError as err:
                    # If parsing fails, return the raw output with an error message
                    return {"error": f"Invalid JSON output: {err}", "raw": result.stdout}
            else:
                # If there is no output from the command, return a message indicating no info
                return {"message": "No available information"}
        except Exception as e:
            # If subprocess execution fails, return the exception as an error message
            return {"error": str(e)}

    def getdifficulty(self):
        """
        Retrieve the current proof-of-work difficulty using the `getdifficulty` RPC command.

        This method queries the Evrmore node to get the current mining difficulty,
        expressed as a multiple of the minimum possible difficulty (i.e., 1.0).

        Returns:
            float or dict:
                - On success: A floating-point number representing the current difficulty.
                - On malformed JSON output: A dictionary with "error" and "raw" keys.
                - On failure: A dictionary with an "error" key containing exception details.

        Evrmore-cli CLI reference:
            getdifficulty

            - Returns the current proof-of-work difficulty.
            - Output: A single numeric value (e.g., 2238590.406819596)

        Example:
            >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> difficulty = rpc.getdifficulty()
        """
        # Build the CLI command to query current difficulty
        command = self._build_command() + [
            "getdifficulty"
        ]

        try:
            # Execute the CLI command using subprocess, capturing stdout and stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout.strip():
                try:
                    # Attempt to parse the numeric output as JSON (float expected)
                    parsed = json.loads(result.stdout)
                    return parsed
                except json.JSONDecodeError as err:
                    # Return raw output if it fails to parse, with error message
                    return {"error": f"Invalid JSON output: {err}", "raw": result.stdout}
            else:
                # Return a message if no output is returned from the command
                return {"message": "No available information"}
        except Exception as e:
            # Catch and return any exception during command execution
            return {"error": str(e)}


    def getmempoolancestors(self, txid, verbose=True):
        """
        Retrieve in-mempool ancestor transactions for a given transaction using the `getmempoolancestors` RPC command.

        This method queries the Evrmore node for all ancestor transactions of a specified transaction ID (`txid`)
        that is currently in the mempool. The output varies depending on the `verbose` flag:

            - If `verbose=True` (default), the result is a dictionary of ancestor transactions with detailed metadata.
            - If `verbose=False`, the result is a list of ancestor transaction IDs only.

        If the specified `txid` is not found in the mempool, an error will be returned.

        Args:
            txid (str): The transaction ID to query. Must be present in the mempool.
            verbose (bool, optional): If True (default), returns structured JSON info.
                If False, returns a list of ancestor transaction IDs.

        Returns:
            dict or list:
                - If verbose=True:
                    Returns a dictionary where each key is an ancestor transaction ID, and each value contains:
                        - "size" (int): Virtual transaction size as defined in BIP 141.
                        - "fee" (float): Transaction fee in EVR.
                        - "modifiedfee" (float): Fee with any mining-priority deltas applied.
                        - "time" (int): UNIX timestamp when the transaction entered the mempool.
                        - "height" (int): Block height at which the transaction entered the mempool.
                        - "descendantcount" (int): Number of in-mempool descendants, including the transaction itself.
                        - "descendantsize" (int): Total virtual size of descendants.
                        - "descendantfees" (float): Combined modified fees of descendants.
                        - "ancestorcount" (int): Number of in-mempool ancestors, including the transaction itself.
                        - "ancestorsize" (int): Total virtual size of ancestors.
                        - "ancestorfees" (float): Combined modified fees of ancestors.
                        - "wtxid" (str): Witness transaction ID.
                        - "depends" (list of str): List of parent transaction IDs used as inputs.
                - If verbose=False:
                    Returns a list of transaction ID strings for all ancestor transactions in the mempool.
                - On malformed JSON output: Returns a dictionary with "error" and "raw" keys.
                - On failure (e.g., txid not in mempool): Returns a dictionary with an "error" key containing exception details.

        Evrmore-cli CLI reference:
            getmempoolancestors "txid" (verbose)

            - "txid":      (string, required) The transaction ID to inspect.
            - verbose:     (boolean, optional, default=false) true for a JSON object, false for an array of txids.

        Example:
            >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> ancestors = rpc.getmempoolancestors("a1b2c3d4...", verbose=False)
        """

        # Build the CLI command with the txid and the verbose flag
        command = self._build_command() + [
            "getmempoolancestors",
            str(txid),
            str(verbose).lower()  # Convert boolean to lowercase string: 'true' or 'false'
        ]

        try:
            # Execute the CLI command using subprocess, capturing stdout and stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout.strip():
                try:
                    # Attempt to parse the output as JSON
                    parsed = json.loads(result.stdout)
                    return parsed
                except json.JSONDecodeError as err:
                    # Return raw output if parsing fails, along with error message
                    return {"error": f"Invalid JSON output: {err}", "raw": result.stdout}
            else:
                # Return a message if the command produced no output
                return {"message": "No available information"}
        except Exception as e:
            # Catch and return any exception (e.g., txid not in mempool, CLI error)
            return {"error": str(e)}



    def getmempooldescendants(self, txid, verbose=True):
        """
        Retrieve in-mempool descendant transactions for a given transaction using the `getmempooldescendants` RPC command.

        This method queries the Evrmore node for all descendant transactions of a specified transaction ID (`txid`)
        that is currently in the mempool. The output varies depending on the `verbose` flag:

            - If `verbose=True` (default), the result is a dictionary of descendant transactions with detailed metadata.
            - If `verbose=False`, the result is a list of descendant transaction IDs only.

        If the specified `txid` is not found in the mempool, an error will be returned.

        Args:
            txid (str): The transaction ID to query. Must be present in the mempool.
            verbose (bool, optional): If True (default), returns structured JSON info.
                If False, returns a list of descendant transaction IDs.

        Returns:
            dict or list:
                - If verbose=True:
                    Returns a dictionary where each key is a descendant transaction ID, and each value contains:
                        - "size" (int): Virtual transaction size as defined in BIP 141.
                        - "fee" (float): Transaction fee in EVR.
                        - "modifiedfee" (float): Fee with any mining-priority deltas applied.
                        - "time" (int): UNIX timestamp when the transaction entered the mempool.
                        - "height" (int): Block height at which the transaction entered the mempool.
                        - "descendantcount" (int): Number of in-mempool descendants, including the transaction itself.
                        - "descendantsize" (int): Total virtual size of descendants.
                        - "descendantfees" (float): Combined modified fees of descendants.
                        - "ancestorcount" (int): Number of in-mempool ancestors, including the transaction itself.
                        - "ancestorsize" (int): Total virtual size of ancestors.
                        - "ancestorfees" (float): Combined modified fees of ancestors.
                        - "wtxid" (str): Witness transaction ID.
                        - "depends" (list of str): List of parent transaction IDs used as inputs.
                - If verbose=False:
                    Returns a list of transaction ID strings for all descendant transactions in the mempool.
                - On malformed JSON output: Returns a dictionary with "error" and "raw" keys.
                - On failure (e.g., txid not in mempool): Returns a dictionary with an "error" key containing exception details.

        Evrmore-cli CLI reference:
            getmempooldescendants "txid" (verbose)

            - "txid":      (string, required) The transaction ID to inspect.
            - verbose:     (boolean, optional, default=false) true for a JSON object, false for an array of txids.

        Example:
            >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> descendants = rpc.getmempooldescendants("a1b2c3d4...", verbose=False)
        """

        # Build the CLI command with the txid and the verbose flag
        command = self._build_command() + [
            "getmempoolancestors",
            str(txid),
            str(verbose).lower()  # Convert boolean to lowercase string: 'true' or 'false'
        ]

        try:
            # Execute the CLI command using subprocess, capturing stdout and stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout.strip():
                try:
                    # Attempt to parse the output as JSON
                    parsed = json.loads(result.stdout)
                    return parsed
                except json.JSONDecodeError as err:
                    # Return raw output if parsing fails, along with error message
                    return {"error": f"Invalid JSON output: {err}", "raw": result.stdout}
            else:
                # Return a message if the command produced no output
                return {"message": "No available information"}
        except Exception as e:
            # Catch and return any exception (e.g., txid not in mempool, CLI error)
            return {"error": str(e)}


    def getmempoolentry(self, txid):
        """
            Retrieve mempool metadata for a specific transaction using the `getmempoolentry` RPC command.

            This method queries the Evrmore node for all mempool-related metadata about a single transaction,
            identified by its transaction ID (`txid`). The transaction must be currently in the mempool.

            Args:
                txid (str): The transaction ID to query. Must be present in the mempool.

            Returns:
                dict:
                    - On success: A dictionary with detailed mempool metadata for the specified transaction, including:
                        - "size" (int): Virtual transaction size (as defined in BIP 141).
                        - "fee" (float): Transaction fee in EVR.
                        - "modifiedfee" (float): Fee after mining-priority deltas.
                        - "time" (int): UNIX timestamp when the transaction entered the mempool.
                        - "height" (int): Block height at which the transaction entered the mempool.
                        - "descendantcount" (int): Number of descendant transactions including this one.
                        - "descendantsize" (int): Total virtual size of descendants.
                        - "descendantfees" (float): Combined modified fees of descendants.
                        - "ancestorcount" (int): Number of ancestor transactions including this one.
                        - "ancestorsize" (int): Total virtual size of ancestors.
                        - "ancestorfees" (float): Combined modified fees of ancestors.
                        - "wtxid" (str): Witness transaction ID.
                        - "depends" (list of str): List of parent transaction IDs this transaction depends on.
                    - On malformed JSON output: Returns a dictionary with "error" and "raw" keys.
                    - On failure (e.g., txid not in mempool): Returns a dictionary with an "error" key containing exception details.

            Evrmore-cli CLI reference:
                getmempoolentry "txid"

                - "txid": (string, required) The transaction ID to inspect. Must be present in the mempool.

            Example:
                >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
                >>> entry = rpc.getmempoolentry("a1b2c3d4...")
            """
        # Build the CLI command to retrieve mempool data for the given transaction ID
        command = self._build_command() + [
            "getmempoolentry",
            str(txid)
        ]

        try:
            # Execute the CLI command using subprocess, capturing stdout and stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout.strip():
                try:
                    # Attempt to parse the output as JSON and return it
                    parsed = json.loads(result.stdout)
                    return parsed
                except json.JSONDecodeError as err:
                    # If JSON parsing fails, return the raw output with an error message
                    return {"error": f"Invalid JSON output: {err}", "raw": result.stdout}
            else:
                # Return a message if the command succeeded but produced no output
                return {"message": "No available information"}
        except Exception as e:
            # Catch and return any exception (e.g., txid not in mempool, CLI error)
            return {"error": str(e)}


    def getmempoolinfo(self):
        """
        Retrieve information about the current state of the mempool using the `getmempoolinfo` RPC command.

        This method queries the Evrmore node for real-time statistics about the transaction memory pool (mempool),
        including the number of transactions, total size, memory usage, and the minimum required fee.

        Args:
            None

        Returns:
            dict:
                - On success: A dictionary with information about the mempool state, including:
                    - "size" (int): The number of transactions currently in the mempool.
                    - "bytes" (int): The total virtual size (vsize) of all transactions in the mempool.
                    - "usage" (int): The total memory usage of the mempool in bytes.
                    - "maxmempool" (int): The maximum memory usage allowed for the mempool in bytes.
                    - "mempoolminfee" (float): The minimum fee rate in EVR/kB required for a transaction to be accepted.
                - On malformed JSON output: Returns a dictionary with "error" and "raw" keys.
                - On failure: Returns a dictionary with an "error" key containing exception details.

        Evrmore-cli CLI reference:
            getmempoolinfo

            - Returns real-time metadata on the memory pool used to hold unconfirmed transactions.

        Example:
            >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> mempool = rpc.getmempoolinfo()
        """
        # Build the CLI command to retrieve mempool information
        command = self._build_command() + [
            "getmempoolinfo"
        ]

        try:
            # Execute the CLI command using subprocess, capturing stdout and stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout.strip():
                try:
                    # Attempt to parse the output as JSON and return it
                    parsed = json.loads(result.stdout)
                    return parsed
                except json.JSONDecodeError as err:
                    # If JSON parsing fails, return the raw output with an error message
                    return {"error": f"Invalid JSON output: {err}", "raw": result.stdout}
            else:
                # Return a message if the command succeeded but produced no output
                return {"message": "No available information"}
        except Exception as e:
            # Catch and return any exception (e.g., txid not in mempool, CLI error)
            return {"error": str(e)}

    def getrawmempool(self, verbose=True
                      ):
        """
        Retrieve raw mempool contents using the `getrawmempool` RPC command.

        This method queries the Evrmore node for all transactions currently in the memory pool.
        The output format depends on the `verbose` flag:

            - If `verbose=True`, returns a dictionary where each key is a transaction ID and each value
              contains detailed metadata for that transaction.
            - If `verbose=False`, returns a list of transaction IDs only.

        Args:
            verbose (bool): If True, returns structured JSON info.
                            If False, returns only a list of txids.

        Returns:
            dict or list:
                - If verbose=True:
                    Returns a dictionary where each key is a transaction ID and each value includes:
                        - "size" (int): Virtual transaction size (BIP 141).
                        - "fee" (float): Transaction fee in EVR.
                        - "modifiedfee" (float): Fee after mining-priority deltas.
                        - "time" (int): UNIX timestamp when the transaction entered the mempool.
                        - "height" (int): Block height when the transaction entered the mempool.
                        - "descendantcount" (int): Count of in-mempool descendants (including itself).
                        - "descendantsize" (int): Total virtual size of all descendants.
                        - "descendantfees" (float): Total modified fees of descendants.
                        - "ancestorcount" (int): Count of in-mempool ancestors (including itself).
                        - "ancestorsize" (int): Total virtual size of all ancestors.
                        - "ancestorfees" (float): Total modified fees of ancestors.
                        - "wtxid" (str): Witness transaction ID.
                        - "depends" (list of str): List of parent transaction IDs used as inputs.
                - If verbose=False:
                    Returns a list of transaction ID strings currently in the mempool.
                - On malformed JSON output: Returns a dictionary with "error" and "raw" keys.
                - On failure: Returns a dictionary with an "error" key containing exception details.

        Evrmore-cli CLI reference:
            getrawmempool (verbose)

            - verbose (optional, default=false): true for detailed JSON, false for array of txids

        Example:
            >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> rpc.getrawmempool(verbose=False)
        """

        # Build the CLI command to retrieve raw mempool data, with optional verbosity
        command = self._build_command() + [
            "getrawmempool",
            str(verbose).lower()
        ]

        try:
            # Execute the CLI command using subprocess, capturing stdout and stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout.strip():
                try:
                    # Attempt to parse the output as JSON and return it
                    parsed = json.loads(result.stdout)
                    return parsed
                except json.JSONDecodeError as err:
                    # If JSON parsing fails, return the raw output with an error message
                    return {"error": f"Invalid JSON output: {err}", "raw": result.stdout}
            else:
                # Return a message if the command succeeded but produced no output
                return {"message": "No available information"}
        except Exception as e:
            # Catch and return any exception (e.g., CLI failure, subprocess error)
            return {"error": str(e)}


    def getspentinfo(self, txid, index):
        """
        Retrieve information about where a specific transaction output was spent using the `getspentinfo` RPC command.

        This method queries the Evrmore node to determine the spending transaction and input index
        for a specific output of a given transaction.

        Args:
            txid (str): The hex string of the transaction ID.
            index (int): The output index of the transaction to check.

        Returns:
            dict:
                - On success: A dictionary containing information about the spending input, including:
                    - "txid" (str): The transaction ID of the transaction that spent the output.
                    - "index" (int): The index of the input that spent the output.
                    - Additional implementation-defined fields may be present.
                - On malformed JSON output: Returns a dictionary with "error" and "raw" keys.
                - On failure (e.g., output not spent or input invalid): Returns a dictionary with an "error" key containing exception details.

        Evrmore-cli CLI reference:
            getspentinfo

            Input:
                {
                    "txid": (string) The hex string of the txid,
                    "index": (number) The output index
                }

            Output:
                {
                    "txid": (string) The transaction ID that spent the output,
                    "index": (number) The index of the input in the spending transaction
                }

        Example:
            >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> rpc.getspentinfo("0437cd7f8525ceed2324359c2d0ba26006d92d856a9c20fa0241106ee5a597c9", 0)
        """

        query = json.dumps({
            "txid": txid,
            "index": index
        })

        command = self._build_command() + [
            "getspentinfo",
            query
        ]

        try:
            # Execute the CLI command using subprocess, capturing stdout and stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout.strip():
                try:
                    # Attempt to parse the output as JSON and return it
                    parsed = json.loads(result.stdout)
                    return parsed
                except json.JSONDecodeError as err:
                    # If JSON parsing fails, return the raw output with an error message
                    return {"error": f"Invalid JSON output: {err}", "raw": result.stdout}
            else:
                # Return a message if the command succeeded but produced no output
                return {"message": "No available information"}
        except Exception as e:
            # Catch and return any exception (e.g., CLI failure, subprocess error)
            return {"error": str(e)}


    def gettxout(self, txid, n, include_mempool=True):
        """
        Retrieve details about an unspent transaction output (UTXO) using the `gettxout` RPC command.

        This method queries the Evrmore node to determine the current state and metadata of a specific
        transaction output. If the output is unspent and not spent in the mempool (if `include_mempool=True`),
        it returns detailed information. If the output is already spent, it returns None.

        Args:
            txid (str): The transaction ID to inspect.
            n (int): The output index (vout number) of the transaction.
            include_mempool (bool, optional): Whether to include mempool transactions when determining if the output is unspent.
                                              Defaults to True.

        Returns:
            dict:
                - On success (unspent output): A dictionary with UTXO details including:
                    - "bestblock" (str): The block hash that includes the transaction.
                    - "confirmations" (int): Number of confirmations.
                    - "value" (float): Amount in EVR for this output.
                    - "scriptPubKey" (dict): Details of the output script, including:
                        - "asm" (str): Script in assembly form.
                        - "hex" (str): Script in hex encoding.
                        - "reqSigs" (int): Required number of signatures.
                        - "type" (str): Script type (e.g., "pubkeyhash").
                        - "addresses" (list of str): List of associated Evrmore addresses.
                    - "coinbase" (bool): True if the transaction is a coinbase transaction.
                - If spent or not found: Returns None or {"message": "No available information"}
                - On malformed JSON output: Returns a dictionary with "error" and "raw" keys.
                - On failure: Returns a dictionary with an "error" key containing exception details.

        Evrmore-cli CLI reference:
            gettxout "txid" n ( include_mempool )

            - "txid":             (string, required) The transaction ID.
            - n:                  (numeric, required) The vout number (output index).
            - include_mempool:   (boolean, optional) Whether to include mempool when checking for spent status. Default is true.

        Example:
            >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> utxo = rpc.gettxout("0437cd7f8525ceed2324359c2d0ba26006d92d856a9c20fa0241106ee5a597c9", 0)
        """

        # Build the CLI command with txid, output index, and optional mempool flag
        command = self._build_command() + [
            "gettxout",
            str(txid),
            str(n),
            str(include_mempool).lower()
        ]

        try:
            # Execute the CLI command using subprocess, capturing stdout and stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout.strip():
                try:
                    # Attempt to parse the output as JSON and return it
                    parsed = json.loads(result.stdout)
                    return parsed
                except json.JSONDecodeError as err:
                    # If JSON parsing fails, return the raw output with an error message
                    return {"error": f"Invalid JSON output: {err}", "raw": result.stdout}
            else:
                # Return a message if the command succeeded but produced no output
                return {"message": "No available information"}
        except Exception as e:
            # Catch and return any exception (e.g., CLI failure, subprocess error)
            return {"error": str(e)}


    def gettxoutproof(self, txids, blockhash):
        """
        Retrieve a hex-encoded Merkle proof that one or more transactions were included in a block
        using the `gettxoutproof` RPC command.

        This method queries the Evrmore node for a Merkle proof that the given transaction(s) were included
        in a specific block. If `-txindex` is not enabled, the `blockhash` argument is required.

        Args:
            txids (list of str): A list of transaction IDs to prove inclusion for.
            blockhash (str): The hash of the block that includes the transaction(s).

        Returns:
            str or dict:
                - On success: A hex-encoded Merkle proof string.
                - On malformed output: A dictionary with "error" and "raw" keys.
                - On failure: A dictionary with an "error" key containing exception details.

        Evrmore-cli CLI reference:
            gettxoutproof ["txid",...] ( blockhash )

        Example:
            >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> proof = rpc.gettxoutproof(["txid1"], "blockhash")
        """

        # Prepare CLI parameters: txid array as JSON string, blockhash as string
        query = json.dumps(
            txids
        )
        # Build the CLI command RPC call, json formatted list, and blockhash string
        command = self._build_command() + [
            "gettxoutproof",
            query,
            str(blockhash)
        ]

        try:
            # Execute the CLI command using subprocess, capturing stdout and stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout.strip():
                try:
                    # This RPC returns a hex string, not JSON — return it directly
                    return result.stdout.strip()
                except json.JSONDecodeError as err:
                    # This block is unlikely to be triggered, but kept for consistency
                    return {"error": f"Invalid JSON output: {err}", "raw": result.stdout}
            else:
                # Handle empty response
                return {"message": "No available information"}
        except Exception as e:
            # Catch and return any exception (e.g., CLI failure)
            return {"error": str(e)}


    def gettxoutsetinfo(self):
        """
        Retrieve statistics about the current UTXO (unspent transaction output) set using the `gettxoutsetinfo` RPC command.

        This method queries the Evrmore node for detailed statistics about the current state of the UTXO set.
        The information includes block height, total number of outputs, total amount, serialized hash, and estimated disk usage.

        Note:
            This call may take some time to complete depending on node state and disk performance.

        Args:
            None

        Returns:
            dict:
                - On success: A dictionary containing UTXO set statistics, including:
                    - "height" (int): The current block height.
                    - "bestblock" (str): The block hash of the best block.
                    - "transactions" (int): Total number of transactions in the chain.
                    - "txouts" (int): Total number of UTXO entries.
                    - "bogosize" (int): A meaningless metric provided for internal size approximation.
                    - "hash_serialized_2" (str): A serialized hash of the UTXO set.
                    - "disk_size" (int): Estimated disk size of the chainstate in bytes.
                    - "total_amount" (float): Total amount of EVR in the UTXO set.
                - On malformed JSON output: A dictionary with "error" and "raw" keys.
                - On failure: A dictionary with an "error" key containing exception details.

        Evrmore-cli CLI reference:
            gettxoutsetinfo

            - Returns metadata about the unspent transaction output (UTXO) set.

        Example:
            >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> stats = rpc.gettxoutsetinfo()
        """

        command = self._build_command() + [
            "gettxoutsetinfo"
        ]

        try:
            # Execute the CLI command using subprocess, capturing stdout and stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout.strip():
                try:
                    # Attempt to parse the output as JSON and return it
                    parsed = json.loads(result.stdout)
                    return parsed
                except json.JSONDecodeError as err:
                    # If JSON parsing fails, return the raw output with an error message
                    return {"error": f"Invalid JSON output: {err}", "raw": result.stdout}
            else:
                # Return a message if the command succeeded but produced no output
                return {"message": "No available information"}
        except Exception as e:
            # Catch and return any exception (e.g., CLI failure, subprocess error)
            return {"error": str(e)}


    def preciousblock(self, blockhash):
        """
        Mark a block as 'precious' using the `preciousblock` RPC command.

        This method tells the Evrmore node to treat the specified block as if it were received
        before others with the same amount of proof-of-work. This can influence chain selection
        by prioritizing the given block in a competing fork scenario.

        Note:
            - The effect is **not persisted** across node restarts.
            - Multiple calls to `preciousblock` can override each other.
            - This does not re-download or reconsider blocks, it only affects tie-breaking.

        Args:
            blockhash (str): The hash of the block to prioritize as precious.

        Returns:
            str or dict:
                - On success: An empty string (standard CLI behavior).
                - On failure: A dictionary with an "error" key containing exception details.
                - On malformed output: A dictionary with "error" and "raw" keys.

        Evrmore-cli CLI reference:
            preciousblock "blockhash"

            - "blockhash": (string, required) The hash of the block to treat as precious.

        Example:
            >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> rpc.preciousblock("0000000000000abc1234...")
        """

        command = self._build_command() + [
            "preciousblock",
            str(blockhash)
        ]

        try:
            # Execute the CLI command using subprocess, capturing stdout and stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout.strip():
                try:
                    # This RPC returns a string (usually empty) — return it directly
                    return result.stdout.strip()
                except json.JSONDecodeError as err:
                    # This block is unlikely to be triggered, but kept for consistency
                    return {"error": f"Invalid JSON output: {err}", "raw": result.stdout}
            else:
                # Handle empty response
                return {"message": "No available information"}
        except Exception as e:
            # Catch and return any exception (e.g., CLI failure)
            return {"error": str(e)}


    def pruneblockchain(self, n):

        command = self._build_command() + [
            "pruneblockchain",
            str(n)
        ]

        try:
            # Execute the CLI command using subprocess, capturing stdout and stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout.strip():
                try:
                    # This RPC returns a string (usually empty) — return it directly
                    return result.stdout.strip()
                except json.JSONDecodeError as err:
                    # This block is unlikely to be triggered, but kept for consistency
                    return {"error": f"Invalid JSON output: {err}", "raw": result.stdout}
            else:
                # Handle empty response
                return {"message": "No available information"}
        except Exception as e:
            # Catch and return any exception (e.g., CLI failure)
            return {"error": str(e)}, print('\nThis likely occurred because node is not in prune mode')


    def savemempool(self):
        """
        Persist the current in-memory mempool to disk using the `savemempool` RPC command.

        This method instructs the Evrmore node to dump the current contents of the mempool
        to the `mempool.dat` file on disk. This allows the mempool to be restored after node restarts.

        Note:
            - This RPC call will **fail** if the node is running in **pruned mode**, as mempool persistence
              is not supported in that configuration.

        Args:
            None

        Returns:
            str or dict:
                - On success: An empty string (standard behavior).
                - On failure (e.g., node is pruned): A dictionary with an "error" key containing exception details.
                - On malformed output: A dictionary with "error" and "raw" keys.

        Evrmore-cli CLI reference:
            savemempool

            - Dumps the mempool to disk.

        Example:
            >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> rpc.savemempool()
        """

        command = self._build_command() + [
            "savemempool"
        ]

        try:
            # Execute the CLI command using subprocess, capturing stdout and stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout.strip():
                try:
                    # This RPC returns a string (usually empty) — return it directly
                    return result.stdout.strip()
                except json.JSONDecodeError as err:
                    # Unlikely for this RPC, but handled for consistency
                    return {"error": f"Invalid JSON output: {err}", "raw": result.stdout}
            else:
                # Command succeeded but returned no output (normal behavior)
                return "No RPC return information.  The mempool dump should be located in your data directory as 'mempool.dat'"
        except Exception as e:
            # Catch and return any exception (e.g., if node is in prune mode)
            return {"error": str(e)}


    def verifychain(self, checklevel=4, nblocks=6):
        """
        Verifies the blockchain database for consistency and correctness.

        Parameters:
            checklevel (int, optional): Specifies the thoroughness of the verification.
                                        Ranges from 0 (lowest) to 4 (highest). Default is 4.
            nblocks (int, optional): Number of blocks to check. 0 means check the entire chain. Default is 6.

        Returns:
            str: "true" or "false" as a string depending on whether the chain verified successfully.
                 If the command produces no output, returns a note about the lack of RPC output.
                 If an error occurs during execution, returns a dictionary with an "error" message.

        RPC Reference:
            verifychain ( checklevel nblocks )

            Verifies blockchain database.

            Arguments:
            1. checklevel   (numeric, optional, 0-4, default=3) How thorough the block verification is.
            2. nblocks      (numeric, optional, default=6, 0=all) The number of blocks to check.

            Result:
            true|false       (boolean) Verified or not

            Examples:
            > evrmore-cli verifychain
            > curl --user myusername --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "verifychain", "params": [] }' -H 'content-type: text/plain;' http://127.0.0.1:8819/
        """
        command = self._build_command() + [
            "verifychain",
            str(checklevel),
            str(nblocks)
        ]

        try:
            # Execute the CLI command using subprocess, capturing stdout and stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout.strip():
                try:
                    # This RPC returns a string (usually empty) — return it directly
                    return result.stdout.strip()
                except json.JSONDecodeError as err:
                    # Unlikely for this RPC, but handled for consistency
                    return {"error": f"Invalid JSON output: {err}", "raw": result.stdout}
            else:
                # Command succeeded but returned no output (normal behavior)
                return "No RPC return information.  The mempool dump should be located in your data directory as 'mempool.dat'"
        except Exception as e:
            # Catch and return any exception (e.g., if node is in prune mode)
            return {"error": str(e)}


    def verifytxoutproof(self, proof):
        """
        Verify that a Merkle proof commits to one or more transactions in a known block using the `verifytxoutproof` RPC command.

        This method checks that a hex-encoded proof (typically generated by `gettxoutproof`) correctly commits to a transaction
        included in a block that is part of the current best chain. If the block is unknown or invalid, the call will fail.

        Args:
            proof (str): A hex-encoded Merkle proof string that commits to one or more transactions in a block.

        Returns:
            list | dict:
                - On success: A list of transaction IDs (txids) that the proof commits to.
                - If the proof is invalid: An empty list.
                - On malformed JSON output: A dictionary with "error" and "raw" keys.
                - On failure: A dictionary with an "error" key containing exception details.

        Evrmore-cli CLI reference:
            verifytxoutproof "proof"

            - proof (string, required): The Merkle proof as a hex-encoded string.

        Example:
            >>> rpc = BlockchainRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> proof = rpc.gettxoutproof(["<txid>"], "<blockhash>")
            >>> verified_txids = rpc.verifytxoutproof(proof)
        """
        command = self._build_command() + [
            "verifytxoutproof",
            str(proof)
        ]

        try:
            # Execute the CLI command using subprocess, capturing stdout and stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout.strip():
                try:
                    # Attempt to parse the output as JSON and return it
                    parsed = json.loads(result.stdout)
                    return parsed
                except json.JSONDecodeError as err:
                    # If JSON parsing fails, return the raw output with an error message
                    return {"error": f"Invalid JSON output: {err}", "raw": result.stdout}
            else:
                # Return a message if the command succeeded but produced no output
                return {"message": "No available information"}
        except Exception as e:
            # Catch and return any exception (e.g., CLI failure, subprocess error)
            return {"error": str(e)}