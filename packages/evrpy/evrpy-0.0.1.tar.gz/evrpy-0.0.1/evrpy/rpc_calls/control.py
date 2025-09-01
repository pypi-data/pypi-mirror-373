from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json



class ControlRPC:

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


    def getinfo(self):
        """
        Retrieve general information about the Evrmore node and wallet.

        Executes the `getinfo` command via the Evrmore CLI, which returns a variety
        of runtime and blockchain-related metadata. This includes wallet balance, block height,
        difficulty, versioning, connection status, and other system-level data.

        Note:
            This RPC method is deprecated and may be removed in future versions. It is recommended
            to use more specific RPC methods (like `getblockchaininfo`, `getnetworkinfo`, `getwalletinfo`) instead.

        Returns:
            dict: A dictionary containing:
                - "version" (int): Evrmore server version
                - "protocolversion" (int): Network protocol version
                - "walletversion" (int): Wallet version
                - "balance" (float): Wallet balance in EVR
                - "blocks" (int): Current block height
                - "timeoffset" (int): Time offset in seconds
                - "connections" (int): Number of active peer connections
                - "proxy" (str, optional): Proxy setting if any
                - "difficulty" (float): Current PoW difficulty
                - "testnet" (bool): True if running on testnet
                - "keypoololdest" (int): Timestamp of oldest pre-generated key
                - "keypoolsize" (int): Number of keys in the keypool
                - "unlocked_until" (int): Wallet unlock expiration (epoch), or 0 if locked
                - "paytxfee" (float): Fee per KB set by user
                - "relayfee" (float): Minimum fee required to relay transactions
                - "errors" (str): Any network or wallet-related warnings

            On failure, returns:
                - {"error": "Received non-JSON output", "raw": <raw output>}
                - {"error": "No info available.  Check your wallet/node is running."}
                - {"error": <exception message>} if the subprocess fails

        Example:
            >>> rpc = EvrmoreRPC(cli_path="evrmore-cli", datadir="/home/aethyn/.evrmore-test/testnet1", rpc_user="neubtrino_testnet", rpc_pass="pass_testnet", testnet=True)
            >>> info = rpc.getinfo()
        """
        command = self._build_command() + [
            "getinfo"
        ]

        try:
            # Execute the command as a subprocess, capturing standard output and error
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Attempt to parse the output as JSON (should be a decoded block dictionary)
                    parsed = json.loads(result.stdout.strip())
                    return parsed  # Return the info data as a Python dictionary
                except json.JSONDecodeError:
                    # Output was not valid JSON, so return an error dictionary with the raw output
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # No data was returned
                return {"error": f"No info available.  Check your wallet/node is running."}
        except Exception as e:
            # Catch and return any exception that occurs during the subprocess execution as an error dictionary
            return {"error": str(e)}

    def getmemoryinfo(self, mode="stats"):
        """
        Retrieve memory usage information from the Evrmore node.

        This method executes the `getmemoryinfo` RPC command via the CLI. It provides either high-level
        memory usage stats or a low-level heap state (in XML format), depending on the selected mode.

        Parameters:
            mode (str, optional): The mode of memory info to return. Must be one of:
                - "stats": General statistics about memory usage (default)
                - "mallocinfo": Low-level heap state as an XML string (glibc 2.10+ required)

        Returns:
            dict or str:
                - If mode is "stats", returns a dictionary with the following structure:
                    {
                      "locked": {
                        "used": int,
                        "free": int,
                        "total": int,
                        "locked": int,
                        "chunks_used": int,
                        "chunks_free": int
                      }
                    }
                - If mode is "mallocinfo", returns a string containing XML output from malloc.

            On failure, returns:
                - {"error": "Received non-JSON output", "raw": <raw output>}
                - {"error": "No info available.  Check your wallet/node is running."}
                - {"error": <exception message>} if the subprocess fails

        Example:
            >>> rpc = EvrmoreRPC(cli_path="evrmore-cli", datadir="/home/aethyn/.evrmore-test/testnet1", rpc_user="neubtrino_testnet", rpc_pass="pass_testnet", testnet=True)
            >>> meminfo = rpc.getmemoryinfo()
        """
        # Build the full CLI command with the chosen mode
        command = self._build_command() + [
            "getmemoryinfo",
            str(mode)
        ]

        try:
            # Execute the command as a subprocess, capturing standard output and error
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # If output is JSON (expected for "stats" mode), parse and return it
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    # If output is not JSON (e.g., "mallocinfo" returns XML), return raw output
                    return result.stdout.strip()
            else:
                # No output received from the command
                return {"error": "No info available.  Check your wallet/node is running."}
        except Exception as e:
            # Catch any subprocess or execution errors
            return {"error": str(e)}

    def getrpcinfo(self):
        """
        Retrieve information about the RPC server and currently active commands.

        Executes the `getrpcinfo` RPC command via the Evrmore CLI. This returns details about the
        RPC subsystem, including a list of currently executing RPC commands and their durations.

        Returns:
            dict: A dictionary containing:
                - "active_commands" (list of dict): Each dictionary includes:
                    - "method" (str): The name of the currently running RPC method
                    - "duration" (int): Time in microseconds the command has been running

            On failure, returns:
                - {"error": "Received non-JSON output", "raw": <raw output>}
                - {"error": "No info available.  Check your wallet/node is running."}
                - {"error": <exception message>} if the subprocess fails

        Example:
            >>> rpc = EvrmoreRPC(cli_path="evrmore-cli", datadir="/home/aethyn/.evrmore-test/testnet1", rpc_user="neubtrino_testnet", rpc_pass="pass_testnet", testnet=True)
            >>> rpcinfo = rpc.getrpcinfo()
        """
        # Build the CLI command to call the 'getrpcinfo' RPC method
        command = self._build_command() + [
            "getrpcinfo"
        ]

        try:
            # Execute the command and capture standard output and error
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Parse and return JSON output (expected format)
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    # Return raw output if not valid JSON (should not happen for getrpcinfo)
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # Handle the case of empty output
                return {"error": "No info available.  Check your wallet/node is running."}
        except Exception as e:
            # Return any exception encountered during subprocess execution
            return {"error": str(e)}

    def help(self, rpccall=None):
        """
        Display help information for all RPC commands or a specific command.

        This method executes the `help` RPC command via the Evrmore CLI. If a specific RPC command
        is provided, the method returns usage information for that command. Otherwise, it returns
        the full categorized list of available commands.

        Parameters:
            rpccall (str, optional): The name of an RPC method to get help for. If None, prints help for all.

        Returns:
            str: A plain text help message with command usage details.

            On failure, returns:
                - {"error": "No help available.  Check your wallet/node is running."}
                - {"error": <exception message>} if the subprocess fails

        Example:
            >>> rpc = EvrmoreRPC(cli_path="evrmore-cli", datadir="/home/aethyn/.evrmore-test/testnet1", rpc_user="neubtrino_testnet", rpc_pass="pass_testnet", testnet=True)
            >>> helptext = rpc.help()
        """
        # Construct the CLI command, adding the optional specific RPC call if provided
        if rpccall is not None:
            command = self._build_command() + ["help", str(rpccall)]
        else:
            command = self._build_command() + ["help"]

        try:
            # Execute the CLI help command
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                return result.stdout.strip()  # Always plain text, so return directly
            else:
                return {"error": "No help available.  Check your wallet/node is running."}
        except Exception as e:
            return {"error": str(e)}



    def stop(self):
        """
        Gracefully shut down the Evrmore node.

        Executes the `stop` RPC command via the CLI, which causes the Evrmore daemon
        to shut down cleanly. This command will terminate the process, so it should
        only be called when you are ready to shut down the node.

        Returns:
            str: A plain text message confirming that shutdown was initiated.
                  Typically returns "Evrmore server stopping".

            On failure, returns:
                - {"error": "No shutdown confirmation received."}
                - {"error": <exception message>} if the subprocess fails

        Example:
            >>> rpc = EvrmoreRPC(cli_path="evrmore-cli", datadir="/home/aethyn/.evrmore-test/testnet1", rpc_user="neubtrino_testnet", rpc_pass="pass_testnet", testnet=True)
            >>> result = rpc.stop()
        """
        # Build the CLI command to stop the node
        command = self._build_command() + ["stop"]

        try:
            # Execute the command and capture output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                return result.stdout.strip()  # Return the raw confirmation string
            else:
                return {"error": "No shutdown confirmation received."}
        except Exception as e:
            return {"error": str(e)}

    def uptime(self):
        """
        Return the total uptime of the Evrmore server in dd:hh:mm:ss format.

        Executes the `uptime` RPC command via the Evrmore CLI. The command returns the number
        of seconds the Evrmore node has been running. This function converts that into a
        human-readable `dd:hh:mm:ss` string.

        Returns:
            str: Uptime formatted as "dd:hh:mm:ss".

            On failure, returns:
                - {"error": "No uptime received."}
                - {"error": <exception message>} if the subprocess fails
                - {"error": "Non-integer output", "raw": <raw output>} if the CLI returns non-numeric text

        Example:
            >>> rpc = EvrmoreRPC(cli_path="evrmore-cli", datadir="/home/aethyn/.evrmore-test/testnet1", rpc_user="neubtrino_testnet", rpc_pass="pass_testnet", testnet=True)
            >>> uptime_val = rpc.uptime()
            >>> isinstance(uptime_val, str)
            True
            >>> len(uptime_val.split(":")) == 4 or "error" in uptime_val
            True
        """

        def seconds_to_dhms(seconds):
            """Convert seconds to dd:hh:mm:ss format with leading zeros."""
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{days:02}:{hours:02}:{minutes:02}:{secs:02}"

        # Build CLI command to query uptime
        command = self._build_command() + ["uptime"]

        try:
            # Execute command and capture output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Parse output to int and format as dd:hh:mm:ss
                    seconds = int(result.stdout.strip())
                    return seconds_to_dhms(seconds)
                except ValueError:
                    return {"error": "Non-integer output", "raw": result.stdout.strip()}
            else:
                return {"error": "No uptime received."}
        except Exception as e:
            return {"error": str(e)}

