from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json


class MiningRPC:

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

    def getblocktemplate(self):
        """
        Retrieve data required to construct a new block.

        This RPC call returns a block template per BIPs 22, 23, 9, and 145.
        The result includes information such as version, rules, block height, list of transactions,
        and constraints such as block size, weight, and sigops limits. This is essential for miners
        who want to construct a valid candidate block to be mined and submitted to the network.

        Returns:
            dict: A dictionary containing the block template data required to build a new block.

            On failure, returns:
                - {"error": "Received non-JSON output", "raw": <raw_output>}
                - {"error": "No info available.  Check your wallet/node is running."}
                - {"error": <exception message>} if subprocess call fails

        Example:
            >>> rpc = MiningRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> template = rpc.getblocktemplate()
        """
        # Construct the CLI command for retrieving the block template
        command = self._build_command() + [
            "getblocktemplate"
        ]

        try:
            # Execute the command and capture the standard output and error
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Parse the result as JSON; expected to be a complex dictionary of block data
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    # If the output isn't valid JSON, return an error with the raw result
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # If the command ran but returned nothing, notify that no data was available
                return {"error": "No info available.  Check your wallet/node is running."}
        except Exception as e:
            # If subprocess execution fails (e.g., command doesn't exist), return error message
            return {"error": str(e)}

    def getevrprogpowhash(self, header_hash, mix_hash, nonce, height, target):
        """
        Calls the `getevrprogpowhash` RPC command to compute the EvrProgPoW digest for a block.

        This RPC is typically used to verify or test mining results by recomputing the EvrProgPoW
        digest from known block parameters. It returns a dictionary that includes whether the digest
        meets the difficulty target, the final digest, and additional metadata.

        Parameters:
            header_hash (str): The header hash from the block template (provided to miners).
            mix_hash (str): The mix hash computed by the GPU miner.
            nonce (str): The nonce used for hashing, provided as a hexadecimal string (e.g., '0x1a2b3c').
            height (int): The block height associated with the block being hashed.
            target (str): Optional target threshold (usually the `bits` field from a block header).

        Returns:
            dict: A dictionary containing:
                  - 'digest': The computed EvrProgPoW digest.
                  - 'mix_hash': Echo of the input mix_hash.
                  - 'meets_target': Whether the hash meets the difficulty target ('true' or 'false').
                  - 'info': Additional information (may be empty).
                  - 'result': General result field (typically 'false' unless extended behavior is added).

                  If an error occurs or invalid JSON is returned, an error dictionary is returned instead.

        Example:
            >>> rpc = MiningRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> template = rpc.getevrprogpowhash()
        """

        # Build the CLI command with all required arguments
        command = self._build_command() + [
            "getevrprogpowhash",
            str(header_hash),
            str(mix_hash),
            str(nonce),
            str(height),
            str(target)
        ]

        try:
            # Execute the command and capture the standard output and error
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Attempt to parse the output as JSON (expected dictionary with hash results)
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    # Return raw output if it's not valid JSON
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # Handle the case where the command succeeds but returns no output
                return {"error": "No info available.  Check your wallet/node is running."}
        except Exception as e:
            # Handle any exception raised during subprocess execution
            return {"error": str(e)}

    def getmininginfo(self):
        """
        Calls the `getmininginfo` RPC command to retrieve mining-related statistics and status.

        This includes details such as current block height, difficulty, mempool size, network hashrate,
        and the current chain being used (main, testnet, etc.). It's useful for monitoring node status
        and mining conditions.

        Returns:
            dict: A dictionary containing:
                - "blocks": Current block height (int)
                - "currentblockweight": Weight of the most recent block (int)
                - "currentblocktx": Number of transactions in the most recent block (int)
                - "difficulty": Current mining difficulty (float)
                - "networkhashps": Network hash rate in hashes per second (int)
                - "hashespersec": Hash rate of built-in miner (int, usually 0 unless local mining)
                - "pooledtx": Number of transactions in the mempool (int)
                - "chain": Name of the active chain (e.g., "main", "test")
                - "warnings": Network or blockchain warnings (str)
                - "errors": Deprecated, present only with `-deprecatedrpc=getmininginfo` (str, optional)

            If any error occurs or output is invalid, returns a dictionary with an 'error' key.

        Example:
            >>> rpc = MiningRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> template = rpc.getmininginfo()
        """

        # Construct the CLI command for getmininginfo
        command = self._build_command() + [
            "getmininginfo"
        ]

        try:
            # Run the command using subprocess and capture output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Parse the output as JSON
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    # Handle the case where output is not valid JSON
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # Handle the case where no output is returned
                return {"error": "No info available.  Check your wallet/node is running."}
        except Exception as e:
            # Handle exceptions during subprocess execution
            return {"error": str(e)}

    def getnetworkhashps(self, nblocks=120, height=-1):
        """
        Calls the `getnetworkhashps` RPC method to estimate the current network hashrate.

        This value is based on how many hashes are estimated to be performed across the entire
        network per second, over the last `nblocks` blocks. You can also request an estimate
        as of a specific historical block height.

        Args:
            nblocks (int, optional): The number of blocks to use for the estimate. Default is 120.
                                    Use -1 to estimate since the last difficulty adjustment.
            height (int, optional): The block height to estimate the network hash rate at.
                                    Default is -1 (most recent block).

        Returns:
            float | dict: The estimated hashes per second as a float if successful.
                          Returns a dictionary with an 'error' key if an error occurs or
                          if the output is not valid JSON.

        Example:
            >>> rpc = MiningRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> template = rpc.getnetworkhashps()
        """

        # Construct the CLI command with given arguments
        command = self._build_command() + [
            "getnetworkhashps",
            str(nblocks),
            str(height)
        ]

        try:
            # Run the command and capture the output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Parse the output; expected to be a single numeric value (hashes per second)
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    # Return raw string if output isn't valid JSON
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # Handle empty output from the CLI
                return {"error": "No info available.  Check your wallet/node is running."}
        except Exception as e:
            # Handle subprocess execution errors
            return {"error": str(e)}

    def pprpcsb(self, header_hash, mix_hash, nonce):
        """
        Submit a mined EvrprogPoW block to the network.

        This RPC method is designed for use with GPU miners who mined a block using
        the EvrprogPoW algorithm. It submits the relevant block components—header hash,
        mix hash, and nonce—back to the node for validation and inclusion into the blockchain.

        Args:
            header_hash (str): The header hash used for mining (from getblocktemplate).
            mix_hash (str): The mix hash returned by the miner during the PoW computation.
            nonce (str): The hex string nonce used to mine the block.

        Returns:
            dict | str: Parsed JSON response if the submission was processed,
                        or an error dictionary if something goes wrong or if the response
                        isn't valid JSON.

        Example:
            >>> rpc = MiningRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> template = rpc.pprpcsb()
        """

        # Build the CLI command with the required EvrprogPoW mining arguments
        command = self._build_command() + [
            "pprpcsb",
            str(header_hash),
            str(mix_hash),
            str(nonce)
        ]

        try:
            # Run the command and capture the output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Parse the output; expected to be a valid JSON response
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    # Return raw output if not valid JSON
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # If the command returned no output, notify the user
                return {"error": "No info available. Check your wallet/node is running."}
        except Exception as e:
            # Return any error encountered during subprocess execution
            return {"error": str(e)}

    def prioritisetransaction(self, txid, fee_delta, dummy=0.0):
        """
        Adjust the mining priority of a transaction by modifying its effective fee.

        This RPC method allows you to manually influence the mining algorithm’s decision to include
        a specific transaction in a block by simulating a fee adjustment. The actual transaction
        fee remains unchanged on-chain; this only affects local block template selection.

        Args:
            txid (str): The transaction ID (txid) of the transaction to prioritize.
            fee_delta (int | float): The value in satoshis to simulate adding (positive) or subtracting (negative)
                                     from the transaction fee. A higher value increases the likelihood
                                     of inclusion in mined blocks.
            dummy (float, optional): A legacy argument retained for compatibility with older APIs.
                                     Defaults to 0.0 and is ignored internally.

        Returns:
            dict | str: A parsed JSON response indicating success (typically `true`),
                        or an error dictionary if something goes wrong.

        Example:
            >>> rpc = MiningRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> template = rpc.prioritisetransaction()
        """

        # Build the CLI command with txid, dummy (deprecated), and fee_delta
        command = self._build_command() + [
            "prioritisetransaction",
            str(txid),
            str(dummy),
            str(fee_delta)
        ]

        try:
            # Run the command using subprocess and capture output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Attempt to parse JSON response (expected: true on success)
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    # Return raw output if not valid JSON
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # Handle the case where the command executed but returned nothing
                return {"error": "No info available. Check your wallet/node is running."}
        except Exception as e:
            # Catch and return any subprocess execution error
            return {"error": str(e)}

    def submitblock(self, hexdata):
        """
        Submit a newly mined block to the network.

        This method is used to relay a fully constructed and valid block (in hex format)
        to the Evrmore network. It's typically used by mining software once a valid solution
        is found. The block must be properly formatted and serialized per consensus rules.

        Args:
            hexdata (str): The hex-encoded string representing the full block to submit.

        Returns:
            dict | str: A parsed JSON result (which may be empty or indicate errors),
                        or a dictionary with an error message if the submission fails.
                        According to BIP22, a return of `null` or an empty string indicates success.

        Example:
            >>> rpc = MiningRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> template = rpc.submitblock()
        """

        # Build the CLI command for submitting the block
        command = self._build_command() + [
            "submitblock",
            str(hexdata)
        ]

        try:
            # Execute the command and capture the result
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Try parsing the result as JSON
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    # If it's not valid JSON, return the raw output for inspection
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # If there’s no output, the submission may have succeeded silently
                return {"message": "Block submitted successfully (no response from node)."}
        except Exception as e:
            # Return any exception encountered during execution
            return {"error": str(e)}
