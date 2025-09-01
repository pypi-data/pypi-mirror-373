from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json


class GeneratingRPC:

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

    def generate(self, nblocks=1, maxtries=1000000):
        """
        Mine new blocks to a wallet address immediately.

        Executes the `generate` RPC command via the Evrmore CLI. This command triggers immediate
        mining of up to `nblocks` blocks using an address in the local wallet. It returns the list
        of newly generated block hashes.

        Parameters:
            nblocks (int, optional): Number of blocks to mine immediately (default is 1).
            maxtries (int, optional): Maximum number of iterations to attempt mining
                                      (default is 1,000,000). Higher values may be needed if blocks are slow to solve.

        Returns:
            list of str: A list of block hashes for the successfully mined blocks.

            On failure, returns:
                - {"error": "Received non-JSON output", "raw": <raw output>}
                - {"error": "No info available.  Check your wallet/node is running."}
                - {"error": <exception message>} if the subprocess fails

        Example:
            >>> rpc = EvrmoreRPC(cli_path="evrmore-cli", datadir="/home/aethyn/.evrmore-test/testnet1", rpc_user="neubtrino_testnet", rpc_pass="pass_testnet", testnet=True)
            >>> blocks = rpc.generate(nblocks=1)
        """
        # Build the CLI command for mining blocks
        command = self._build_command() + [
            "generate",
            str(nblocks),
            str(maxtries)
        ]

        try:
            # Execute the command and capture the output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Parse JSON-formatted list of block hashes
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    # If output isn't valid JSON, return raw output as an error
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                return {"error": "No info available.  Check your wallet/node is running."}
        except Exception as e:
            return {"error": str(e)}

    def generatetoaddress(self, nblocks=1, address="no_good_default_address", maxtries=1000000):
        """
        Mine new blocks immediately to a specific address.

        Executes the `generatetoaddress` RPC command via the Evrmore CLI. This mines `nblocks` blocks
        and sends the coinbase rewards to the specified address.

        Parameters:
            nblocks (int, optional): Number of blocks to mine (default: 1).
            address (str): The destination address for block rewards. Must be a valid Evrmore address.
            maxtries (int, optional): Maximum attempts to find a valid block (default: 1,000,000).

        Returns:
            list of str: A list of block hashes that were successfully mined and sent to the address.

            On failure, returns:
                - {"error": "Received non-JSON output", "raw": <raw output>}
                - {"error": "No info available.  Check your wallet/node is running."}
                - {"error": <exception message>} if the subprocess fails

        Example:
            >>> rpc = EvrmoreRPC(cli_path="evrmore-cli", datadir="/home/aethyn/.evrmore-test/testnet1", rpc_user="neubtrino_testnet", rpc_pass="pass_testnet", testnet=True)
            >>> myaddr = "someValidEVRTestnetAddress"
            >>> blocks = rpc.generatetoaddress(nblocks=1, address=myaddr)
        """
        # Construct the CLI command to mine blocks to a specific address
        command = self._build_command() + [
            "generatetoaddress",
            str(nblocks),
            str(address),
            str(maxtries)
        ]

        try:
            # Run the CLI command and capture stdout and stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Parse block hashes as a JSON array
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                return {"error": "No info available.  Check your wallet/node is running."}
        except Exception as e:
            return {"error": str(e)}

    def getgenerate(self):
        """
        Check whether the node is set to generate (mine) blocks automatically.

        Executes the `getgenerate` RPC command via the Evrmore CLI. This returns a boolean value
        indicating whether the node is configured to mine (either via `-gen` or `setgenerate true`).

        Returns:
            bool: True if the node is set to generate blocks, False otherwise.

            On failure, returns:
                - {"error": "Received non-JSON output", "raw": <raw output>}
                - {"error": "No info available.  Check your wallet/node is running."}
                - {"error": <exception message>} if the subprocess fails

        Example:
            >>> rpc = EvrmoreRPC(cli_path="evrmore-cli", datadir="/home/aethyn/.evrmore-test/testnet1", rpc_user="neubtrino_testnet", rpc_pass="pass_testnet", testnet=True)
            >>> gen = rpc.getgenerate()
        """
        # Build CLI command to check mining state
        command = self._build_command() + ["getgenerate"]

        try:
            # Run the command and capture output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Expecting "true" or "false" -> parse as JSON boolean
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                return {"error": "No info available.  Check your wallet/node is running."}
        except Exception as e:
            return {"error": str(e)}

    def setgenerate(self, generate=True, num_processors=1):
        """
        Enable or disable block generation (mining) on the Evrmore node.

        Executes the `setgenerate` RPC command via the Evrmore CLI. This turns mining on or off
        and sets a limit for how many processor cores may be used.

        Parameters:
            generate (bool, optional): Whether to enable (`True`) or disable (`False`) mining (default: True).
            num_processors (int, optional): Maximum number of processor threads to use.
                                            Set to -1 for unlimited (default: 1).

        Returns:
            str: A message indicating that generation was enabled or disabled.

            On failure, returns:
                - {"error": <exception message>} if the subprocess fails

        Example:
            >>> rpc = EvrmoreRPC(cli_path="evrmore-cli", datadir="/home/aethyn/.evrmore-test/testnet1", rpc_user="neubtrino_testnet", rpc_pass="pass_testnet", testnet=True)
            >>> result = rpc.setgenerate(True, 2)
        """
        # Build the CLI command
        command = self._build_command() + [
            "setgenerate",
            str(generate).lower(),
            str(num_processors)
        ]

        try:
            # Run the command and capture any output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # No stdout is expected from setgenerate if successful
            return f"Mining {'enabled' if generate else 'disabled'} with processor limit {num_processors}"
        except Exception as e:
            return {"error": str(e)}
