from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json


class MessagesRPC:

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

    def clearmessages(self):
        """
        Delete the current message database from the Evrmore node.

        Executes the `clearmessages` RPC command via the Evrmore CLI. This permanently deletes
        all stored messages in the node’s message system.

        Returns:
            str: A success confirmation string (e.g., "Message database cleared.") or empty string if successful.

            On failure, returns:
                - {"error": "No response received."}
                - {"error": <exception message>} if the subprocess fails

        Example:
            >>> rpc = EvrmoreRPC(cli_path="evrmore-cli", datadir="/home/aethyn/.evrmore-test/testnet1", rpc_user="neubtrino_testnet", rpc_pass="pass_testnet", testnet=True)
            >>> result = rpc.clearmessages()
            >>> isinstance(result, str) or "error" in result
            True
        """
        # Build CLI command to clear messages
        command = self._build_command() + ["clearmessages"]

        try:
            # Execute the command and capture output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout.strip():
                return result.stdout.strip()  # Return any confirmation string if present
            else:
                return "Message database cleared."  # Assume success on empty output
        except Exception as e:
            return {"error": str(e)}

    def sendmessage(self, channel_name, ipfs_hash, expire_time=None):
        """
        Send a message to a channel using an IPFS hash.

        Executes the `sendmessage` RPC command via the Evrmore CLI. This creates and broadcasts
        a message transaction to the network for a channel owned by the wallet. The message data
        is stored on IPFS, referenced by the given hash.

        Parameters:
            channel_name (str): The name of the message channel (asset admin). If it lacks '!', it will be added automatically.
            ipfs_hash (str): The IPFS hash of the message content.
            expire_time (int, optional): UTC timestamp when the message should expire.

        Returns:
            list of str: A list containing the transaction ID of the message transaction.

            On failure, returns:
                - {"error": "Received non-JSON output", "raw": <raw output>}
                - {"error": "No info available.  Check your wallet/node is running."}
                - {"error": <exception message>} if the subprocess fails

        Example:
            >>> rpc = EvrmoreRPC(cli_path="evrmore-cli", datadir="/home/aethyn/.evrmore-test/testnet1", rpc_user="neubtrino_testnet", rpc_pass="pass_testnet", testnet=True)
            >>> tx = rpc.sendmessage("MYCHANNEL!", "QmTqu3Lk3gmTsQVtjU7rYYM37EAW4xNmbuEAp2Mjr4AV7E")
        """
        # Construct CLI command based on whether expire_time is provided
        # If no expire_time, use the 2-argument version of sendmessage
        if expire_time is None:
            command = self._build_command() + [
                "sendmessage",             # RPC method
                str(channel_name),         # Required: message channel (must end in '!')
                str(ipfs_hash)             # Required: IPFS hash of the message
            ]
        else:
            # If expire_time is provided, include it as a third argument
            command = self._build_command() + [
                "sendmessage",             # RPC method
                str(channel_name),         # Required: message channel
                str(ipfs_hash),            # Required: IPFS hash
                str(expire_time)           # Optional: UTC timestamp for expiration
            ]

        try:
            # Execute the CLI command and capture both stdout and stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Attempt to parse the response as JSON
                    # Expected: a JSON list containing one transaction ID (txid)
                    parsed = json.loads(result.stdout.strip())
                    return parsed  # Return the txid as a list
                except json.JSONDecodeError:
                    # If the output isn't valid JSON, return the raw string for debugging
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # If no output was returned, the RPC call may have failed silently
                return {"error": "No info available.  Check your wallet/node is running."}
        except Exception as e:
            # If the subprocess command itself failed (e.g., CLI missing, bad args), capture the error
            return {"error": str(e)}


    def subscribetochannel(self, channel_name):
        """
        Subscribe to a message channel by name (requires '!' or '~').

        Executes the `subscribetochannel` RPC command via the Evrmore CLI.
        Automatically appends '!' to the channel name if it's not present.

        Parameters:
            channel_name (str): The name of the channel to subscribe to.

        Returns:
            str: Success message or CLI output if present.

            On failure, returns:
                - {"error": <exception message>} if the subprocess fails

        Example:
            >>> rpc = EvrmoreRPC(cli_path="evrmore-cli", datadir="...", rpc_user="...", rpc_pass="...", testnet=True)
            >>> result = rpc.subscribetochannel("MYASSET")
        """
        # Ensure channel_name is a string (in case it was passed as int, etc.)
        channel_name = str(channel_name)

        # Ensure the channel name is valid:
        # - Must end in '!' (for admin channels), unless it's a '~' channel (anonymous/pseudonymous)
        if not channel_name.endswith("!") and "~" not in channel_name:
            channel_name += "!"  # Append '!' if missing and not a '~' channel

        # Build the CLI command to subscribe to the specified channel
        command = self._build_command() + [
            "subscribetochannel",  # RPC command
            channel_name           # Properly formatted channel name
        ]

        try:
            # Execute the CLI command and capture stdout and stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # If the command returns any output, return it
            if result.stdout.strip():
                return result.stdout.strip()

            # If no output is returned (common for success cases), return a default confirmation message
            else:
                return f"Subscribed to channel: {channel_name}"
        except Exception as e:
            # If the command fails (e.g., bad channel name, CLI error), return the exception message
            return {"error": str(e)}



    def unsubscribefromchannel(self, channel_name):
        """
        Subscribe to a message channel by name (requires '!' or '~').

        Executes the `unsubscribefromchannel` RPC command via the Evrmore CLI.
        Automatically appends '!' to the channel name if it's not present.

        Parameters:
            channel_name (str): The name of the channel to unsubscribe from.

        Returns:
            str: Success message or CLI output if present.

            On failure, returns:
                - {"error": <exception message>} if the subprocess fails

        Example:
            >>> rpc = EvrmoreRPC(cli_path="evrmore-cli", datadir="...", rpc_user="...", rpc_pass="...", testnet=True)
            >>> result = rpc.unsubscribetochannel("MYASSET")
        """
        # Ensure channel_name is a string (in case the caller passed an int or other type)
        channel_name = str(channel_name)

        # Validate and normalize the channel name format:
        # - Must end in '!' for administrator channels, unless it's a '~' pseudonymous channel
        if not channel_name.endswith("!") and "~" not in channel_name:
            channel_name += "!"  # Append '!' if needed to make it a valid admin channel

        # Build the CLI command to unsubscribe from the specified channel
        command = self._build_command() + [
            "unsubscribefromchannel",  # RPC method to unsubscribe
            channel_name               # Sanitized and formatted channel name
        ]

        try:
            # Execute the CLI command and capture stdout and stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # If the command returns output (confirmation or warning), return it as-is
            if result.stdout.strip():
                return result.stdout.strip()

            # If there's no output, assume successful unsubscribe and return default message
            else:
                return f"Unsubscribed from channel: {channel_name}"
        except Exception as e:
            # If the CLI fails (e.g., channel not found or invalid format), return the error message
            return {"error": str(e)}

    def viewallmessagechannels(self):
        """
        View all message channels that the wallet is currently subscribed to.

        Executes the `viewallmessagechannels` RPC command via the Evrmore CLI.
        This returns a list of asset channel names (strings) that the wallet
        is subscribed to for receiving IPFS messages.

        Returns:
            list of str: A list of channel names (e.g., ["MYASSET!", "~testchannel"]).

            On failure, returns:
                - {"error": "Received non-JSON output", "raw": <raw output>}
                - {"error": "No info available.  Check your wallet/node is running."}
                - {"error": <exception message>} if the subprocess fails

        Example:
            >>> rpc = EvrmoreRPC(cli_path="evrmore-cli", datadir="/home/aethyn/.evrmore-test/testnet1", rpc_user="neubtrino_testnet", rpc_pass="pass_testnet", testnet=True)
            >>> channels = rpc.viewallmessagechannels()
        """
        # Build the CLI command to list all subscribed message channels
        command = self._build_command() + [
            "viewallmessagechannels"
        ]

        try:
            # Execute the CLI command and capture stdout and stderr
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Attempt to parse the JSON response (expected: list of strings)
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    # If output isn't valid JSON, return the raw text for debugging
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # If output is empty, treat as a failure to retrieve subscriptions
                return {"error": "No info available.  Check your wallet/node is running."}
        except Exception as e:
            # Catch and return any subprocess execution errors
            return {"error": str(e)}

    def viewallmessages(self):
        """
        Retrieve all messages that the wallet currently contains.

        Executes the `viewallmessages` RPC command via the Evrmore CLI. This returns a list of
        message entries the wallet has received through subscribed channels.

        Each message contains details like:
            - Asset channel name
            - IPFS hash of the message
            - Timestamp
            - Block height
            - Message status (e.g., READ, UNREAD, EXPIRED)
            - Optional expiration time

        Returns:
            list of dict: Each dict contains:
                - "Asset Name" (str): Channel the message was sent on
                - "Message" (str): IPFS hash of the message content
                - "Time" (str): Timestamp in format "YY-mm-dd HH-MM-SS"
                - "Block Height" (int): Block number where message was included
                - "Status" (str): One of READ, UNREAD, ORPHAN, EXPIRED, SPAM, etc.
                - Optional: "Expire Time", "Expire UTC Time" (as date strings)

            On failure, returns:
                - {"error": "Received non-JSON output", "raw": <raw output>}
                - {"error": "No info available.  Check your wallet/node is running."}
                - {"error": <exception message>} if the subprocess fails

        Example:
            >>> rpc = EvrmoreRPC(cli_path="evrmore-cli", datadir="/home/aethyn/.evrmore-test/testnet1", rpc_user="neubtrino_testnet", rpc_pass="pass_testnet", testnet=True)
            >>> msgs = rpc.viewallmessages()
        """
        # Build the CLI command to fetch all messages visible to the wallet
        command = self._build_command() + [
            "viewallmessages"
        ]

        try:
            # Run the CLI command and capture the output and errors
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Parse the response as JSON (expecting a list of message dicts)
                    parsed = json.loads(result.stdout.strip())
                    return parsed
                except json.JSONDecodeError:
                    # If parsing fails, return the raw output for inspection
                    return {"error": "Received non-JSON output", "raw": result.stdout.strip()}
            else:
                # If there's no output at all, assume a problem with node or message list
                return {"error": "No info available.  Check your wallet/node is running."}
        except Exception as e:
            # Return any CLI or subprocess-related error
            return {"error": str(e)}
