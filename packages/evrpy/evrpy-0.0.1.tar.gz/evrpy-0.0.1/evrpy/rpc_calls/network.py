from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json


class NetworkRPC:

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

    def addnode(self, node, node_command):
        """
        Attempts to add, remove, or try connecting to a peer node.

        This RPC call allows you to manage the peer connection list by adding or removing nodes from it,
        or by attempting a one-time connection to a node without adding it persistently.

        Parameters:
            node (str): The IP address and port of the peer node (e.g., "192.168.0.6:8819").
            node_command (str): The command to perform. Must be one of:
                                - "add" to add the node to the list
                                - "remove" to remove the node from the list
                                - "onetry" to try connecting to the node once

        Returns:
            dict: A dictionary containing either a success message or an error message.
                  Successful calls typically return:
                  {
                      "message": "Node successfully added/removed/onetry"
                  }

        Example:
            >>> rpc = NetworkRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass",
            ... testnet=True)
            >>> rpc.addnode("192.168.0.6:8819", "add")
        """

        # Construct the full command with node and command type
        command = self._build_command() + [
            "addnode",
            str(node),
            str(node_command)
        ]

        try:
            # Run the command and capture output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout.strip():
                try:
                    # Try to parse the response in case it's JSON (unusual for this command)
                    return json.loads(result.stdout.strip())
                except json.JSONDecodeError:
                    # Return the raw string if not valid JSON (still successful)
                    return {"message": "Command executed successfully", "raw": result.stdout.strip()}
            else:
                # Success case: many addnode calls return no output on success
                return {"message": "Node successfully added/removed/onetry"}
        except Exception as e:
            # Handle subprocess or execution error
            return {"error": str(e)}

    def clearbanned(self):
        """
        Clear all banned IPs from the ban list.

        This method issues the `clearbanned` RPC command, which removes all currently
        banned IP addresses from the node's memory. Useful when managing peer bans manually.

        Returns:
            dict: If successful, returns a message indicating silent success.
                  If there is an error or the output is non-JSON, it returns a dictionary
                  with an "error" key or a "raw" key for debugging purposes.

        Example:
            >>> rpc = NetworkRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> result = rpc.clearbanned()
        """
        command = self._build_command() + [
            "clearbanned"
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
                return {"message": "Silent success."}
        except Exception as e:
            # Return any exception encountered during execution
            return {"error": str(e)}


    def disconnectnode(self, ip_address=None, node_id=None):
        """
            Immediately disconnects from the specified peer node using either its IP address or node ID.

            Only one of `ip_address` or `node_id` should be provided. If both are passed, `ip_address` takes precedence.

            Args:
                ip_address (str, optional): The IP address and port of the peer to disconnect, e.g., "192.168.0.6:8819".
                node_id (int, optional): The numeric node ID (retrievable via getpeerinfo).

            Returns:
                dict: A success message if disconnect was silent, or the parsed result or error details.

            Raises:
                ValueError: If neither `ip_address` nor `node_id` is provided.

            Example:
                >>> rpc = NetworkRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
                >>> result = rpc.disconnectnode(ip_address="192.168.0.6:8819")
            """
        #  Validate the arguments
        if ip_address is not None:
            command = self._build_command() + [
                "disconnectnode",
                str(ip_address)
            ]
        # now use an empty string if you're only passing node_id
        elif node_id is not None:
            command = self._build_command() + [
                "disconnectnode",
                "",
                str(node_id)
            ]
        # if the ip address or node id is not provided, raise an error.
        else:
            raise ValueError("You must provide either the ip address or node id.")

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
                return {"message": "Silent success."}
        except Exception as e:
            # Return any exception encountered during execution
            return {"error": str(e)}


    def getaddednodeinfo(self, ip_address=None):
        """
        Returns information about the given added node, or all added nodes if no IP is specified.

        Args:
            ip_address (str, optional): The IP address of a specific node added via `addnode`.
                If not provided, information about all added nodes will be returned.

        Returns:
            dict or list: Parsed JSON response from the CLI if successful, or an error dictionary.

        Example:
            >>> rpc = NetworkRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> result = rpc.getaddednodeinfo()
        """
        if ip_address is not None:
            command = self._build_command() + [
                "getaddednodeinfo",
                str(ip_address)
            ]
        else:
            command = self._build_command() + [
                "getaddednodeinfo"
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
                return {"message": "Silent success."}
        except Exception as e:
            # Return any exception encountered during execution
            return {"error": str(e)}

    def getconnectioncount(self):
        """
        Returns the number of active connections to other nodes.

        This RPC call returns a numeric value representing how many peers
        the node is currently connected to.

        Returns:
            int or dict: Integer count of current connections, or an error dictionary.

        Example:
            >>> rpc = NetworkRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> result = rpc.getconnectioncount()
        """
        # Build the command to get the number of peer connections
        command = self._build_command() + ["getconnectioncount"]

        try:
            # Execute the CLI command and capture output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Parse the output (expected to be a simple integer)
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    # If parsing fails, return the raw output with an error message
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # Command executed but produced no output
                return {"message": "Silent success."}
        except Exception as e:
            # Return any error raised during subprocess execution
            return {"error": str(e)}


    def getnettotals(self):
        """
        Returns information about network traffic including bytes received,
        bytes sent, current time, and upload target stats.

        This RPC call is useful for monitoring overall data usage and
        bandwidth-related policy configurations.

        Returns:
            dict: Dictionary containing keys like 'totalbytesrecv', 'totalbytessent',
                  'timemillis', and 'uploadtarget', or an error dictionary on failure.

        Example:
            >>> rpc = NetworkRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> result = rpc.getnettotals()

        """
        command = self._build_command() + [
            "getnettotals"
        ]

        try:
            # Execute the CLI command and capture output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Parse the output (expected to be a simple integer)
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    # If parsing fails, return the raw output with an error message
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # Command executed but produced no output
                return {"message": "Silent success."}
        except Exception as e:
            # Return any error raised during subprocess execution
            return {"error": str(e)}

    def getnetworkinfo(self):
        """
        Returns networking-related state information from the Evrmore node.

        Returns:
            dict: A dictionary containing server version, subversion, connections,
                  relay fee, local services, reachable network status, and more.

        Example:
            >>> rpc = NetworkRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> result = rpc.getnetworkinfo()
        """

        command = self._build_command() + [
            "getnetworkinfo"
        ]

        try:
            # Execute the CLI command and capture output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Parse the output (expected to be a simple integer)
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    # If parsing fails, return the raw output with an error message
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # Command executed but produced no output
                return {"message": "Silent success."}
        except Exception as e:
            # Return any error raised during subprocess execution
            return {"error": str(e)}

    def getpeerinfo(self):
        """
        Returns data about each connected network node as a JSON array of objects.

        Returns:
            dict or list: A list of dictionaries, each containing peer connection data,
                          such as IP address, connection time, services, bytes sent/received,
                          and version info.

        Example:
            >>> rpc = NetworkRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> result = rpc.getpeerinfo()
        """

        command = self._build_command() + [
            "getpeerinfo"
        ]

        try:
            # Execute the CLI command and capture output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Parse the output (expected to be a simple integer)
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    # If parsing fails, return the raw output with an error message
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # Command executed but produced no output
                return {"message": "Silent success."}
        except Exception as e:
            # Return any error raised during subprocess execution
            return {"error": str(e)}

    def listbanned(self):
        """
        List all banned IP addresses and subnets.

        Returns:
            list or dict: A list of banned IP/subnet entries with details such as ban reason,
                          creation time, and ban duration. If an error occurs, a dictionary
                          with an 'error' key will be returned.

        Example:
            >>> rpc = NetworkRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> result = rpc.listbanned()
        """

        command = self._build_command() + [
            "listbanned"
        ]

        try:
            # Execute the CLI command and capture output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Parse the output (expected to be a simple integer)
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    # If parsing fails, return the raw output with an error message
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # Command executed but produced no output
                return {"message": "Silent success."}
        except Exception as e:
            # Return any error raised during subprocess execution
            return {"error": str(e)}

    def ping(self):
        """
        Request a ping to all connected peers to measure network latency and backlog.

        This does not return immediate results. Instead, use `getpeerinfo()` to view updated `pingtime` and `pingwait` values.

        Returns:
            dict: A message indicating silent success or an error dictionary if execution fails.

        Example:
            >>> rpc = NetworkRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> result = rpc.ping()
            >>> isinstance(result, dict)
            True
        """

        command = self._build_command() + [
            "ping"
        ]

        try:
            # Execute the CLI command and capture output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Parse the output (expected to be a simple integer)
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    # If parsing fails, return the raw output with an error message
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # Command executed but produced no output
                return {"message": "Silent success."}
        except Exception as e:
            # Return any error raised during subprocess execution
            return {"error": str(e)}

    def setban(self, subnet, rpc_command, bantime=None, absolute=None):
        """
        Attempts to add or remove an IP/Subnet from the banned list.

        Args:
            subnet (str): The IP or subnet to ban (e.g., "192.168.0.6" or "192.168.0.0/24").
            rpc_command (str): Either "add" or "remove".
            bantime (int, optional): Duration in seconds to ban. Defaults to 24 hours unless specified.
            absolute (bool, optional): Whether the bantime is an absolute timestamp.

        Returns:
            dict: Parsed response, or an error dictionary if the output is invalid or an exception occurs.

        Example:
            >>> rpc = NetworkRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> result = rpc.setban("192.168.0.6", "add", 86400)
        """

        command = self._build_command() + [
            "setban",
            str(subnet),
            str(rpc_command)
        ]

        if bantime is not None:
            command.append(str(bantime))
        if absolute is not None:
            command.append(str(absolute).lower())

        try:
            # Execute the CLI command and capture output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Parse the output (expected to be a simple integer)
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    # If parsing fails, return the raw output with an error message
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # Command executed but produced no output
                return {"message": "Silent success."}
        except Exception as e:
            # Return any error raised during subprocess execution
            return {"error": str(e)}

    def setnetworkactive(self, state):
        """
        Enable or disable all P2P network activity.

        Args:
            state (bool): Set to True to enable networking, or False to disable it.

        Returns:
            dict: Parsed JSON response if successful, or a dictionary with an error message.

        Example:
            >>> rpc = NetworkRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> result = rpc.setnetworkactive(True)
            >>> isinstance(result, dict)
            True
        """

        command = self._build_command() + [
            "setnetworkactive",
            str(state).lower()
        ]

        try:
            # Execute the CLI command and capture output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Parse the output (expected to be a simple integer)
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    # If parsing fails, return the raw output with an error message
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # Command executed but produced no output
                return {"message": "Silent success."}
        except Exception as e:
            # Return any error raised during subprocess execution
            return {"error": str(e)}

