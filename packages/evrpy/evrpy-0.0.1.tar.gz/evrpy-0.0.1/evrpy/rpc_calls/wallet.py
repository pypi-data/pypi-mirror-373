from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json



class WalletRPC:

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

        self.cli_path = cli_path
        self.datadir = datadir
        self.rpc_user = rpc_user
        self.rpc_pass = rpc_pass
        self.testnet = testnet

    def _build_command(self):
        """
        Create the base command-line argument list to invoke `evrmore-cli` with the current client configuration.

        Returns:
            list: Command-line arguments representing the base CLI call, including authentication and network mode.
        """

        return build_base_command(
            self.cli_path,
            self.datadir,
            self.rpc_user,
            self.rpc_pass,
            self.testnet
        )

    def abandontransaction(self, txid):
        """
        Marks an in-wallet transaction (and its in-wallet descendants) as **abandoned**.

        Invokes the `abandontransaction` RPC. Abandoning a transaction frees up its inputs so
        they can be respent. This is useful for replacing **stuck** or **evicted** transactions
        that are neither confirmed in a block nor currently in the mempool.

        Mirrors native help:

            abandontransaction "txid"

            Mark in-wallet transaction <txid> as abandoned.
            This will mark this transaction and all its in-wallet descendants as abandoned which
            will allow for their inputs to be respent. It can be used to replace "stuck" or
            evicted transactions. It only works on transactions which are not included in a block
            and are not currently in the mempool. It has no effect on transactions which are
            already conflicted or abandoned.

        Args:
            txid (str):
                The transaction id (hex) of the **in-wallet** transaction to abandon.

        Returns:
            str | dict | None:
                - If the node prints nothing (common for this RPC), returns the string
                  `"Transaction abandoned."` to acknowledge success.
                - If the node returns JSON, the parsed object is returned.
                - If the node returns non-JSON text, that raw text is returned.
                - On error, returns `"Error: <message>"`.

        Notes:
            - **Preconditions**: The target transaction must be:
                * in your wallet,
                * **not** in a block (unconfirmed),
                * **not** currently in the mempool.
            - Descendants (in-wallet) are also abandoned as part of this operation.
            - Does **not** affect transactions already marked **conflicted** or **abandoned**.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> out = rpc.abandontransaction("1075db55d416d3ca199f55b6084e2115b9345e16c5cf302fc80e9d5fbf5d48d")
        """

        # Build the CLI command with wallet/auth/network flags + RPC + required argument.
        command = self._build_command() + [
            "abandontransaction",
            str(txid),  # txid of the in-wallet, unconfirmed, non-mempool transaction
        ]

        try:
            # Execute the command. On non-zero return codes, CalledProcessError is raised.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout for parsing/inspection.
            out = (result.stdout or "").strip()

            # Many wallet RPCs return empty output on success; provide a friendly confirmation.
            if not out:
                return "Transaction abandoned."

            # Attempt JSON parse first; fall back to raw string if not JSON.
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Concise error reporting per your style.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()


    def abortrescan(self):
        """
        Requests the wallet to stop an in-progress rescan.

        Invokes the `abortrescan` RPC. Useful when a long-running rescan (e.g., after
        `importprivkey`) is underway and you need to cancel it.

        Mirrors native help:

            abortrescan
            Stops current wallet rescan triggered e.g. by an importprivkey call.

        Returns:
            bool | str:
                - `True`  → the node accepted the abort and a rescan was in progress.
                - `False` → no rescan was in progress (nothing to abort).
                - If the node returns non-JSON output, that raw string is returned.
                - If there is no output, returns "No output (rescan may not have been running)."
                - On error, returns: "Error: <node stderr or exception message>"

        Notes:
            - The abort is a request; the rescan may take a moment to fully stop.
            - No arguments; this affects the current wallet only.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> ok = rpc.abortrescan()
            >>> isinstance(ok, (bool, str))
            True
        """

        # Build the CLI command with wallet/auth/network flags + RPC name (no params).
        command = self._build_command() + ["abortrescan"]

        try:
            # Execute the command. Non-zero exit codes raise CalledProcessError.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout; guard against None and strip whitespace/newlines.
            out = (result.stdout or "").strip()
            if not out:
                return "No output (rescan may not have been running)."

            # Try to parse as JSON (expected: boolean true/false).
            try:
                parsed = json.loads(out)
                if isinstance(parsed, bool):
                    return parsed
                return str(parsed)  # Unexpected JSON type; return as string for transparency.
            except json.JSONDecodeError:
                # Handle plain-text booleans and otherwise return the raw payload.
                low = out.lower()
                if low == "true":
                    return True
                if low == "false":
                    return False
                return out

        except Exception as e:
            # Use the standardized error format you requested (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def addmultisigaddress(self, nrequired, keys, account=None):
        """
        Adds an n-of-m multisig address to the wallet and returns the new address.

        Invokes the `addmultisigaddress` RPC. You specify how many signatures are required
        (`nrequired`) and provide the set of participant keys as **Evrmore addresses or
        hex-encoded public keys**. The legacy `account` argument is **deprecated** and optional.

        Mirrors native help:

            addmultisigaddress nrequired ["key", ...] ( "account" )

            1. nrequired    (numeric, required) Number of required signatures out of the n keys
            2. "keys"       (string, required) JSON array of Evrmore addresses or hex pubkeys
                             [
                               "address_or_hexpubkey",
                               ...
                             ]
            3. "account"    (string, optional) DEPRECATED. Account label.

        Args:
            nrequired (int):
                Number of required signatures (must be ≤ len(keys)).
            keys (list[str] | tuple[str] | str):
                The **set of signers** as Evrmore addresses or hex-encoded public keys.
                - If a **list/tuple** is provided, it will be serialized to a JSON array for the CLI.
                - If a **pre-serialized JSON string** is provided (e.g., '["addr1","addr2"]'),
                  it will be passed through as-is.
            account (str, optional):
                **Deprecated** account label to associate with the new multisig address.

        Returns:
            str:
                On success, the newly created **multisig Evrmore address**.
                If the node returns non-JSON text, that raw text is returned.
                On error, returns: `"Error: <node stderr or exception message>"`.

        Notes:
            - Ensure `nrequired <= len(keys)`, otherwise the node will error.
            - Keys may be **addresses** or **hex pubkeys** (mixing is allowed).
            - This call **adds** the address to the current wallet; it does not broadcast anything.
            - The `"account"` argument is deprecated and may be ignored by modern setups.

        Example:
            Create a 2-of-2 multisig from two addresses:

            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> addr = rpc.addmultisigaddress(2, ["n2FirstAddressXXXXXXXXXXXXXXX", "n3SecondAddressXXXXXXXXXXXXXX"])

            Create a 2-of-3 multisig using hex public keys:

            >>> keys = [
            ...   "0250863AD64A87AE8A2FE83C1AF1A8403CB55A1D...<trimmed>",
            ...   "03A34B7E8C0F3E3B11D24B3E6B1B...<trimmed>",
            ...   "02F01A1C2B...<trimmed>"
            ... ]
            >>> addr = rpc.addmultisigaddress(2, keys)

        """

        # --- Build CLI arguments in the exact order expected by the node -------------------------
        # nrequired must be numeric; convert safely to int then to str for the subprocess call.
        nrequired_str = str(int(nrequired))

        # The CLI expects the "keys" parameter as a **single JSON array string**.
        # If the caller passed a Python list/tuple, serialize it; if it's already a JSON string,
        # pass it through unchanged.
        if isinstance(keys, (list, tuple)):
            keys_arg = json.dumps(list(keys))
        else:
            keys_arg = str(keys)  # assume caller provided a JSON array string

        args = ["addmultisigaddress", nrequired_str, keys_arg]

        # Append the deprecated account label only if provided.
        if account is not None:
            args.append(str(account))

        command = self._build_command() + args

        try:
            # Execute the command and capture output.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                # Core-like nodes typically return the address string; if empty, surface something helpful.
                return "No address returned."

            # Try JSON first; many implementations return a plain string (non-JSON), so fall back gracefully.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def addwitnessaddress(self, address):
        """
        Adds a witness address (P2SH-wrapped witness script) for a known script/address.

        Invokes the `addwitnessaddress` RPC. Given an address whose **pubkey or redeemscript is
        already known to the wallet**, this creates and returns a corresponding **witness address**
        (P2SH of the witness script). This is typically used to receive to a SegWit-wrapped form
        of an existing script that your wallet can already satisfy.

        Mirrors native help:

            addwitnessaddress "address"

            Add a witness address for a script (with pubkey or redeemscript known).
            It returns the witness script.

        Args:
            address (str):
                An address already known to the wallet (its pubkey or redeemscript must be known).
                If the wallet doesn't know the key/script yet, import it first (e.g., `importprivkey`,
                `importaddress`, or equivalent).

        Returns:
            str:
                On success, the **witness address** (string, P2SH of witness script).
                If the node returns non-JSON text, that raw text is returned.
                On error, returns: `"Error: <node stderr or exception message>"`.

        Notes:
            - This does **not** broadcast a transaction; it derives/creates a witness form in your wallet.
            - If the wallet does not recognize the key/script for `address`, the call will fail.
            - You can verify the returned address with `validateaddress`.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> waddr = rpc.addwitnessaddress("mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF")
        """

        # Build the CLI command with wallet/auth/network flags + RPC + required argument.
        command = self._build_command() + [
            "addwitnessaddress",
            str(address),
        ]

        try:
            # Execute the command. Non-zero exit raises CalledProcessError (we'll surface stderr below).
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout; some nodes return a plain string, others may JSON-quote the string.
            out = (result.stdout or "").strip()
            if not out:
                return "No witness address returned."

            # Try JSON parsing first; fall back to raw string if not JSON.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def backupwallet(self, destination):
        """
        Backs up the current wallet file to the given destination.

        Invokes the `backupwallet` RPC. Safely copies the wallet to the specified
        **destination**, which can be either:
          - a **directory** (the node will create a file within it), or
          - a **full path with filename**.

        Mirrors native help:

            backupwallet "destination"

            Safely copies current wallet file to destination, which can be a
            directory or a path with filename.

        Args:
            destination (str):
                Destination directory **or** full path (including filename) for the backup.
                Absolute paths are recommended. If the path contains spaces, it’s fine—this
                wrapper does not invoke a shell.

        Returns:
            str:
                - If the node prints nothing (common on success), returns
                  **"Wallet backup completed."** for clarity.
                - If the node returns text/JSON, it is surfaced (parsed to string if JSON).
                - On error, returns: **"Error: <node stderr or exception message>"**.

        Notes:
            - This creates a **point-in-time** copy of the wallet file.
            - Consider stopping high-activity operations briefly for a consistent backup, or
              verify with a restore test in a safe environment.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> out = rpc.backupwallet("/tmp/evr_wallet_backup.dat")
        """

        # Build the CLI command with wallet/auth/network flags + RPC + required argument.
        command = self._build_command() + [
            "backupwallet",
            str(destination),
        ]

        try:
            # Execute the command. Non-zero exit codes raise CalledProcessError.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout for parsing; many nodes return empty output on success.
            out = (result.stdout or "").strip()
            if not out:
                return "Wallet backup completed."

            # Try to parse JSON first; fall back to raw text if not JSON.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def dumpprivkey(self, address):
        """
        Reveals the private key (WIF) for a wallet-known address.

        Invokes the `dumpprivkey` RPC. Given an address that belongs to (or is known by) the
        current wallet, this returns its corresponding **private key** in WIF format. You can
        later import this key into another wallet using `importprivkey`.

        Mirrors native help:

            dumpprivkey "address"

            Reveals the private key corresponding to 'address'.
            Then the importprivkey can be used with this output.

        Args:
            address (str):
                The Evrmore address whose private key you want to export. The address must be
                known to the current wallet (i.e., generated/imported there). If the wallet is
                encrypted, it must be **unlocked** before calling this RPC.

        Returns:
            str:
                - On success: the private key in **WIF** (Wallet Import Format).
                - If the node returns non-JSON text (typical), the raw string is returned.
                - If there’s no output, returns "No private key returned."
                - On error, returns: "Error: <node stderr or exception message>"

        Security Notes:
            - **Handle with extreme care.** Anyone with this key can spend the funds.
            - Avoid logging or printing the key; if you do, sanitize your logs immediately.
            - Prefer exporting/handling keys on an **offline** or trusted system.
            - Consider rotating funds to a fresh address after exposure.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> wif = rpc.dumpprivkey("mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF")
        """

        # Build the CLI command with wallet/auth/network flags + RPC + required argument.
        command = self._build_command() + [
            "dumpprivkey",
            str(address),
        ]

        try:
            # Execute the command. Non-zero exit codes raise CalledProcessError.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout; many nodes return a plain WIF string.
            out = (result.stdout or "").strip()
            if not out:
                return "No private key returned."

            # Try JSON first (some builds might JSON-quote the string), else return raw text.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def dumpwallet(self, filename):
        """
        Dumps all wallet keys to a server-side file (human-readable format).

        Invokes the `dumpwallet` RPC. The node writes out a text file containing **all wallet keys**
        and related metadata. This is created on the **server side** (where `evrmored` is running)
        and **will not overwrite** an existing file of the same name.

        Mirrors native help:

            dumpwallet "filename"

            Dumps all wallet keys in a human-readable format to a server-side file.
            This does not allow overwriting existing files.

        Args:
            filename (str):
                The output file name **with path** (absolute, or relative to `evrmored`’s working dir).
                If the path includes spaces, it's fine—this wrapper does not invoke a shell.

        Returns:
            dict | str:
                - On success (typical): a dict containing:
                    { "filename": "<absolute_path_written_by_node>" }
                - If the node returns non-JSON text, that raw string is returned.
                - If there’s no output, returns "No data returned."
                - On error, returns: "Error: <node stderr or exception message>"

        Security Notes:
            - The dump contains **private keys**. Treat it like a secret:
              * Store securely (encrypted volume, restricted permissions).
              * Avoid backups to untrusted services.
              * Consider rotating funds afterward.
            - If your wallet is encrypted, you must **unlock** before calling this RPC.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> out = rpc.dumpwallet("/tmp/evr_wallet_dump.txt")
            >>> isinstance(out, (dict, str))
            True
        """

        # Build the CLI command with wallet/auth/network flags + RPC + required argument.
        command = self._build_command() + [
            "dumpwallet",
            str(filename),
        ]

        try:
            # Execute the command. Non-zero exit codes raise CalledProcessError.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout; expected to be a small JSON object containing the absolute filename.
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Try to parse JSON first; fall back to raw string if not JSON.
            try:
                parsed = json.loads(out)
                return parsed
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def encryptwallet(self, passphrase):
        """
        Encrypts the wallet with the given passphrase (first-time encryption only).

        Invokes the `encryptwallet` RPC. After successful encryption:
          - The node **shuts down** immediately.
          - Future operations that use private keys (send/sign/etc.) will require unlocking
            with `walletpassphrase` (and you can relock with `walletlock`).
          - If the wallet is already encrypted, use `walletpassphrasechange` instead.

        Mirrors native help:

            encryptwallet "passphrase"

            Encrypts the wallet with 'passphrase'. This is for first time encryption.
            After this, any calls that interact with private keys such as sending or signing
            will require the passphrase to be set prior to making these calls.
            Use the walletpassphrase call for this, and then walletlock call.
            If the wallet is already encrypted, use the walletpassphrasechange call.
            Note that this will shutdown the server.

        Args:
            passphrase (str):
                The passphrase to encrypt the wallet with. Must be at least 1 character,
                but should be long and strong. Spaces are allowed.

        Returns:
            str:
                - On success: a status string from the node (typically indicating that the wallet
                  was encrypted and the server is stopping). Expect the daemon to shut down.
                - If no output is returned, the function returns: "Wallet encryption initiated; node is shutting down."
                - On error, returns: "Error: <node stderr or exception message>"

        Security Notes:
            - Choose a strong passphrase and **do not** log or print it.
            - After encrypting, consider making a **fresh backup** of the wallet file.
            - You must **restart** the node after this call completes.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",rpc_user="user", rpc_pass="pass", testnet=True)
            >>> msg = rpc.encryptwallet("passphrase")
        """

        # Build the CLI command with wallet/auth/network flags + RPC + required arg.
        # Passing as separate argv elements (no shell) safely handles spaces in passphrase.
        command = self._build_command() + [
            "encryptwallet",
            str(passphrase),
        ]

        try:
            # Execute the command. On success, the daemon will shut down immediately after responding.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout; many builds print a human-readable status string.
            out = (result.stdout or "").strip()
            if not out:
                return "Wallet encryption initiated; node is shutting down."

            # Try JSON in case the build returns a JSON-quoted string; otherwise return raw text.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getaccount(self, address):
        """
        (DEPRECATED) Returns the legacy account/label associated with an address.

        Invokes the `getaccount` RPC to fetch the **account name** (legacy label) tied to
        the given address. This interface is deprecated; modern wallets use label APIs such
        as `getaddressesbylabel` / `setlabel`.

        Mirrors native help:

            getaccount "address"

            DEPRECATED. Returns the account associated with the given address.

        Args:
            address (str):
                The Evrmore address to look up.

        Returns:
            str:
                - On success: the account/label string.
                - If the node returns non-JSON text, that raw text is returned.
                - If there’s no output, returns "No account returned."
                - On error, returns: "Error: <node stderr or exception message>"

        Notes:
            - This method is **deprecated**; prefer modern label-based RPCs when available.
            - The returned value may be an empty string if no legacy account is set.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> acct = rpc.getaccount("mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF")
        """

        # Build the CLI command with wallet/auth/network flags + RPC + required argument.
        command = self._build_command() + [
            "getaccount",
            str(address),
        ]

        try:
            # Execute the command. Non-zero exit codes raise CalledProcessError.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout; this RPC typically returns a plain string (the account/label).
            out = (result.stdout or "").strip()
            if not out:
                return "No account returned."

            # Try JSON first (some builds might JSON-quote the string); otherwise return raw text.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getaccountaddress(self, account=None):
        """
        (DEPRECATED) Returns the current receiving address for a legacy account.

        Invokes the `getaccountaddress` RPC. For the given legacy **account** name, this returns
        the current Evrmore address used to receive payments. If the account does not exist, the
        node will create it and also create a new receiving address.

        Mirrors native help:

            getaccountaddress "account"

            DEPRECATED. Returns the current Evrmore address for receiving payments to this account.

            1. "account" (string, required) The account name. It can be set to the empty string ""
               to represent the default account. The account does not need to exist; it will be
               created and a new address created if there is no account by the given name.

        Args:
            account (str | None, optional):
                - A legacy account (label) name.
                - Pass **""** (empty string) to target the **default** account explicitly.
                - Pass **None** to **omit the argument**, which most nodes treat as the default account.

        Returns:
            str:
                - On success: the receiving **address** (string).
                - If the node returns non-JSON text, that raw text is returned.
                - If there’s no output, returns "No address returned."
                - On error, returns: "Error: <node stderr or exception message>"

        Notes:
            - This interface is **deprecated**. Prefer modern label APIs (e.g., `getnewaddress` with a
              label, `getaddressesbylabel`, `setlabel`) when available.
            - Behavior differences:
                * `account=None`   → omit the param entirely (equivalent to default account on many nodes).
                * `account=""`     → send an explicit empty string param (default account).
                * `account="name"` → use/create that legacy account and return its current receiving address.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)

            # Default account via omitted parameter:
            >>> addr1 = rpc.getaccountaddress()


            # Default account via explicit empty string:
            >>> addr2 = rpc.getaccountaddress("")


            # A specific legacy account (will be created if missing):
            >>> addr3 = rpc.getaccountaddress("myaccount")
        """

        # Build the CLI command with wallet/auth/network flags + RPC name.
        # The "account" parameter is *deprecated* and can be omitted (defaults to "").
        command = self._build_command() + ["getaccountaddress"]

        # Only append the argument if the caller provided one.
        # - None  -> omit argument (node treats as default account)
        # - ""    -> send explicit empty string to target default account
        # - "abc" -> send provided account name
        if account is not None:
            command.append(str(account))

        try:
            # Execute the command. Non-zero exit codes raise CalledProcessError.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout; this RPC typically returns a plain address string.
            out = (result.stdout or "").strip()
            if not out:
                return "No address returned."

            # Try JSON first (some builds may JSON-quote the string); otherwise return raw text.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getaddressesbyaccount(self, account):
        """
        (DEPRECATED) Returns the list of addresses for a legacy account.

        Invokes the `getaddressesbyaccount` RPC to fetch all Evrmore addresses associated
        with the given **legacy account** (label). This interface is deprecated; modern
        wallets use label-based RPCs such as `getaddressesbylabel`.

        Mirrors native help:

            getaddressesbyaccount "account"

            DEPRECATED. Returns the list of addresses for the given account.

        Args:
            account (str):
                The legacy account name. Some nodes treat the empty string `""` as the
                **default account**.

        Returns:
            list[str] | str:
                - On success: a list of address strings.
                - If the node returns non-JSON text, that raw string is returned.
                - If there’s no output, returns "No addresses returned."
                - On error, returns: "Error: <node stderr or exception message>"

        Notes:
            - This API is **deprecated**; prefer `getaddressesbylabel` / `setlabel`.
            - If the account does not exist, an empty list may be returned.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> addrs = rpc.getaddressesbyaccount("tabby")
        """

        # Build the CLI command with wallet/auth/network flags + RPC + required argument.
        command = self._build_command() + [
            "getaddressesbyaccount",
            str(account),
        ]

        try:
            # Execute the command. Non-zero exit codes raise CalledProcessError.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout; expected to be a JSON array of strings.
            out = (result.stdout or "").strip()
            if not out:
                return "No addresses returned."

            # Parse JSON array; fall back to raw text if not JSON.
            try:
                parsed = json.loads(out)
                return parsed
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getbalance(self, account=None, minconf=None, include_watchonly=None):
        """
        Returns the wallet balance, optionally scoped by legacy account, min confirmations, and watch-only.

        Invokes the `getbalance` RPC.

        - If **account is omitted**, returns the wallet’s total available balance (recommended).
        - If **account is provided** (DEPRECATED), returns the balance calculated under that legacy
          account model (see caveats below).

        Mirrors native help:

            getbalance ( "account" minconf include_watchonly )

            If account is not specified, returns the server's total available balance.
            If account is specified (DEPRECATED), returns the balance in the account.
            Note that the account "" is not the same as leaving the parameter out.

        Args:
            account (str | None, optional):
                Legacy account selector (DEPRECATED). Special values:
                - `None` → omit the argument (total wallet balance mode).
                - `""`   → the **default account** under the legacy scheme.
                - `"*"`  → all wallet keys (legacy mode).
                - `"name"` → a specific legacy account.
            minconf (int | None, optional):
                Only include transactions confirmed at least this many times (default = 1).
                **Note:** if you provide `minconf` but omit `account`, this wrapper will pass
                `account="*"` to preserve positional order (matches the CLI examples).
            include_watchonly (bool | None, optional):
                Include balances from watch-only addresses (default = False).
                **Positional note:** if you provide `include_watchonly` you must also supply (or allow
                the wrapper to supply) a `minconf` value to keep arguments aligned.

        Returns:
            float | int | str:
                - On success: the numeric balance (float/int as returned by the node).
                - If the node returns non-JSON text, that raw text is returned.
                - If there’s no output, returns "No balance returned."
                - On error, returns: "Error: <node stderr or exception message>"

        Caveats (from native help):
            - The legacy **account** mode calculates balances differently and can produce confusing results
              (e.g., double-counting with conflicting pending transactions). Prefer omitting `account` entirely.

        Examples:
            Total wallet balance (≥1 conf):
                >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
                ...                 rpc_user="user", rpc_pass="pass", testnet=True)
                >>> total = rpc.getbalance()

            At least 6 confirmations (legacy mode uses "*"):
                >>> six_conf = rpc.getbalance("*", 6)

            Include watch-only (fills minconf=1 if you only set include_watchonly):
                >>> with_watch = rpc.getbalance("*", 6, True)
        """

        # Build base command.
        args = ["getbalance"]

        # Decide whether to include the legacy 'account' parameter.
        # If minconf or include_watchonly are provided but account is None, use "*" to match CLI examples.
        if account is not None or minconf is not None or include_watchonly is not None:
            acct = "*" if (account is None) else str(account)
            args.append(acct)

        # If minconf is provided (or needed because include_watchonly is set), append it.
        if minconf is not None or (include_watchonly is not None):
            # Default to 1 when include_watchonly is provided without an explicit minconf.
            args.append(str(int(minconf) if minconf is not None else 1))

        # If include_watchonly is explicitly provided, append boolean literal.
        if include_watchonly is not None:
            args.append("true" if include_watchonly else "false")

        command = self._build_command() + args

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No balance returned."

            # Try to parse as JSON; numeric values like 0.1234 will parse fine.
            try:
                parsed = json.loads(out)
                # Return the numeric (or string) as-is; callers can cast/format as they wish.
                return parsed
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getmasterkeyinfo(self):
        """
        Returns the wallet’s master BIP32 keys and account-derivation information.

        Invokes the `getmasterkeyinfo` RPC and fetches:
          - the **extended master private key** (xprv),
          - the **extended master public key** (xpub),
          - the **account derivation path**,
          - the **extended account private/public keys**.

        Mirrors native help:

            getmasterkeyinfo

        Result (JSON object):
            {
              "bip32_root_private":           (string) extended master private key,
              "bip32_root_public":            (string) extended master public key,
              "account_derivation_path":      (string) derivation path to the account keys,
              "account_extended_private_key": (string) extended account private key,
              "account_extended_public_key":  (string) extended account public key
            }

        Returns:
            dict | str:
                - On success: a dictionary with the fields shown above.
                - If the node returns non-JSON text, that raw string is returned.
                - If there’s no output, returns "No data returned."
                - On error, returns: "Error: <node stderr or exception message>"

        Security Notes:
            - **Extremely sensitive.** The extended *private* keys (xprv) can derive all child keys.
              Do **not** log, print, or transmit them. Handle outputs offline and erase securely.
            - Wallet may need to be **unlocked** to access private components.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> info = rpc.getmasterkeyinfo()
        """

        # Build the CLI command with wallet/auth/network flags + RPC name (no params).
        command = self._build_command() + ["getmasterkeyinfo"]

        try:
            # Execute the command and capture stdout/stderr; raise on non-zero exit.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout for parsing.
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Expected: JSON object with extended keys/paths.
            try:
                parsed = json.loads(out)
                return parsed
            except json.JSONDecodeError:
                # If not valid JSON, return raw text so caller can inspect.
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getmywords(self, account=None):
        """
        Returns the wallet’s BIP39 seed words (12-word mnemonic) and optional passphrase, if available.

        Invokes the `getmywords` RPC. It only returns data if the wallet was **created from**
        a 12-word BIP39 mnemonic (import/generation path). If the wallet was created another way,
        this will typically return nothing or an error.

        Mirrors native help:

            getmywords ( "account" )

            Returns the 12 words and passphrase used by BIP39 to generate the wallet's private keys.
            Only returns a value if the wallet was created by the 12 words import/generation.

        Args:
            account (str | None, optional):
                Legacy account selector (if supported by your build). Most setups can omit this.
                - `None` → omit the parameter.
                - `""`   → explicitly target the default account (legacy).
                - `"name"` → a specific legacy account label.

        Returns:
            dict | str:
                - On success (typical): a dictionary that may contain:
                    {
                      "word_list:":   "<space-separated 12 words>",
                      "passphrase:":  "<passphrase-if-one-was-used>"   # optional key
                    }
                - If the node returns non-JSON text, that raw string is returned.
                - If there’s no output, returns "No data returned."
                - On error, returns: "Error: <node stderr or exception message>"

        Security Notes:
            - **Extremely sensitive**: Anyone with the 12 words (+ optional passphrase) can control all funds.
            - Do **not** log, print, or transmit this data. Handle on a trusted/offline system.
            - Prefer immediately securing/erasing any buffers or files that contain these values.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> words = rpc.getmywords()
        """

        # Build the CLI command with wallet/auth/network flags + RPC name.
        command = self._build_command() + ["getmywords"]

        # Append legacy "account" only if explicitly provided.
        if account is not None:
            command.append(str(account))

        try:
            # Execute the RPC; raise on non-zero exit status.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Try JSON first; some builds may return a JSON object with the documented keys.
            try:
                parsed = json.loads(out)
                return parsed
            except json.JSONDecodeError:
                # If not JSON, return raw output (could be plaintext or otherwise formatted).
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getnewaddress(self, account=None):
        """
        Returns a new Evrmore address for receiving payments.

        Invokes the `getnewaddress` RPC. If a legacy **account** is specified (DEPRECATED),
        the new address is added to that account in the address book so payments received
        to it are credited to that account.

        Mirrors native help:

            getnewaddress ( "account" )

            Returns a new Evrmore address for receiving payments.
            If 'account' is specified (DEPRECATED), it is added to the address book so payments
            received with the address will be credited to 'account'.

        Args:
            account (str | None, optional):
                DEPRECATED legacy account/label to associate with the new address.
                - `None` → omit the parameter (node uses the default account logic).
                - `""`   → explicitly target the default account.
                - `"name"` → use/create that legacy account label.

        Returns:
            str:
                - On success: the newly generated Evrmore address (string).
                - If the node returns non-JSON text (typical), the raw string is returned.
                - If there’s no output, returns "No address returned."
                - On error, returns: "Error: <node stderr or exception message>"

        Notes:
            - The account parameter is **deprecated**; modern label APIs are preferred.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> addr = rpc.getnewaddress()

            # With a legacy account label:
            >>> addr2 = rpc.getnewaddress("payments")
        """

        # Build the CLI command with wallet/auth/network flags + RPC name.
        command = self._build_command() + ["getnewaddress"]

        # Append the (deprecated) account parameter only if provided.
        # None  -> omit entirely; "" or "name" -> send as given.
        if account is not None:
            command.append(str(account))

        try:
            # Execute the command; raise on non-zero exit code so we can surface stderr cleanly.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Most builds return a plain address string.
            out = (result.stdout or "").strip()
            if not out:
                return "No address returned."

            # If some build JSON-quotes the string, handle that too.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getrawchangeaddress(self):
        """
        Returns a new internal/change address (for raw transactions).

        Invokes the `getrawchangeaddress` RPC. This generates a new **change** address intended
        for use as the change output when constructing **raw transactions**. It’s not meant for
        general receiving; use `getnewaddress` for normal receive addresses.

        Mirrors native help:

            getrawchangeaddress

            Returns a new Evrmore address, for receiving change.
            This is for use with raw transactions, NOT normal use.

        Returns:
            str:
                - On success: the newly generated **change** address (string).
                - If the node returns non-JSON text (typical), the raw string is returned.
                - If there’s no output, returns "No address returned."
                - On error, returns: "Error: <node stderr or exception message>"

        Notes:
            - This address is marked internally as a **change** address by the wallet.
            - Use when assembling inputs/outputs with raw transaction APIs.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> chg = rpc.getrawchangeaddress()
        """

        # Build the CLI command with wallet/auth/network flags + RPC name (no params).
        command = self._build_command() + ["getrawchangeaddress"]

        try:
            # Execute the command; raise on non-zero exit for clean error surfacing.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Most builds return a plain address string.
            out = (result.stdout or "").strip()
            if not out:
                return "No address returned."

            # If some build JSON-quotes the string, handle that too.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getreceivedbyaccount(self, account, minconf=None):
        """
        (DEPRECATED) Returns the total amount received by addresses under a legacy account.

        Invokes the `getreceivedbyaccount` RPC. It sums the EVR received by all addresses
        associated with the given **legacy account** (label), counting only transactions with
        at least `minconf` confirmations.

        Mirrors native help:

            getreceivedbyaccount "account" ( minconf )

            DEPRECATED. Returns the total amount received by addresses with <account> in
            transactions with at least [minconf] confirmations.

        Args:
            account (str):
                Legacy account/label to total. Use `""` for the **default account**.
            minconf (int | None, optional):
                Minimum confirmations to include (default = 1). If omitted, the node’s default is used.

        Returns:
            float | int | str:
                - On success: the numeric total received (as returned by the node).
                - If the node returns non-JSON text, that raw text is returned.
                - If there’s no output, returns "No amount returned."
                - On error, returns: "Error: <node stderr or exception message>"

        Notes:
            - This API is **deprecated**; modern setups use label-based RPCs instead.
            - Passing `0` for `minconf` includes unconfirmed transactions.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> total_default = rpc.getreceivedbyaccount("")

            >>> total_tabby_6 = rpc.getreceivedbyaccount("tabby", 6)
        """

        # Build the CLI command with wallet/auth/network flags + RPC + required argument.
        args = ["getreceivedbyaccount", str(account)]

        # Append minconf only when provided; otherwise let the node use its default (1).
        if minconf is not None:
            args.append(str(int(minconf)))

        command = self._build_command() + args

        try:
            # Execute the command; raise on non-zero exit so we can surface stderr below.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Expected output is a numeric (JSON-compatible) string like 0 or 0.1234.
            out = (result.stdout or "").strip()
            if not out:
                return "No amount returned."

            # Parse JSON first (handles plain numerics cleanly); fall back to raw on failure.
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getreceivedbyaddress(self, address, minconf=None):
        """
        Returns the total EVR received by a single address, filtered by confirmations.

        Invokes the `getreceivedbyaddress` RPC. It sums the amount received by the specified
        address in transactions with **at least** `minconf` confirmations.

        Mirrors native help:

            getreceivedbyaddress "address" ( minconf )

            Returns the total amount received by the given address in transactions with
            at least minconf confirmations.

        Args:
            address (str):
                The Evrmore address to query.
            minconf (int | None, optional):
                Only include transactions confirmed at least this many times (default = 1).
                Pass `0` to include unconfirmed transactions.

        Returns:
            float | int | str:
                - On success: the numeric total received (as returned by the node).
                - If the node returns non-JSON text, that raw text is returned.
                - If there’s no output, returns "No amount returned."
                - On error, returns: "Error: <node stderr or exception message>"

        Notes:
            - This call sums *received* amounts; it does not subtract spends from this address.
            - Use `minconf=0` to include mempool (unconfirmed) transactions.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> amt = rpc.getreceivedbyaddress("mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF")
        """

        # Build CLI args in the exact order expected by the node.
        args = ["getreceivedbyaddress", str(address)]
        if minconf is not None:
            # Append minconf only when provided; otherwise the node uses its default (1).
            args.append(str(int(minconf)))

        command = self._build_command() + args

        try:
            # Execute the command; raise on non-zero exit to surface node errors via stderr.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Expected output is a JSON-parsable numeric (e.g., 0, 0.1234).
            out = (result.stdout or "").strip()
            if not out:
                return "No amount returned."

            # Prefer JSON parsing to get a numeric type; fall back to raw text if not JSON.
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def gettransaction(self, txid, include_watchonly=None):
        """
        Returns detailed information about an **in-wallet** transaction.

        Invokes the `gettransaction` RPC to fetch wallet-scoped details for the given `txid`.
        This includes overall amounts/fee, confirmation metadata, per-address breakdowns, and
        (on Evrmore) asset-aware details. You can optionally include watch-only data.

        Mirrors native help:

            gettransaction "txid" ( include_watchonly )

        Args:
            txid (str):
                The transaction id (hex).
            include_watchonly (bool, optional):
                Whether to include watch-only addresses in balance calculations and `details[]`
                (default = False). If omitted, the parameter is not sent.

        Returns:
            dict | str:
                On success, a dictionary like:
                {
                  "amount": <number>,                 # net wallet delta for this tx (EVR)
                  "fee": <number>,                    # negative for 'send' txs; absent otherwise
                  "confirmations": <int>,
                  "blockhash": "<hex>",               # present if confirmed
                  "blockindex": <int>,
                  "blocktime": <int>,                 # epoch seconds
                  "txid": "<hex>",
                  "time": <int>,                      # epoch seconds (when created/seen)
                  "timereceived": <int>,              # epoch seconds (when wallet saw it)
                  "bip125-replaceable": "yes|no|unknown",
                  "details": [                        # per-address wallet impact
                    {
                      "account": "<name>",            # DEPRECATED legacy account
                      "address": "<address>",
                      "category": "send|receive",
                      "amount": <number>,
                      "label": "<label>",             # wallet label, if any
                      "vout": <int>,
                      "fee": <number>,                # negative; only for 'send'
                      "abandoned": <bool>             # only for 'send'
                    },
                    ...
                  ],
                  "asset_details": [                  # Evrmore-specific asset info (if any)
                    {
                      "asset_type": "new_asset|transfer_asset|reissue_asset",
                      "asset_name": "<name>",
                      "amount": <number>,
                      "address": "<address>",
                      "vout": <int>,
                      "category": "send|receive"
                    },
                    ...
                  ],
                  "hex": "<rawtxhex>"                 # raw transaction hex
                }
                If non-JSON text is returned, the raw string is returned.
                On empty output, returns "No data returned."
                On error, returns: "Error: <node stderr or exception message>"

        Notes:
            - This is **wallet-scoped**: it shows how the transaction affects your wallet.
              For a network-wide decode, use `getrawtransaction`/`decoderawtransaction`.
            - `amount` is the **net** effect on your wallet (positive for receive, negative for send).
            - `fee` is typically **negative** and only present for the 'send' category.
            - `bip125-replaceable` may be `"unknown"` for unconfirmed transactions not in the mempool.
            - `asset_details` is included when the tx touches Evrmore assets.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> tx = rpc.gettransaction("1075db55d416d3ca199f55b6084e2115b9345e16c5cf302fc80e9d5fbf5d48d")

            # Include watch-only data:
            >>> tx2 = rpc.gettransaction("1075db55d416d3ca199f55b6084e2115b9345e16c5cf302fc80e9d5fbf5d48d", True)
        """

        # Build CLI args in exact positional order.
        args = ["gettransaction", str(txid)]
        if include_watchonly is not None:
            # Boolean literals in CLI need to be "true"/"false"
            args.append("true" if include_watchonly else "false")

        # Compose the full command (base flags + RPC + args).
        command = self._build_command() + args

        try:
            # Execute the command; a non-zero exit raises CalledProcessError (we’ll surface stderr below).
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout for parsing.
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Try JSON; the expected payload is a JSON object.
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                # If the node returns plain text for some reason, pass it through verbatim.
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getunconfirmedbalance(self):
        """
        Returns the wallet’s total **unconfirmed** balance.

        Invokes the `getunconfirmedbalance` RPC.

        Mirrors native help:

            getunconfirmedbalance
            Returns the server's total unconfirmed balance

        Returns:
            float | int | str:
                - On success: the numeric unconfirmed balance (as returned by the node).
                - If the node returns non-JSON text, that raw text is returned.
                - If there’s no output, returns "No balance returned."
                - On error, returns: "Error: <node stderr or exception message>"

        Notes:
            - “Unconfirmed” generally includes funds from transactions that are in the mempool
              but not yet included in a block. It may exclude certain categories depending on
              wallet policy/build.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> ubal = rpc.getunconfirmedbalance()
        """

        # Build the CLI command with wallet/auth/network flags + RPC name (no parameters).
        command = self._build_command() + ["getunconfirmedbalance"]

        try:
            # Execute the command; raise on non-zero exit so we can return node stderr clearly.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize the output for parsing.
            out = (result.stdout or "").strip()
            if not out:
                return "No balance returned."

            # Parse JSON first (numeric strings parse cleanly); fall back to raw text if not JSON.
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getwalletinfo(self):
        """
        Returns an object containing various wallet state information.

        Invokes the `getwalletinfo` RPC and reports balances, tx counts, keypool
        metadata, unlock status, fee settings, and optional HD identifiers.

        Mirrors native help:

            getwalletinfo

        Result (JSON object):
            {
              "walletname":                 (string)  wallet name
              "walletversion":              (numeric) wallet version
              "balance":                    (numeric) confirmed balance (EVR)
              "unconfirmed_balance":        (numeric) unconfirmed balance (EVR)
              "immature_balance":           (numeric) immature balance (EVR)
              "txcount":                    (numeric) number of wallet transactions
              "keypoololdest":              (numeric) epoch seconds of oldest pre-generated key
              "keypoolsize":                (numeric) count of pre-generated **external** keys
              "keypoolsize_hd_internal":    (numeric) pre-generated **internal** (change) keys
              "unlocked_until":             (numeric) epoch seconds until wallet relocks; 0 if locked
              "paytxfee":                   (numeric) configured tx fee (EVR/kB)
              "hdseedid":                   (string, optional) Hash160 of HD seed (HD wallets)
              "hdmasterkeyid":              (string, optional) alias of hdseedid (back-compat)
            }

        Returns:
            dict | str:
                - On success: a dictionary with the fields above.
                - If the node returns non-JSON text, that raw text is returned.
                - If there’s no output, returns "No data returned."
                - On error, returns: "Error: <node stderr or exception message>"

        Notes:
            - `unlocked_until` is a UNIX timestamp (seconds). `0` means the wallet is locked.
            - `keypoolsize_hd_internal` appears when the wallet uses a separate internal (change) pool.
            - `hdseedid` / `hdmasterkeyid` are present for HD-enabled wallets.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> info = rpc.getwalletinfo()
        """

        # Build the CLI command with wallet/auth/network flags + RPC name (no params).
        command = self._build_command() + ["getwalletinfo"]

        try:
            # Execute the command and capture stdout/stderr; raise on non-zero exit.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize output.
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Expected: JSON object; return parsed dict. If not JSON, return raw string.
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def importaddress(self, address_or_script, label=None, rescan=None, p2sh=None):
        """
        Imports an address *or* raw script (hex) as watch-only into the wallet.

        Invokes the `importaddress` RPC. This adds a script (hex) or address that your wallet can
        **watch** (see incoming funds) but **cannot spend** from. Optionally assigns a label, triggers
        a wallet rescan, and can also add the **P2SH** version of the script.

        Mirrors native help:

            importaddress "address" ( "label" rescan p2sh )

            Adds a script (in hex) or address that can be watched as if it were in your wallet
            but cannot be used to spend.

            1. "script"   (string, required) The hex-encoded script (or address)
            2. "label"    (string, optional, default="") Label for bookkeeping
            3. rescan     (boolean, optional, default=true) Rescan the wallet for transactions
            4. p2sh       (boolean, optional, default=false) Also add the P2SH form of the script

        Args:
            address_or_script (str):
                An Evrmore **address** or a **hex-encoded script** to import as watch-only.
            label (str | None, optional):
                Wallet label to assign. If omitted, the node uses the empty string `""`.
            rescan (bool | None, optional):
                Whether to rescan the blockchain for historical transactions involving this
                address/script. Defaults to **True**. Note that rescans can take minutes.
            p2sh (bool | None, optional):
                If `True`, also import the **P2SH** version of the script. Defaults to **False**.

        Returns:
            str:
                - On success, nodes often print nothing; this wrapper returns
                  **"Import successful (rescan may take time)."** if no output is produced.
                - If the node returns JSON or text, it is surfaced (parsed to string if JSON).
                - On error, returns: **"Error: <node stderr or exception message>"**.

        Notes:
            - If you have the **full public key**, prefer `importpubkey`.
            - Importing a **non-standard raw script** may cause outputs to be treated as *change* and
              not appear in some RPCs.
            - To avoid a long rescan on large wallets, set `rescan=False` and manually rescan later if needed.

        Examples:
            Import an address with default rescan:
                >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",rpc_user="user", rpc_pass="pass", testnet=True)
                >>> result = rpc.importaddress("mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF")
        """

        # Build CLI args in the exact positional order the node expects.
        args = ["importaddress", str(address_or_script)]

        # If ANY optional is provided, we enter the optional zone and must fill positions in order.
        if any(x is not None for x in (label, rescan, p2sh)):
            # Position 2: label (empty string default if omitted)
            args.append("" if label is None else str(label))

            # Position 3: rescan (default True if omitted but we've entered optional args)
            if rescan is None:
                args.append("true")
            else:
                args.append("true" if rescan else "false")

            # Position 4: p2sh (only append if explicitly provided; otherwise default is False)
            if p2sh is not None:
                args.append("true" if p2sh else "false")

        command = self._build_command() + args

        try:
            # Execute the command; a non-zero exit raises CalledProcessError.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            out = (result.stdout or "").strip()
            if not out:
                # Most nodes print nothing on success.
                return "Import successful (rescan may take time)."

            # Try JSON parsing; fall back to returning raw text.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def importmulti(self, requests, options=None):
        """
        Bulk-import addresses/scripts (and optional keys/scripts) in a single pass.

        Invokes the `importmulti` RPC. You provide an array of request objects that describe
        what to import (addresses, scripts, redeem scripts, pubkeys/privkeys, labels, etc.),
        along with metadata (e.g., `timestamp`, `watchonly`, `internal`). Optionally supply an
        `options` object to control rescanning.

        Mirrors native help:

            importmulti "requests" ( "options" )

            Import addresses/scripts (with private or public keys, redeem script (P2SH)),
            rescanning all addresses in one-shot-only (rescan can be disabled via options).

        Request object fields (array of JSON objects):
            {
              "scriptPubKey": "<hex_script>" | { "address":"<address>" },  # required
              "timestamp": <int>|"now",                                    # required (epoch seconds or "now")
              "redeemscript": "<hex_script>",                              # optional, only for P2SH
              "pubkeys": ["<hex_pubkey>", ...],                            # optional
              "keys": ["<WIF_privkey>", ...],                              # optional (privkeys)
              "internal": <bool>,                                          # optional, default false (treat as change)
              "watchonly": <bool>,                                         # optional, default false (only if keys=[])
              "label": "<label>"                                           # optional, default '' (only if internal=false)
            }

        Options object (optional):
            {
              "rescan": <bool>  # default true; set false to skip the rescan
            }

        Returns:
            list[dict] | str:
                - On success: an array with one result per request, e.g.
                  [{ "success": true }, { "success": false, "error": { "code": -1, "message": "..." } }, ...]
                - If the node returns non-JSON text, that raw string is returned.
                - If there’s no output, returns "No data returned."
                - On error, returns: "Error: <node stderr or exception message>"

        Notes:
            - **Rescan time**: With many imports and `rescan=true` (default), this call can take minutes.
              You can pass options `{"rescan": false}` and run a rescan later if needed.
            - **Timestamp** drives how far back the rescan goes. Use:
                * an epoch seconds integer, or
                * `"now"` to bypass scanning for history.
              Using `0` scans the entire chain (slow).
            - `watchonly=true` is only allowed when no private keys are provided (`"keys": [] or omitted`).
            - `internal=true` treats matches as non-incoming (change-only).
            - `redeemscript` is only valid for P2SH contexts.
            - This RPC does not broadcast anything; it only updates your wallet’s knowledge.

        Example:
            # Import two addresses with different timestamps; skip rescan for speed:
            >>> reqs = [
            ...   { "scriptPubKey": { "address": "n2abc...Addr1" }, "timestamp": "now", "label": "watch-1", "watchonly": True },
            ...   { "scriptPubKey": { "address": "n3def...Addr2" }, "timestamp": 1693350000, "label": "watch-2", "watchonly": True }
            ... ]
            >>> opts = { "rescan": False }
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> result = rpc.importmulti(reqs, opts)

            # Import a P2SH address with its redeem script and public keys; full rescan:
            >>> reqs = [
            ...   {
            ...     "scriptPubKey": { "address": "2Nxxx...P2SH" },
            ...     "redeemscript": "5121...ae",   # hex
            ...     "pubkeys": ["02aa...","03bb..."],
            ...     "timestamp": 0,
            ...     "label": "multisig-watch",
            ...     "watchonly": True
            ...   }
            ... ]
            >>> result = rpc.importmulti(reqs)  # default options -> rescan=true
        """

        # ---- Serialize "requests" to the single JSON string the CLI expects ---------------------
        # Accept Python list/tuple OR pre-serialized JSON string.
        if isinstance(requests, (list, tuple)):
            try:
                requests_json = json.dumps(requests)
            except (TypeError, ValueError) as ser_err:
                return f"Error: Failed to serialize 'requests' to JSON: {ser_err}"
        else:
            # Assume the caller passed a JSON string; still coerce to str to be safe.
            requests_json = str(requests)

        # ---- Serialize "options" (optional) to JSON string -------------------------------------
        options_json = None
        if options is not None:
            if isinstance(options, dict):
                try:
                    options_json = json.dumps(options)
                except (TypeError, ValueError) as ser_err:
                    return f"Error: Failed to serialize 'options' to JSON: {ser_err}"
            else:
                # Assume pre-serialized JSON string for options
                options_json = str(options)

        # Build CLI args exactly as the node expects:
        #   importmulti "<requests_json>" ["<options_json>"]
        args = ["importmulti", requests_json]
        if options_json is not None:
            args.append(options_json)

        command = self._build_command() + args

        try:
            # Execute the RPC; long-running if a rescan occurs. Non-zero exit raises CalledProcessError.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            out = (result.stdout or "").strip()
            if not out:
                # Some builds may print nothing (rare). Surface a helpful message.
                return "No data returned."

            # Expected: JSON array of per-request results.
            try:
                parsed = json.loads(out)
                return parsed
            except json.JSONDecodeError:
                # If the node returns non-JSON (unexpected), surface raw text for debugging.
                return out

        except Exception as e:
            # Standardized error format you requested (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def importprivkey(self, privkey, label=None, rescan=None):
        """
        Imports a private key (WIF) into the wallet.

        Invokes the `importprivkey` RPC. This adds a private key (as returned by
        `dumpprivkey`) to your wallet. Optionally assigns a label and controls whether
        to rescan the blockchain for historical transactions involving the key.

        Mirrors native help:

            importprivkey "privkey" ( "label" ) ( rescan )

            Adds a private key (as returned by dumpprivkey) to your wallet.

            1. "privkey"  (string, required) The private key (WIF)
            2. "label"    (string, optional, default="") An optional label
            3. rescan     (boolean, optional, default=true) Rescan the wallet for transactions

        Args:
            privkey (str):
                The private key in **WIF** format (from `dumpprivkey`).
            label (str | None, optional):
                Wallet label to assign. If omitted, the node uses the empty string `""`.
            rescan (bool | None, optional):
                Whether to rescan the blockchain for historical transactions. Defaults to **True**.
                Note that rescans can take **minutes** on large wallets.

        Returns:
            str:
                - On success, nodes typically print nothing; this wrapper returns
                  **"Import successful (rescan may take time)."** if no output is produced.
                - If the node returns JSON/text, it is surfaced (parsed to string if JSON).
                - On error, returns: **"Error: <node stderr or exception message>"**.

        Security Notes:
            - Handle private keys with extreme care. Anyone with the key can spend the funds.
            - Avoid logging or printing the key. Consider moving funds to a fresh address after import.
            - If the wallet is encrypted, unlock it before calling this RPC.

        Examples:
            # Import with default rescan (slow on large wallets):
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> result = rpc.importprivkey("L1aW4aubDFB7yfras2S1mN3bqg9w7")

        """

        # Build CLI args in exact positional order: privkey, (label), (rescan)
        args = ["importprivkey", str(privkey)]

        # If any optional provided, we must start filling positions in order.
        if (label is not None) or (rescan is not None):
            # Position 2: label (empty string default if omitted)
            args.append("" if label is None else str(label))

            # Position 3: rescan (only append if explicitly provided; otherwise node default is True)
            if rescan is not None:
                args.append("true" if rescan else "false")

        command = self._build_command() + args

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "Import successful (rescan may take time)."

            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def importprunedfunds(self, rawtransaction, txoutproof):
        """
        Imports funds **without** a rescan (for pruned wallets).

        Invokes the `importprunedfunds` RPC. This lets a pruned wallet credit specific UTXOs
        by providing:
          - the funding transaction **hex** (`rawtransaction`), and
          - a corresponding **txoutproof** (Merkle proof) obtained via `gettxoutproof`.

        The **corresponding address or script must already be in the wallet** (e.g., added via
        `importaddress`, `importpubkey`, `importmulti`, or it was generated by the wallet).

        Mirrors native help:

            importprunedfunds

            Imports funds without rescan. Corresponding address or script must previously be
            included in wallet. Aimed towards pruned wallets. The end-user is responsible to
            import additional transactions that subsequently spend the imported outputs or rescan
            after the point in the blockchain the transaction is included.

        Args:
            rawtransaction (str):
                The funding transaction in **hex** (as returned by `getrawtransaction` or other source).
            txoutproof (str):
                The **hex** output from `gettxoutproof` that proves inclusion of the transaction.

        Returns:
            str | dict:
                - Most nodes print nothing on success; this wrapper returns
                  **"Import successful (no rescan performed)."** if stdout is empty.
                - If the node returns JSON or text, it is surfaced (parsed to dict/string).
                - On error, returns: **"Error: <node stderr or exception message>"**.

        Notes:
            - Designed for **pruned** wallets; there is **no rescan**.
            - You are responsible for importing any **subsequent spending transactions** that
              spend these outputs, or performing a rescan **starting before** the tx’s block.
            - Ensure the destination address/script is already known to the wallet.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> out = rpc.importprunedfunds("tx_hex", "proof_hex")
        """

        # Build the CLI command with wallet/auth/network flags + RPC + required args.
        command = self._build_command() + [
            "importprunedfunds",
            str(rawtransaction),
            str(txoutproof),
        ]

        try:
            # Execute the command; non-zero exit raises CalledProcessError (we’ll surface stderr below).
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            out = (result.stdout or "").strip()
            if not out:
                # Typical success path: node prints nothing.
                return "Import successful (no rescan performed)."

            # Try JSON first; fall back to raw string if not JSON.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, (dict, list, str)) else str(parsed)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def importpubkey(self, pubkey, label=None, rescan=None):
        """
        Imports a public key (hex) as **watch-only** into the wallet.

        Invokes the `importpubkey` RPC. This adds a **hex-encoded public key** that the wallet
        can watch for incoming funds, but **cannot spend** from (no private key). Optionally
        assigns a label and controls whether to **rescan** for historical transactions.

        Mirrors native help:

            importpubkey "pubkey" ( "label" rescan )

            Adds a public key (in hex) that can be watched as if it were in your wallet
            but cannot be used to spend.

            1. "pubkey"  (string, required) The hex-encoded public key
            2. "label"   (string, optional, default="") An optional label
            3. rescan    (boolean, optional, default=true) Rescan the wallet for transactions

        Args:
            pubkey (str):
                The **hex-encoded** public key (compressed/uncompressed) to watch.
            label (str | None, optional):
                Wallet label to assign. If omitted, the node uses the empty string `""`.
            rescan (bool | None, optional):
                Whether to rescan the blockchain for historical activity. Defaults to **True**.
                Note: rescans can take **minutes** on larger wallets.

        Returns:
            str:
                - On success, nodes often print nothing; this wrapper returns
                  **"Import successful (rescan may take time)."** if no output is produced.
                - If the node returns JSON/text, it is surfaced (parsed to string if JSON).
                - On error, returns: **"Error: <node stderr or exception message>"**.

        Notes:
            - This is **watch-only**: spending requires the corresponding private key.
            - If you have a private key (WIF), use `importprivkey` instead.
            - Consider setting `rescan=False` for many imports, then rescan once later.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> result = rpc.importpubkey("02a1633cafhex pubkey>")
        """

        # Build CLI args in the exact positional order expected by the node.
        args = ["importpubkey", str(pubkey)]

        # If any optional parameter is provided, we must start filling positions in order.
        if (label is not None) or (rescan is not None):
            # Position 2: label (empty string default if omitted)
            args.append("" if label is None else str(label))

            # Position 3: rescan (only append if explicitly provided; otherwise node default is True)
            if rescan is not None:
                args.append("true" if rescan else "false")

        command = self._build_command() + args

        try:
            # Execute the command; non-zero exit raises CalledProcessError (we surface stderr below).
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            out = (result.stdout or "").strip()
            if not out:
                return "Import successful (rescan may take time)."

            # Try JSON parsing (some builds may JSON-quote strings); fall back to raw text.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error format you requested (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def importwallet(self, filename):
        """
        Imports keys from a wallet **dump file** (see `dumpwallet`).

        Invokes the `importwallet` RPC to read a dump file created by `dumpwallet` and
        import all contained keys (and metadata) into the current wallet.

        Mirrors native help:

            importwallet "filename"

            Imports keys from a wallet dump file (see dumpwallet).

        Args:
            filename (str):
                Path to the wallet dump file on the **server/daemon host** (absolute path
                or relative to the `evrmored` working directory). If the path contains
                spaces, it’s fine—this wrapper does not invoke a shell.

        Returns:
            str | dict:
                - Most nodes print nothing on success; this wrapper returns
                  **"Import successful (rescan may take time)."** if stdout is empty.
                - If the node returns JSON/text, it is surfaced (parsed if JSON).
                - On error, returns: **"Error: <node stderr or exception message>"**.

        Notes:
            - This operation typically triggers a **rescan** to discover historical
              transactions for the imported keys and can take **minutes** or longer.
            - Ensure the wallet is **unlocked** if required by your setup.
            - Consider importing on a trusted machine; dump files contain **private keys**.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> out = rpc.importwallet("/tmp/evr_wallet_dump.txt")
        """

        # Build CLI command with wallet/auth/network flags + RPC + required filename.
        command = self._build_command() + [
            "importwallet",
            str(filename),
        ]

        try:
            # Execute the command; non-zero exit raises CalledProcessError (we surface stderr below).
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Many builds return no stdout on success.
            out = (result.stdout or "").strip()
            if not out:
                return "Import successful (rescan may take time)."

            # Try to parse JSON, otherwise return raw text.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, (dict, list, str)) else str(parsed)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def keypoolrefill(self, newsize=None):
        """
        Refills (tops up) the wallet’s keypool.

        Invokes the `keypoolrefill` RPC to pre-generate additional keys used for
        new receive addresses (and, for HD wallets, internal/change keys as well).

        Mirrors native help:

            keypoolrefill ( newsize )

            Fills the keypool.
            1. newsize (numeric, optional, default=100) The new keypool size

        Args:
            newsize (int | None, optional):
                Target size for the **external** keypool. If omitted, the node uses its
                default (typically 100). For HD wallets that support separate internal
                pools, the node will handle those according to its own policy.

        Returns:
            str:
                - On success, nodes usually print nothing; this wrapper returns
                  **"Keypool refill requested."** if stdout is empty.
                - If the node returns JSON/text, it is surfaced (parsed to string if JSON).
                - On error, returns: **"Error: <node stderr or exception message>"**.

        Notes:
            - You can check current pool sizes via `getwalletinfo` (see `keypoolsize`
              and `keypoolsize_hd_internal` when available).
            - Some builds/configs may require the wallet to be unlocked to derive keys.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> result = rpc.keypoolrefill(200)

        """

        # Build CLI command with wallet/auth/network flags + RPC name.
        args = ["keypoolrefill"]

        # Append the optional size only if provided; let the node use its default otherwise.
        if newsize is not None:
            args.append(str(int(newsize)))

        command = self._build_command() + args

        try:
            # Execute the command; raise on non-zero exit to surface stderr cleanly.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            out = (result.stdout or "").strip()
            if not out:
                return "Keypool refill requested."

            # Try JSON first; fall back to raw text if not JSON.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error format you requested (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def listaccounts(self, minconf=None, include_watchonly=None):
        """
        (DEPRECATED) Returns a mapping of legacy account names to their balances.

        Invokes the `listaccounts` RPC. This legacy API aggregates balances by **account**
        (old label system). Modern wallets favor label-based RPCs instead.

        Mirrors native help:

            listaccounts ( minconf include_watchonly )

            DEPRECATED. Returns object that has account names as keys, balances as values.
            1. minconf           (numeric, optional, default=1)
            2. include_watchonly (bool, optional, default=false)

        Args:
            minconf (int | None, optional):
                Only include transactions with at least this many confirmations.
                If omitted and `include_watchonly` is provided, this wrapper supplies the
                node default of **1** to keep positional arguments aligned.
            include_watchonly (bool | None, optional):
                Include balances from watch-only addresses (default = False).

        Returns:
            dict | str:
                - On success: a dict like { "": 1.2345, "acct1": 0.5, ... } where `""` is the default account.
                - If the node returns non-JSON text, that raw string is returned.
                - If there’s no output, returns "No data returned."
                - On error, returns: "Error: <node stderr or exception message>"

        Notes:
            - This interface is **deprecated**; prefer modern label APIs (`getbalances`, `getaddressesbylabel`, etc.).
            - Balances can be confusing with conflicting unconfirmed transactions; see node help for caveats.

        Examples:
            # At least 1 confirmation (default):
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> accts = rpc.listaccounts()
            >>> accts0 = rpc.listaccounts(0)
            >>> accts_wo = rpc.listaccounts(1, True)
        """

        # Build CLI args in the exact positional order the node expects.
        args = ["listaccounts"]

        # If any optional is provided, we must begin filling positions in order.
        if (minconf is not None) or (include_watchonly is not None):
            # Position 1: minconf (use 1 if only include_watchonly was provided)
            args.append(str(int(minconf) if minconf is not None else 1))

            # Position 2: include_watchonly (only if explicitly provided)
            if include_watchonly is not None:
                args.append("true" if include_watchonly else "false")

        command = self._build_command() + args

        try:
            # Execute the RPC; raise on non-zero exit to surface node stderr.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Expected: JSON object { account: balance, ... }
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                # If not JSON for some reason, return raw text so the caller can inspect.
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def listaddressgroupings(self):
        """
        Lists groups of addresses that appear to share common ownership.

        Invokes the `listaddressgroupings` RPC. The wallet heuristically groups addresses
        that have revealed common ownership by being used together as inputs or as change
        in past transactions.

        Mirrors native help:

            listaddressgroupings

            Lists groups of addresses which have had their common ownership made public by
            common use as inputs or as the resulting change in past transactions.

        Returns:
            list[list[list]] | str:
                - On success: a nested list structure like:
                  [
                    [
                      ["address", amount, "account?" ],   # group 1, entry 1
                      ["address", amount, "account?" ],   # group 1, entry 2
                      ...
                    ],
                    [
                      ["address", amount, "account?" ],   # group 2, entry 1
                      ...
                    ],
                    ...
                  ]
                  where each **entry** is `[address: str, amount: number, account: str?]`
                  and the legacy `account` (if present) is **DEPRECATED**.
                - If the node returns non-JSON text, that raw string is returned.
                - If there’s no output, returns "No data returned."
                - On error, returns: "Error: <node stderr or exception message>"

        Privacy Notes:
            - These groupings are derived from **on-chain heuristics** (e.g., co-spend, change).
            - They may reveal wallet structure; handle outputs carefully if sharing logs.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> groups = rpc.listaddressgroupings()
        """

        # Build CLI command with wallet/auth/network flags + RPC name (no params).
        command = self._build_command() + ["listaddressgroupings"]

        try:
            # Execute the command; raise on non-zero exit so we can surface node stderr cleanly.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout for parsing.
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Expected: JSON array of arrays of address entries.
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                # If not valid JSON (unlikely), return raw text so caller can inspect.
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def listlockunspent(self):
        """
        Lists wallet outputs that are currently **locked** (temporarily unspendable).

        Invokes the `listlockunspent` RPC. These UTXOs have been locked via `lockunspent`
        (e.g., to prevent the coin selection algorithm from using them). Use `lockunspent`
        again to unlock them.

        Mirrors native help:

            listlockunspent

            Returns list of temporarily unspendable outputs.
            See the lockunspent call to lock and unlock transactions for spending.

        Returns:
            list[dict] | str:
                - On success: a list of objects like:
                  [
                    { "txid": "<transactionid>", "vout": <n> },
                    ...
                  ]
                - If the node returns non-JSON text, that raw string is returned.
                - If there’s no output, returns **"No data returned."**
                - On error, returns: **"Error: <node stderr or exception message>"**.

        Notes:
            - Locked UTXOs are excluded from spending until explicitly unlocked.
            - To lock or unlock, use:
                * `lockunspent(False, [{"txid": "...","vout": n}])`  → lock
                * `lockunspent(True,  [{"txid": "...","vout": n}])`  → unlock

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> locked = rpc.listlockunspent()
        """

        # Build the CLI command with wallet/auth/network flags + RPC name (no params).
        command = self._build_command() + ["listlockunspent"]

        try:
            # Execute the command; non-zero exit raises CalledProcessError (stderr captured below).
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout for parsing.
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Expected: JSON array of { "txid": "...", "vout": n } objects.
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                # If not JSON for some reason, return raw text so the caller can inspect.
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def listreceivedbyaccount(self, minconf=None, include_empty=None, include_watchonly=None):
        """
        (DEPRECATED) Lists received balances grouped by legacy account.

        Invokes the `listreceivedbyaccount` RPC. For each **legacy account** (old label system),
        returns its total received amount, most recent confirmation depth, and optional flags.

        Mirrors native help:

            listreceivedbyaccount ( minconf include_empty include_watchonly )

            DEPRECATED. List balances by account.

        Args:
            minconf (int | None, optional):
                Minimum confirmations required for payments to be counted (default = 1).
            include_empty (bool | None, optional):
                Include accounts that have **not** received any payments (default = False).
            include_watchonly (bool | None, optional):
                Include results for watch-only addresses (default = False).

        Returns:
            list[dict] | str:
                - On success: a list like:
                  [
                    {
                      "involvesWatchonly": <bool>,  # only when watch-only txs were involved
                      "account": "<name>",          # legacy account name (DEPRECATED)
                      "amount": <number>,           # total received by this account
                      "confirmations": <int>,       # confs of the most recent included tx
                      "label": "<label>"            # comment/label, if any
                    },
                    ...
                  ]
                - If the node returns non-JSON text, that raw string is returned.
                - If there’s no output, returns "No data returned."
                - On error, returns: "Error: <node stderr or exception message>"

        Notes:
            - This API is **deprecated**; modern setups use label-based RPCs instead.
            - Positional rules:
                * If you provide `include_watchonly` but omit prior args, this wrapper fills
                  the earlier positions with their defaults to keep argument order correct.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> rows = rpc.listreceivedbyaccount(6, True, True)
        """

        # Build CLI args in the exact positional order the node expects.
        args = ["listreceivedbyaccount"]

        # If any optional is specified, we must start filling positions in order.
        if (minconf is not None) or (include_empty is not None) or (include_watchonly is not None):
            # Position 1: minconf
            args.append(str(int(minconf) if minconf is not None else 1))

            # Position 2: include_empty (only append if provided OR if include_watchonly is provided,
            # in which case fill its default to preserve positional order).
            if include_empty is not None or include_watchonly is not None:
                args.append("true" if include_empty else "false")

            # Position 3: include_watchonly (only append if explicitly provided)
            if include_watchonly is not None:
                args.append("true" if include_watchonly else "false")

        command = self._build_command() + args

        try:
            # Execute the command; raise on non-zero exit so stderr is captured for the error message.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Expected: JSON array of account summaries.
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                # If not JSON for some reason, return raw text so the caller can inspect.
                return out

        except Exception as e:
            # Standardized error format you requested (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def listreceivedbyaddress(self, minconf=None, include_empty=None, include_watchonly=None):
        """
        Lists balances grouped by **receiving address**.

        Invokes the `listreceivedbyaddress` RPC. For each receiving address known to the
        wallet, returns its total received amount, most recent confirmation depth, and
        related metadata. You can control the minimum confirmations, whether to include
        empty addresses, and whether to include watch-only addresses.

        Mirrors native help:

            listreceivedbyaddress ( minconf include_empty include_watchonly )

            List balances by receiving address.

        Args:
            minconf (int | None, optional):
                Minimum confirmations required before payments are counted (default = 1).
            include_empty (bool | None, optional):
                Whether to include addresses that have not received any payments (default = False).
            include_watchonly (bool | None, optional):
                Whether to include watch-only addresses (default = False).

        Returns:
            list[dict] | str:
                - On success: a list like:
                  [
                    {
                      "involvesWatchonly": <bool>,   # only when watch-only txs were involved
                      "address": "<receivingaddress>",
                      "account": "<accountname>",    # DEPRECATED legacy account (may be "")
                      "amount": <number>,            # total EVR received by this address
                      "confirmations": <int>,        # confs of the most recent included tx
                      "label": "<label>",            # address/tx comment, if any
                      "txids": ["<txid>", ...]       # transaction ids that paid this address
                    },
                    ...
                  ]
                - If the node returns non-JSON text, that raw string is returned.
                - If there’s no output, returns "No data returned."
                - On error, returns: "Error: <node stderr or exception message>"

        Notes:
            - This reports **received** amounts only; it does not subtract any spends from the address.
            - Use `minconf=0` to include unconfirmed (mempool) transactions.
            - The `account` field is part of the legacy account system and is **deprecated**.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> rows = rpc.listreceivedbyaddress(6, True, True)
        """

        # Build CLI args in the exact positional order the node expects.
        args = ["listreceivedbyaddress"]

        # If any optional is specified, begin filling positions in order.
        if (minconf is not None) or (include_empty is not None) or (include_watchonly is not None):
            # Position 1: minconf (use default 1 if later args require us to fill this slot)
            args.append(str(int(minconf) if minconf is not None else 1))

            # Position 2: include_empty — append if explicitly provided OR if include_watchonly
            # is provided (to keep positions aligned). Default is "false".
            if include_empty is not None or include_watchonly is not None:
                args.append("true" if include_empty else "false")

            # Position 3: include_watchonly — only append if explicitly provided.
            if include_watchonly is not None:
                args.append("true" if include_watchonly else "false")

        # Compose the full command with base flags + RPC name + args.
        command = self._build_command() + args

        try:
            # Execute the command; non-zero exit raises CalledProcessError (stderr captured).
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout for parsing.
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Expected: JSON array of per-address summaries.
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                # If the node returns plain text for some reason, pass it through.
                return out

        except Exception as e:
            # Standardized error format (surface node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def listsinceblock(self, blockhash=None, target_confirmations=None, include_watchonly=None, include_removed=None):
        """
        Lists wallet transactions since a given block (or since the beginning if omitted).

        Invokes the `listsinceblock` RPC. Returns all wallet-affecting transactions found in
        blocks **after** `blockhash`. If `blockhash` is omitted, returns **all** transactions.
        If the referenced block is not on the active chain (reorg), results start from the fork point.
        When `include_removed=True`, transactions removed by a reorg are returned in the `"removed"` array.

        Mirrors native help:

            listsinceblock ( "blockhash" target_confirmations include_watchonly include_removed )

        Args:
            blockhash (str | None, optional):
                A block hash to list transactions **since**. Omit to list all. If you want to
                specify later parameters but not this one, this wrapper sends an empty string "".
            target_confirmations (int | None, optional):
                Default = 1. Not a filter: only affects the `"lastblock"` value in the result,
                which is the tip minus (target_confirmations - 1). Useful to feed back into the
                next call so you keep getting transactions until they reach N confs.
            include_watchonly (bool | None, optional):
                Include transactions that involve watch-only addresses (default = False).
            include_removed (bool | None, optional):
                Include transactions that were **removed** due to a reorg in the `"removed"` array
                (default = True per node help; pruned nodes may not support this).

        Returns:
            dict | str:
                On success, a dictionary like:
                {
                  "transactions": [
                    {
                      "account": "<name>",           # DEPRECATED legacy account, may be ""
                      "address": "<address>",        # not present for category=move
                      "category": "send|receive",
                      "amount": <number>,            # negative for 'send'
                      "vout": <int>,
                      "fee": <number>,               # negative; only for 'send'
                      "confirmations": <int>,        # < 0 means conflicted that many blocks ago
                      "blockhash": "<hex>",
                      "blockindex": <int>,
                      "blocktime": <int>,            # epoch seconds
                      "txid": "<hex>",
                      "time": <int>,                 # epoch seconds
                      "timereceived": <int>,         # epoch seconds
                      "bip125-replaceable": "yes|no|unknown",
                      "abandoned": <bool>,           # only for 'send'
                      "comment": "<str>",
                      "label": "<str>",
                      "to": "<str>"
                    },
                    ...
                  ],
                  "removed": [ ... ],                # same structure as "transactions" (if requested)
                  "lastblock": "<blockhash>"
                }
                If non-JSON text is returned, the raw string is returned.
                If there’s no output, returns "No data returned."
                On error, returns: "Error: <node stderr or exception message>"

        Notes:
            - `target_confirmations` drives `"lastblock"` for incremental polling:
                * Call 1 with N=6 → use `"lastblock"` from result as the next `blockhash`.
                * Repeat until a tx reaches 6 confs; new txs keep appearing.
            - `include_removed=True` helps detect reorg-removed transactions (may not work on pruned nodes).
            - This is **wallet-scoped**: shows txs involving your wallet’s keys/addresses.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> res_all = rpc.listsinceblock()
            >>> res = rpc.listsinceblock("", 6, True, True)
        """

        # Build args in exact positional order expected by the node.
        args = ["listsinceblock"]

        # Determine if we need to enter the "optional zone" (i.e., append placeholders/defaults).
        any_optional = any(x is not None for x in (blockhash, target_confirmations, include_watchonly, include_removed))
        if any_optional:
            # Position 1: "blockhash" — empty string if not provided but later args are.
            args.append("" if blockhash is None else str(blockhash))

            # Position 2: target_confirmations — supply default 1 if later args require alignment.
            if (target_confirmations is not None) or (include_watchonly is not None) or (include_removed is not None):
                args.append(str(int(target_confirmations) if target_confirmations is not None else 1))

            # Position 3: include_watchonly — append only if explicitly provided or if include_removed is provided
            # (to preserve positional order). Default is "false".
            if (include_watchonly is not None) or (include_removed is not None):
                args.append("true" if include_watchonly else "false")

            # Position 4: include_removed — only if explicitly provided.
            if include_removed is not None:
                args.append("true" if include_removed else "false")

        command = self._build_command() + args

        try:
            # Execute RPC; non-zero exit raises CalledProcessError (stderr captured).
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Expected: JSON object with "transactions", optional "removed", and "lastblock".
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out  # surface raw output if not valid JSON

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def listtransactions(self, account=None, count=None, skip=None, include_watchonly=None):
        """
        Returns recent wallet transactions, with paging and optional watch-only inclusion.

        Invokes the `listtransactions` RPC. It returns up to `count` most recent transactions,
        skipping the first `skip` entries, for the (legacy) `account`. The legacy account arg
        is **DEPRECATED**; the help text suggests using `"*"`.

        Mirrors native help:

            listtransactions ( "account" count skip include_watchonly )

        Args:
            account (str | None, optional):
                DEPRECATED legacy account name. The help suggests `"*"`. If you provide
                later parameters (e.g., `count`) but leave `account=None`, this wrapper
                will pass `"*"` to preserve positional order.
            count (int | None, optional):
                Number of transactions to return (default = 10).
            skip (int | None, optional):
                Number of transactions to skip from the head (default = 0).
            include_watchonly (bool | None, optional):
                Include transactions that involve watch-only addresses (default = False).

        Returns:
            list[dict] | str:
                On success: a list of transaction objects, each like:
                {
                  "account": "<name>",                 # DEPRECATED; "" for default
                  "address": "<address>",              # not present for category="move"
                  "category": "send|receive|move",
                  "amount": <number>,                  # negative for 'send'
                  "label": "<label>",
                  "vout": <int>,
                  "fee": <number>,                     # negative; only for 'send'
                  "confirmations": <int>,              # negative means conflicted that many blocks
                  "trusted": <bool>,
                  "blockhash": "<hex>",
                  "blockindex": <int>,
                  "blocktime": <int>,                  # epoch seconds
                  "txid": "<hex>",
                  "time": <int>,                       # epoch seconds
                  "timereceived": <int>,               # epoch seconds
                  "comment": "<str>",
                  "otheraccount": "<name>",            # DEPRECATED; for category="move"
                  "bip125-replaceable": "yes|no|unknown",
                  "abandoned": <bool>                  # only for 'send'
                }
                If non-JSON text is returned, the raw string is returned.
                If there’s no output, returns "No data returned."
                On error, returns: "Error: <node stderr or exception message>"

        Notes:
            - This is **wallet-scoped** and shows how transactions affect your wallet.
            - `category="move"` entries are local bookkeeping (no chain txid).
            - Use `count`+`skip` for paging. Example: page 2 of 20 → `count=20, skip=20`.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> txs = rpc.listtransactions()
            >>> # Page with explicit paging and include watch-only:
            >>> txs2 = rpc.listtransactions("*", 20, 100, True)
        """

        # Build CLI args in the exact positional order the node expects.
        args = ["listtransactions"]

        # Determine if any optional arg is being used; if so, we must start filling positions.
        if (account is not None) or (count is not None) or (skip is not None) or (include_watchonly is not None):
            # Position 1: account — if omitted but later args provided, pass "*" per help text.
            args.append(str(account) if account is not None else "*")

            # Position 2: count — if later args require alignment but count is None, use default 10.
            if (count is not None) or (skip is not None) or (include_watchonly is not None):
                args.append(str(int(count) if count is not None else 10))

            # Position 3: skip — if include_watchonly requires alignment but skip is None, use default 0.
            if (skip is not None) or (include_watchonly is not None):
                args.append(str(int(skip) if skip is not None else 0))

            # Position 4: include_watchonly — only if explicitly provided.
            if include_watchonly is not None:
                args.append("true" if include_watchonly else "false")

        command = self._build_command() + args

        try:
            # Execute the command; non-zero exit raises CalledProcessError (stderr captured for error message).
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize and parse stdout.
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            try:
                return json.loads(out)
            except json.JSONDecodeError:
                # If node returns plain text for some reason, surface it verbatim.
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def listunspent(self, minconf=None, maxconf=None, addresses=None, include_unsafe=None, query_options=None):
        """
        Returns UTXOs (unspent transaction outputs) in the wallet, with flexible filters.

        Invokes the `listunspent` RPC. You can filter by confirmation range, restrict to
        specific addresses, include/exclude “unsafe” UTXOs, and apply query options (e.g.,
        minimum amount per UTXO, total minimum sum, max count).

        Mirrors native help:

            listunspent ( minconf maxconf ["addresses",...] [include_unsafe] [query_options] )

            Returns array of unspent transaction outputs with between minconf and maxconf
            (inclusive) confirmations. Optionally filter to only include txouts paid to
            specified addresses.

        Args:
            minconf (int | None, optional):
                Minimum confirmations to include (default = 1). If later parameters are
                provided and `minconf` is None, this wrapper supplies the default to keep
                positional arguments aligned.
            maxconf (int | None, optional):
                Maximum confirmations to include (default = 9_999_999). If later parameters
                are provided and `maxconf` is None, this wrapper supplies the default.
            addresses (list[str] | str | None, optional):
                A **JSON array** of Evrmore addresses to filter on. Pass a Python list/tuple
                and this wrapper will JSON-encode it; or pass a pre-serialized JSON string.
                If you provide `include_unsafe` or `query_options` but omit `addresses`,
                this wrapper will send an empty array `[]` to preserve positional order.
            include_unsafe (bool | None, optional):
                Include outputs not considered “safe” to spend (default = True). In Bitcoin/Evrmore
                semantics, “unsafe” typically includes unconfirmed UTXOs from external keys or RBF
                replacements. If `query_options` is provided but this is None, we send the default
                **true** to preserve positional order.
            query_options (dict | str | None, optional):
                JSON object with query options:
                  {
                    "minimumAmount": <number|string>,     # default 0 (per-UTXO minimum EVR)
                    "maximumAmount": <number|string>,     # default unlimited
                    "maximumCount":  <number|string>,     # default unlimited
                    "minimumSumAmount": <number|string>   # default unlimited (sum across UTXOs)
                  }
                Pass a Python dict (will be JSON-encoded) or a pre-serialized JSON string.

        Returns:
            list[dict] | str:
                On success: an array of UTXO objects like
                [
                  {
                    "txid": "<hex>",
                    "vout": <int>,
                    "address": "<address>",
                    "account": "<string>",         # DEPRECATED (may be "")
                    "scriptPubKey": "<hex>",
                    "amount": <number>,            # EVR
                    "confirmations": <int>,
                    "redeemScript": "<hex>",       # when scriptPubKey is P2SH
                    "spendable": <bool>,
                    "solvable": <bool>,
                    "safe": <bool>
                  },
                  ...
                ]
                If non-JSON text is returned, the raw string is returned.
                If there’s no output, returns "No data returned."
                On error, returns: "Error: <node stderr or exception message>"

        Notes:
            - **Positional rules** (important):
                * If you pass `addresses`, you must also pass `minconf` and `maxconf` (this wrapper
                  auto-fills defaults when omitted).
                * If you pass `query_options`, you must also include `include_unsafe` (this wrapper
                  auto-fills its default **true** when omitted) and (by position) `addresses`
                  (auto-filled to `[]` if omitted), plus preceding `minconf`/`maxconf`.
            - The `"safe"` attribute reflects the wallet’s policy for spend eligibility.
            - Use this output to build manual coin selection for raw transactions.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> utxos = rpc.listunspent()
            >>> utxos2 = rpc.listunspent(
            ...     minconf=6,
            ...     maxconf=9_999_999,
            ...     addresses=["mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF", "n4iLxDUVRsJrf4824Wdur2nVoZDAtGUtEv"],
            ...     include_unsafe=True,
            ...     query_options={"minimumAmount": 0.005}
            ... )
        """

        # Build the CLI args in the exact positional order the node expects.
        args = ["listunspent"]

        # Determine which earlier positions must be supplied due to later args.
        need_addresses = (addresses is not None) or (include_unsafe is not None) or (query_options is not None)
        need_maxconf = (maxconf is not None) or need_addresses
        need_minconf = (minconf is not None) or need_maxconf

        # Position 1: minconf (supply default 1 if later args require alignment)
        if need_minconf:
            args.append(str(int(minconf) if minconf is not None else 1))

        # Position 2: maxconf (supply default 9_999_999 if later args require alignment)
        if need_maxconf:
            args.append(str(int(maxconf) if maxconf is not None else 9_999_999))

        # Position 3: addresses (JSON array) — required if include_unsafe or query_options are provided
        if need_addresses:
            if addresses is None:
                addresses_json = "[]"
            elif isinstance(addresses, (list, tuple)):
                try:
                    addresses_json = json.dumps(list(addresses))
                except (TypeError, ValueError) as ser_err:
                    return f"Error: Failed to serialize 'addresses' to JSON: {ser_err}"
            else:
                # Assume caller passed a pre-serialized JSON string
                addresses_json = str(addresses)
            args.append(addresses_json)

        # Position 4: include_unsafe — append if explicitly provided OR if query_options is present
        if (include_unsafe is not None) or (query_options is not None):
            # Default is true per help text
            inc_unsafe = True if include_unsafe is None else bool(include_unsafe)
            args.append("true" if inc_unsafe else "false")

        # Position 5: query_options — only if provided; JSON object
        if query_options is not None:
            if isinstance(query_options, dict):
                try:
                    query_json = json.dumps(query_options)
                except (TypeError, ValueError) as ser_err:
                    return f"Error: Failed to serialize 'query_options' to JSON: {ser_err}"
            else:
                query_json = str(query_options)
            args.append(query_json)

        command = self._build_command() + args

        try:
            # Execute RPC; non-zero exit raises CalledProcessError (stderr captured in exception).
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout for parsing.
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Expected: JSON array of UTXO objects.
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out  # surface raw text if not valid JSON

        except Exception as e:
            # Standardized error format (shows node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def listwallets(self):
        """
        Returns a list of currently loaded wallets.

        Invokes the `listwallets` RPC. For full details about a specific wallet,
        call `getwalletinfo` after selecting or loading it.

        Mirrors native help:

            listwallets
            Returns a list of currently loaded wallets.
            For full information on the wallet, use "getwalletinfo"

        Returns:
            list[str] | str:
                - On success: a list of wallet names, e.g. ["", "wallet1", "wallet2"].
                  ("" often represents the default/primary wallet when applicable.)
                - If the node returns non-JSON text, that raw text is returned.
                - If there’s no output, returns "No data returned."
                - On error, returns: "Error: <node stderr or exception message>"

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> wallets = rpc.listwallets()
        """

        # Build the CLI command with auth/network flags and the RPC name (no parameters).
        command = self._build_command() + ["listwallets"]

        try:
            # Execute the command. Non-zero exit -> CalledProcessError (we surface stderr below).
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout and attempt JSON parse (expected: JSON array of strings).
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            try:
                return json.loads(out)
            except json.JSONDecodeError:
                # If the daemon returned plain text for some reason, surface it as-is.
                return out

        except Exception as e:
            # Standardized error format (shows node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def lockunspent(self, unlock, transactions=None):
        """
        Lock or unlock specific UTXOs to control coin selection.

        Invokes the `lockunspent` RPC. You can:
          - **Lock** UTXOs (`unlock=False`) so the wallet will not spend them automatically.
          - **Unlock** specific UTXOs (`unlock=True` with a list), or **unlock all** currently
            locked UTXOs by omitting the list.

        Mirrors native help:

            lockunspent unlock ([{"txid":"txid","vout":n},...])

            Updates list of temporarily unspendable outputs.
            Temporarily lock (unlock=false) or unlock (unlock=true) specified transaction outputs.
            If no transaction outputs are specified when unlocking then all current locked
            transaction outputs are unlocked.
            A locked transaction output will not be chosen by automatic coin selection.
            Locks are stored **in memory** only and are cleared when the node stops.

        Args:
            unlock (bool):
                - `True`  → unlock (the given UTXOs, or **all** if `transactions` is omitted).
                - `False` → lock (the given UTXOs must be provided).
            transactions (list[dict] | str | None, optional):
                A list (or pre-serialized JSON string) of UTXO descriptors:
                  [{ "txid": "<hex>", "vout": <int> }, ...]
                - Required when **locking** (`unlock=False`).
                - Optional when **unlocking** (`unlock=True`). If omitted, **all** locked
                  outputs are unlocked.

        Returns:
            bool | str:
                - On success: `True` or `False` (as returned by the node).
                - If the node returns non-JSON text, that raw text is returned.
                - If there’s no output, returns "No data returned."
                - On error, returns: "Error: <node stderr or exception message>".

        Notes:
            - See also: `listlockunspent` to view currently locked UTXOs.
            - Locks reside only in memory and are reset on restart.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> result1 = rpc.lockunspent(False, [{"txid": "a08e69...adf0", "vout": 1}])
            >>> result2 = rpc.lockunspent(True,  [{"txid": "a08e69...adf0", "vout": 1}])
            >>> result3 = rpc.lockunspent(True)
        """

        # Build the CLI args in the exact positional order the node expects.
        args = ["lockunspent", "true" if unlock else "false"]

        # If a list/string of transactions is provided, serialize/append it.
        if transactions is not None:
            if isinstance(transactions, (list, tuple)):
                try:
                    tx_json = json.dumps(transactions)
                except (TypeError, ValueError) as ser_err:
                    return f"Error: Failed to serialize 'transactions' to JSON: {ser_err}"
            else:
                # Assume caller passed a pre-serialized JSON string.
                tx_json = str(transactions)
            args.append(tx_json)
        else:
            # When locking (unlock=False), a transactions list is expected by the node.
            # We let the node error if it's missing, rather than enforcing here.
            pass

        command = self._build_command() + args

        try:
            # Execute the command; non-zero exit will raise and we’ll surface node stderr below.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Node typically returns a bare JSON boolean.
            try:
                parsed = json.loads(out)
                if isinstance(parsed, bool):
                    return parsed
                if isinstance(parsed, str):
                    low = parsed.strip().lower()
                    if low == "true":
                        return True
                    if low == "false":
                        return False
                return parsed  # If some other JSON structure, return as-is.
            except json.JSONDecodeError:
                # Fallback for plain-text 'true'/'false'
                low = out.lower()
                if low == "true":
                    return True
                if low == "false":
                    return False
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def move(self, fromaccount, toaccount, amount, minconf_or_dummy=None, comment=None):
        """
        (DEPRECATED) Move funds between legacy **accounts** within the same wallet.

        Invokes the `move` RPC. This **does not create a blockchain transaction**; it only
        adjusts internal account balances in your wallet’s old “accounts” system.

        Mirrors native help:

            move "fromaccount" "toaccount" amount ( minconf "comment" )
            DEPRECATED. Move a specified amount from one account in your wallet to another.

        Args:
            fromaccount (str):
                Legacy source account name. The empty string `""` refers to the default account.
            toaccount (str):
                Legacy destination account name. `""` refers to the default account.
            amount (int | float | str):
                Amount of **EVR** to move between accounts. Accepts number or numeric string.
            minconf_or_dummy (int | None, optional):
                The **4th positional** argument is retained for backward compatibility and is
                ignored by many builds. Historically it represented `minconf`. Pass `None` to
                omit it, or an integer (e.g., `0`, `1`, `6`). If you provide a `comment` but
                omit this slot, this wrapper will send `0` as a placeholder to keep positions aligned.
            comment (str | None, optional):
                Optional wallet-only comment/label for bookkeeping.

        Returns:
            bool | str:
                - On success: `True` if the move was recorded, `False` otherwise (as returned by the node).
                - If the node returns non-JSON text, that raw text is returned.
                - If there’s no output, returns **"No data returned."**
                - On error, returns: **"Error: <node stderr or exception message>"**.

        Notes:
            - The legacy **accounts** system is deprecated; modern wallets prefer **labels**.
            - Because no on-chain transaction is created, there is **no fee** and **no txid**.
            - Use this only if you rely on the old account-based bookkeeping.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> # Move 0.01 EVR from default ("") to "ops" with a comment:
            >>> ok = rpc.move("", "ops", 0.01, 0, "budget rebalancing")
        """

        # ---- Build CLI args in exact positional order the node expects -------------------------
        # Required positions: fromaccount, toaccount, amount
        args = [
            "move",
            str(fromaccount),
            str(toaccount),
            str(amount),  # accept int/float/Decimal/str; node parses number from string
        ]

        # Optional positions:
        # 4th: legacy minconf/dummy (often ignored by modern nodes)
        # 5th: comment
        if (minconf_or_dummy is not None) or (comment is not None):
            # If user supplied the 4th slot, honor it; otherwise send 0 to allow a comment in 5th.
            if minconf_or_dummy is not None:
                args.append(str(int(minconf_or_dummy)))
            else:
                args.append("0")

            # Append comment only if provided.
            if comment is not None:
                args.append(str(comment))

        command = self._build_command() + args

        try:
            # Execute the command; non-zero exit -> CalledProcessError (stderr captured in exception).
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout and try to parse a boolean.
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Expected: bare JSON boolean true/false
            try:
                parsed = json.loads(out)
                if isinstance(parsed, bool):
                    return parsed
                if isinstance(parsed, str):
                    low = parsed.strip().lower()
                    if low == "true":
                        return True
                    if low == "false":
                        return False
                # If some other JSON is returned, surface it.
                return parsed
            except json.JSONDecodeError:
                # Fallback for plain-text 'true'/'false'
                low = out.lower()
                if low == "true":
                    return True
                if low == "false":
                    return False
                return out

        except Exception as e:
            # Standardized error format you requested (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def removeprunedfunds(self, txid):
        """
        Removes a specific transaction from the wallet (for pruned-wallet workflows).

        Invokes the `removeprunedfunds` RPC. This deletes the specified transaction
        from the wallet’s internal store. It is intended as a companion to
        `importprunedfunds` for **pruned** wallets and **will affect wallet balances**.

        Mirrors native help:

            removeprunedfunds "txid"

            Deletes the specified transaction from the wallet. Meant for use with
            pruned wallets and as a companion to importprunedfunds. This will affect
            wallet balances.

        Args:
            txid (str):
                The hex-encoded transaction id to remove from the wallet.

        Returns:
            str:
                - On success, nodes typically print nothing; this wrapper returns
                  **"Transaction removed from wallet."** if stdout is empty.
                - If the node returns JSON/text, it is surfaced (parsed to string if JSON).
                - On error, returns: **"Error: <node stderr or exception message>"**.

        Warnings:
            - This operation **changes wallet balances** (e.g., credits/debits tied to
              the removed transaction will no longer be reflected).
            - Use with care; ensure you understand the implications for accounting and
              any subsequent imports/rescans.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> out = rpc.removeprunedfunds("a8d0c0184dde994a09ec054286f1ce58...ea0a5")
        """

        # Build the CLI command with auth/network flags + RPC name + required txid.
        command = self._build_command() + [
            "removeprunedfunds",
            str(txid),
        ]

        try:
            # Run the command; non-zero exit raises CalledProcessError (we surface stderr below).
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Many builds return no stdout on success.
            out = (result.stdout or "").strip()
            if not out:
                return "Transaction removed from wallet."

            # Try to parse JSON; otherwise return raw text.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, (dict, list, str)) else str(parsed)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error format (surfaces node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def rescanblockchain(self, start_height=None, stop_height=None):
        """
        Rescan the local blockchain for wallet-related transactions.

        Invokes the `rescanblockchain` RPC. This walks the chain and (re)discovers
        transactions that affect your wallet. Useful after importing keys/addresses
        or recovering a wallet.

        Mirrors native help:

            rescanblockchain ("start_height") ("stop_height")

            Rescan the local blockchain for wallet related transactions.

            1. "start_height" (numeric, optional) block height where the rescan should start
            2. "stop_height"  (numeric, optional) the last block height that should be scanned

        Args:
            start_height (int | None, optional):
                Block height to **begin** scanning from. If omitted, the node starts from
                the genesis block.
            stop_height (int | None, optional):
                Last block height to scan. If omitted, the node scans up to the current tip.
                Because parameters are positional, if you want to provide `stop_height`
                without a specific `start_height`, this wrapper will pass **0** for
                `start_height` to preserve argument order.

        Returns:
            dict | str:
                - On success (typical): a dict like:
                  {
                    "start_height": <int>,  # actual start height used
                    "stop_height":  <int>   # last rescanned block (or tip)
                  }
                - If the node returns non-JSON text, that raw string is returned.
                - If there’s no output, returns **"Rescan started (this may take a while)."**
                - On error, returns: **"Error: <node stderr or exception message>"**.

        Notes:
            - Rescans can be **time-consuming** on long chains.
            - You can call `abortrescan` from another thread/process to stop an ongoing rescan.
            - After importing multiple keys/addresses, consider one rescan at the end rather
              than rescanning for each import individually.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> info = rpc.rescanblockchain()
        """

        # Build the CLI args in the exact positional order the node expects.
        args = ["rescanblockchain"]

        # If the caller supplies any optional parameter, we must begin filling positions.
        if (start_height is not None) or (stop_height is not None):
            # If stop_height is provided but start_height is not, use 0 to align positions.
            effective_start = 0 if (start_height is None and stop_height is not None) else start_height

            # Position 1: start_height (if None and stop provided, we used 0 above)
            if effective_start is not None:
                args.append(str(int(effective_start)))
            else:
                # If only start was provided as None (and stop also None) we wouldn't be here.
                # This clause is defensive; it shouldn't run.
                args.append(str(0))

            # Position 2: stop_height — only append if explicitly provided.
            if stop_height is not None:
                args.append(str(int(stop_height)))

        # Compose the full command with base flags + RPC name + arguments.
        command = self._build_command() + args

        try:
            # Execute the RPC; non-zero exit raises CalledProcessError (we surface stderr below).
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout for parsing.
            out = (result.stdout or "").strip()
            if not out:
                # Some nodes may stream progress elsewhere or return nothing until complete.
                return "Rescan started (this may take a while)."

            # Expected: JSON object with start_height/stop_height.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, (dict, list, str)) else str(parsed)
            except json.JSONDecodeError:
                # If the daemon returned plain text, surface it as-is so the caller can inspect.
                return out

        except Exception as e:
            # Standardized error format (shows node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def sendfrom(self, fromaccount, toaddress, amount, minconf=None, comment=None, comment_to=None):
        """
        (DEPRECATED — prefer `sendtoaddress`) Send an amount from a legacy account to an address.

        Invokes the `sendfrom` RPC. Sends EVR from the specified **legacy account** to a
        destination address. The legacy account system is deprecated; amounts sent are
        associated with that account for bookkeeping/history only.

        Mirrors native help:

            sendfrom "fromaccount" "toaddress" amount ( minconf "comment" "comment_to" )

            DEPRECATED (use sendtoaddress). Send an amount from an account to an Evrmore address.

        Args:
            fromaccount (str):
                Legacy account to debit. The empty string `""` refers to the default account.
                Choosing an account does **not** influence coin selection; it only tags history.
            toaddress (str):
                Destination Evrmore address.
            amount (int | float | str):
                Amount in **EVR** to send (fee added on top). Numeric or numeric string accepted.
            minconf (int | None, optional):
                Only use funds with at least this many confirmations (default = 1).
                Positional note: if you provide `comment`/`comment_to` but not `minconf`,
                this wrapper auto-fills the default `1` to keep positions aligned.
            comment (str | None, optional):
                Wallet-only note describing the purpose of the transaction (not on-chain).
            comment_to (str | None, optional):
                Wallet-only note naming the recipient (not on-chain).

        Returns:
            str:
                - On success: the transaction id (`txid`) as a string.
                - If the node returns JSON/text, it’s surfaced (parsed to str if JSON).
                - If no output is produced, returns **"No data returned."**
                - On error, returns: **"Error: <node stderr or exception message>"**.

        Notes:
            - This RPC exists for backward compatibility with the legacy **accounts** system.
            - Prefer `sendtoaddress` for modern workflows.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> txid = rpc.sendfrom("", "n4iLxDUVRsJrf4824Wdur2nVoZDAtGUtEv", 0.01, 6, "donation", "ops")
            >>> isinstance(txid, str)
            True
        """

        # ---- Build CLI args in the exact positional order the node expects --------------------
        args = [
            "sendfrom",
            str(fromaccount),
            str(toaddress),
            str(amount),  # node parses number from string; supports ints/floats/strings
        ]

        # Optional positions (in order): minconf, comment, comment_to
        if (minconf is not None) or (comment is not None) or (comment_to is not None):
            # Position 4: minconf — if later args present but minconf omitted, use default 1
            args.append(str(int(minconf) if minconf is not None else 1))

            # Position 5: comment — only if provided OR if comment_to requires alignment
            if (comment is not None) or (comment_to is not None):
                args.append("" if comment is None else str(comment))

            # Position 6: comment_to — only if explicitly provided
            if comment_to is not None:
                args.append(str(comment_to))

        command = self._build_command() + args

        try:
            # Execute the command; on non-zero exit, CalledProcessError is raised with stderr.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Node typically returns a JSON-quoted txid string; parse if possible.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                # Fallback: surface raw text (some builds may not JSON-quote).
                return out

        except Exception as e:
            # Standardized error format you requested (prefers node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def sendfromaddress(self, from_address, to_address, amount,comment=None, comment_to=None, subtractfeefromamount=None, conf_target=None, estimate_mode=None):
        """
        Send EVR **from a specific address** to a destination address (change returns to the source).

        Invokes the `sendfromaddress` RPC. Unlike `sendtoaddress`, this call **forces inputs** to be
        selected from `from_address` and sends all change back to that same address.

        Mirrors native help:

            sendfromaddress "from_address" "to_address" amount
                            ( "comment" "comment_to" subtractfeefromamount conf_target "estimate_mode")

            1. "from_address"       (string, required) The Evrmore address to send from.
            2. "to_address"         (string, required) The Evrmore address to send to.
            3. "amount"             (numeric or string, required) The amount in EVR to send (e.g., 0.1).
            4. "comment"            (string, optional) Wallet-only note about the purpose.
            5. "comment_to"         (string, optional) Wallet-only note naming the recipient.
            6. subtractfeefromamount (bool, optional, default=false) If true, fee is deducted from `amount`.
            7. conf_target          (numeric, optional) Target confirmations (blocks) for fee estimation.
            8. "estimate_mode"      (string, optional, default=UNSET) One of: UNSET | ECONOMICAL | CONSERVATIVE.

        Args:
            from_address (str): Source address (inputs will be chosen from here; change returns here).
            to_address (str):   Destination address.
            amount (int | float | str): Amount in EVR to send. (Number or numeric string.)
            comment (str | None, optional): Wallet-only memo. Not broadcast on-chain.
            comment_to (str | None, optional): Wallet-only recipient note. Not on-chain.
            subtractfeefromamount (bool | None, optional): If True, recipient receives `amount - fee`.
            conf_target (int | None, optional): Fee target confirmations (blocks).
            estimate_mode (str | None, optional): "UNSET" | "ECONOMICAL" | "CONSERVATIVE".
                Note: If you wish to set `estimate_mode`, you should also provide `conf_target`
                (because it occupies the prior positional slot).

        Returns:
            str:
                - On success: the transaction id (`txid`) string.
                - If daemon returns JSON/text, it is surfaced (parsed to string if JSON).
                - If no output: "No data returned."
                - On error: "Error: <node stderr or exception message>"

        Positional/compat notes:
            - RPC parameters are positional. If you provide a later parameter (e.g., `conf_target`)
              you must also provide **placeholders for earlier ones**:
                * For `comment`/`comment_to` use empty strings `""` if you have nothing to say.
                * For `subtractfeefromamount`, use its default `false` if you only want to set `conf_target`.
            - Some daemon builds are picky about types for `conf_target`. This wrapper sends numeric
              values as integers and ensures earlier placeholders are included to align positions.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> # Simple send with defaults:
            >>> txid = rpc.sendfromaddress("mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF",
            ...                            "n4iLxDUVRsJrf4824Wdur2nVoZDAtGUtEv", 0.10)
            >>> # Provide conf_target → also include placeholders for earlier args:
            >>> txid2 = rpc.sendfromaddress("mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF",
            ...                             "n4iLxDUVRsJrf4824Wdur2nVoZDAtGUtEv",
            ...                             0.10, "", "", False, 6, "CONSERVATIVE")
        """

        # --- Build the CLI command in the exact positional order the node expects ---------------
        args = [
            "sendfromaddress",
            str(from_address),
            str(to_address),
            str(amount),  # pass numbers as strings; the CLI/RPC will parse numeric type
        ]

        # If ANY optional param is provided, we must begin filling the optional slots in order:
        # 4: comment, 5: comment_to, 6: subtractfeefromamount, 7: conf_target, 8: estimate_mode
        any_optional = (
                comment is not None
                or comment_to is not None
                or subtractfeefromamount is not None
                or conf_target is not None
                or estimate_mode is not None
        )
        if any_optional:
            # Slot 4: comment (empty string if later params require alignment)
            args.append("" if comment is None else str(comment))

            # Slot 5: comment_to (empty string if later params require alignment)
            # If comment_to is None but later params exist, pass "" to hold its place.
            if (comment_to is not None) or (subtractfeefromamount is not None) or (conf_target is not None) or (
                    estimate_mode is not None):
                args.append("" if comment_to is None else str(comment_to))

            # Slot 6: subtractfeefromamount
            if (subtractfeefromamount is not None) or (conf_target is not None) or (estimate_mode is not None):
                sffa = False if subtractfeefromamount is None else bool(subtractfeefromamount)
                args.append("true" if sffa else "false")

            # Slot 7: conf_target (only if explicitly provided)
            if conf_target is not None:
                args.append(str(int(conf_target)))

            # Slot 8: estimate_mode — only include if explicitly provided.
            # (Best practice: supply conf_target if you set estimate_mode.)
            if estimate_mode is not None:
                args.append(str(estimate_mode))

        command = self._build_command() + args

        try:
            # Execute the command; non-zero exit raises CalledProcessError with stderr attached.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Daemon typically returns a JSON-quoted txid; parse if possible.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                # If non-JSON, return raw text.
                return out

        except Exception as e:
            # Standardized error format you requested (prefer node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def sendmany(
            self,
            fromaccount,
            amounts,
            minconf=None,
            comment=None,
            subtractfeefrom=None,  # list[str] | str | None  (JSON array of addresses)
            conf_target=None,
            estimate_mode=None,
    ):
        """
        Send to multiple recipients in a single transaction.

        Invokes the `sendmany` RPC. Builds one transaction paying multiple addresses and can
        optionally subtract fees from specified recipients’ outputs.

            sendmany "fromaccount" {"address":amount,...}
                     ( minconf "comment" ["address",...] conf_target "estimate_mode")

        Args:
            fromaccount (str):
                DEPRECATED legacy account to associate the spend with. Use "" for the default
                account. (Does not affect coin selection; only tags history.)

            amounts (dict[str, int|float|str] | str):
                Mapping of destination addresses to EVR amounts, e.g.:
                    {"mzKoq...": 0.01, "n4iLx...": "0.02"}
                You may pass a Python dict (this wrapper JSON-encodes it) or a pre-serialized
                JSON string. For safety against float rounding, strings like "0.01000000" are
                recommended.

            minconf (int | None, optional, default=1):
                Only use funds with at least this many confirmations. Because parameters are
                positional, if you provide later parameters (e.g., comment) but omit `minconf`,
                this wrapper supplies the default **1** to maintain correct positions.

            comment (str | None, optional):
                Wallet-only comment (not on-chain). If later parameters are provided (such as
                `subtractfeefrom`) and you omit `comment`, this wrapper passes an empty string
                "" to preserve positional order.

            subtractfeefrom (list[str] | str | None, optional):
                **JSON array of addresses** whose outputs should have the fee **equally deducted**.
                - Pass a Python list/tuple of addresses (encoded here) or a pre-serialized JSON
                  array string like: '["addr1","addr2"]'.
                - If later parameters are provided and you omit this one, this wrapper sends an
                  empty array `[]` placeholder so positions stay aligned.
                - If no addresses are specified, the sender pays the fee on top.

            conf_target (int | None, optional):
                Confirmation target (in blocks) for fee estimation. Only sent if provided. If you
                set `estimate_mode`, you should also set this (it sits in the prior positional slot).

            estimate_mode (str | None, optional):
                One of: "UNSET", "ECONOMICAL", "CONSERVATIVE". Only sent if provided.

        Returns:
            str:
                - On success: the transaction id (`txid`) as a string (one tx regardless of
                  number of recipients).
                - If the node returns non-JSON text, that raw text is returned.
                - If no output is produced: "No data returned."
                - On error: "Error: <node stderr or exception message>"

        Positional rules (important):
            - RPC params are positional. If you set `conf_target` or `estimate_mode`, you must
              also include earlier placeholders:
                * `minconf` → we insert default **1** if omitted.
                * `comment` → we insert **""** if omitted.
                * `subtractfeefrom` → we insert **[]** if omitted.
            - This wrapper handles those placeholders for you automatically.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> txid = rpc.sendmany(
            ...     fromaccount="",
            ...     amounts={"mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF": "0.01",
            ...              "n4iLxDUVRsJrf4824Wdur2nVoZDAtGUtEv": 0.02},
            ...     minconf=6,
            ...     comment="payout batch",
            ...     subtractfeefrom=["mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF"],  # JSON array of addresses
            ...     conf_target=6,
            ...     estimate_mode="CONSERVATIVE",
            ... )
            >>> isinstance(txid, str)
            True
        """

        # ---- Build the base argument list in the exact positional order the node expects ----
        args = ["sendmany", str(fromaccount)]

        # amounts can be dict (we JSON-encode compactly) or a JSON string the user provided.
        if isinstance(amounts, dict):
            try:
                # Compact JSON avoids any CLI parsing quirks.
                amounts_json = json.dumps(amounts, default=str, separators=(",", ":"))
            except (TypeError, ValueError) as ser_err:
                return f"Error: Failed to serialize 'amounts' to JSON: {ser_err}"
        else:
            amounts_json = str(amounts)
        args.append(amounts_json)

        # If any optional param is present, we must begin appending placeholders/values in order.
        any_optional = (
                minconf is not None
                or comment is not None
                or subtractfeefrom is not None
                or conf_target is not None
                or estimate_mode is not None
        )

        if any_optional:
            # Slot 3: minconf (default to 1 if omitted but later params exist)
            args.append(str(int(minconf) if minconf is not None else 1))

            # Slot 4: comment (use "" if omitted but later params exist)
            if (comment is not None) or (subtractfeefrom is not None) or (conf_target is not None) or (
                    estimate_mode is not None):
                args.append("" if comment is None else str(comment))

            # Slot 5: subtractfeefrom must be a JSON array string; include [] if omitted but later args exist
            if (subtractfeefrom is not None) or (conf_target is not None) or (estimate_mode is not None):
                if subtractfeefrom is None:
                    sff_json = "[]"
                elif isinstance(subtractfeefrom, (list, tuple)):
                    try:
                        sff_json = json.dumps(list(subtractfeefrom), separators=(",", ":"))
                    except (TypeError, ValueError) as ser_err:
                        return f"Error: Failed to serialize 'subtractfeefrom' to JSON: {ser_err}"
                else:
                    # Assume caller passed a JSON array string; accept as-is. Optionally validate:
                    try:
                        parsed = json.loads(str(subtractfeefrom))
                        if not isinstance(parsed, list):
                            return "Error: 'subtractfeefrom' must be a JSON array (list of addresses)."
                        sff_json = json.dumps(parsed, separators=(",", ":"))
                    except Exception:
                        return "Error: 'subtractfeefrom' must be a JSON array (e.g., [\"addr1\",\"addr2\"])."
                args.append(sff_json)

            # Slot 6: conf_target (append only if provided)
            if conf_target is not None:
                args.append(str(int(conf_target)))

            # Slot 7: estimate_mode (append only if provided)
            if estimate_mode is not None:
                args.append(str(estimate_mode))

        # Compose the full command for subprocess
        command = self._build_command() + args

        try:
            # Execute the RPC; non-zero exit raises CalledProcessError (stderr captured on exception)
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Node typically returns a JSON-quoted txid string; parse if possible.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                # If non-JSON, return raw text as-is.
                return out

        except Exception as e:
            # Standardized, user-friendly error surfacing (prefer node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()


    def sendtoaddress(self, address, amount, comment="", comment_to="",
                      subtractfeefromamount=False, conf_target="", estimate_mode=""):
        """
        Sends EVR to a given address.

        Invokes the `sendtoaddress` wallet RPC to send `amount` EVR to `address`. Optional
        fields allow attaching local wallet comments (not on-chain), subtracting the fee from
        the sent amount, and setting fee target/mode.

        Mirrors native help:

            sendtoaddress "address" amount ( "comment" "comment_to" subtractfeefromamount conf_target "estimate_mode")

            1. "address"               (string, required)   Evrmore address to send to
            2. "amount"                (numeric|string, required) EVR amount (e.g., 0.1)
            3. "comment"               (string, optional)   Local wallet note (not on-chain)
            4. "comment_to"            (string, optional)   Local wallet note for recipient (not on-chain)
            5. subtractfeefromamount   (boolean, optional, default=false) Deduct fee from amount
            6. conf_target             (numeric, optional)  Confirmation target (blocks)
            7. "estimate_mode"         (string, optional, default=UNSET) One of:
                  "UNSET" | "ECONOMICAL" | "CONSERVATIVE"

        Args:
            address (str):
                Destination Evrmore address.
            amount (float | str):
                Amount in EVR. Prefer a **string** or `Decimal`-to-string if you need exactness
                (floats may introduce binary rounding).
            comment (str, optional):
                Local wallet memo for this tx (not broadcast). Omit by passing `None`. Include an
                empty comment by passing `""`.
            comment_to (str, optional):
                Local wallet memo for the recipient (not broadcast). Same omission rules as above.
            subtractfeefromamount (bool, optional):
                If `True`, the network fee is subtracted from `amount` (recipient gets less).
            conf_target (int | float, optional):
                Desired confirmation target in blocks.
            estimate_mode (str, optional):
                Fee estimate mode: `"UNSET"`, `"ECONOMICAL"`, or `"CONSERVATIVE"`.

        Returns:
            str:
                On success, the transaction ID (`txid`) as a string.
                If the node returns non-JSON text, that raw text is returned.
                On error, returns `"Error: <message>"`.

        Notes:
            - **Positional optionals**: If you provide a later argument, you must fill earlier
              positions. This wrapper does that for you:
                * If you set `subtractfeefromamount` but omit comments, it sends `""` placeholders
                  for `comment` and `comment_to`.
                * If you set `estimate_mode` but omit `conf_target`, it inserts a placeholder `0`
                  for `conf_target` to preserve positions.
            - Wallet comments (`comment`, `comment_to`) are **not** part of the on-chain tx.
            - For precise monetary values, pass `amount` as a string (e.g., `"0.10000000"`).

        Example:
            Basic send:

            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",rpc_user="user", rpc_pass="pass", testnet=True)
            >>> txid = rpc.sendtoaddress("mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF", "0.10")

            Subtract fee from amount + set fee target/mode (no comments):
            >>> txid = rpc.sendtoaddress("mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF", "1.2345",subtractfeefromamount=True, conf_target=6, estimate_mode="ECONOMICAL")

            With local wallet comments:
            >>> txid = rpc.sendtoaddress("mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF", "0.25",comment="donation", comment_to="project-x")
        """

        # Final command = base flags + RPC + args
        command = self._build_command() + [
            "sendtoaddress",
            str(address),
            str(amount),
            str(comment),
            str(comment_to),
            str(subtractfeefromamount).lower(),
            # int(conf_target),  # conf_target is not working
            # str(estimate_mode).upper() # can't get to this because conf_target breaks
        ]

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                # Usually this RPC returns a txid; if empty, surface something informative.
                return "No txid returned."

            # Try JSON; many nodes return a plain txid string (non-JSON), so fall back gracefully.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            # Show node stderr if present (CalledProcessError has .stderr)
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()



    def setaccount(self, address, account):
        """
        DEPRECATED: Associate an address with an account label in the wallet.

        Invokes the `setaccount` RPC to assign a legacy “account” (label) to an address.
        Modern wallets use labels instead of accounts; this call is retained for backwards
        compatibility with older tooling and scripts.

        Args:
            address (str):
                The Evrmore address to tag with the given account/label.
            account (str):
                The legacy account/label to associate with `address`.

        Returns:
            str:
                - `"Success."` if the node returns no output (typical for this RPC).
                - Any non-empty textual output from the node (returned as-is).
                - If the node returns JSON, it will be decoded and returned as a string.
                - On error: `"Error: <node stderr or exception message>"`.

        Notes:
            - This RPC is **deprecated**. Prefer newer label/descriptor-based workflows.
            - No blockchain state is changed; this only affects the wallet’s internal bookkeeping.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> result = rpc.setaccount("mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF", "tabby")
            >>> isinstance(result, str)
            True
        """

        # Build the CLI command with authentication/network flags, followed by the RPC name
        # and its required positional arguments. We convert to str to be safe for subprocess.
        command = self._build_command() + [
            "setaccount",
            str(address),  # The address to associate
            str(account),  # The (deprecated) account/label
        ]

        try:
            # Execute the command and capture stdout/stderr. check=True raises on non-zero exit.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout: most nodes return empty output on success for this RPC.
            out = (result.stdout or "").strip()

            if not out:
                # Typical success path: no payload, just acknowledge.
                return "Success."

            # If the node printed something, try to parse it as JSON first (defensive).
            try:
                parsed = json.loads(out)
                # Even if it’s JSON, normalize to string for consistent return type.
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                # Not JSON—return the raw text so the caller can see exactly what the node said.
                return out

        except Exception as e:
            # Standardized, user-friendly error surfacing (prefer node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def settxfee(self, amount):
        """
        Set the wallet's manual transaction fee rate (per kB).

        Invokes the `settxfee` RPC to overwrite the wallet's `paytxfee` parameter, which
        applies when manual fees are enabled. Some nodes may still prefer fee estimation;
        this call ensures a fixed fee rate is set at the wallet layer.

            settxfee amount

        Args:
            amount (int | float | str | Decimal):
                The fee rate in EVR **per kilobyte** (kB). For precision, passing a string
                like `"0.00001000"` (or a `Decimal`) is recommended instead of a float.

        Returns:
            bool | str:
                - `True` / `False` if the node returns a boolean result (typical).
                - `"Success."` if the node returns no output on success.
                - Any non-JSON text from the node (returned verbatim).
                - On error: `"Error: <node stderr or exception message>"`.

        Notes:
            - This sets a **manual** fee rate. If your node/build prioritizes fee
              estimation, the manual setting may be ignored unless explicitly enabled.
            - Value is per **kilobyte**, not per virtual byte.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> ok = rpc.settxfee("0.00001000")  # 0.00001 EVR/kB
        """
        # -- Normalize the amount to a string safely. Floats can introduce rounding noise.
        #    If Decimal is available, it’s best; otherwise, str() is acceptable for strings/ints.
        try:
            from decimal import Decimal
            if isinstance(amount, float):
                # Convert float -> Decimal via str() to avoid binary float artifacts.
                amount_str = str(Decimal(str(amount)))
            elif isinstance(amount, Decimal):
                amount_str = str(amount)
            else:
                amount_str = str(amount)
        except Exception:
            # Fallback: just stringify; node will validate.
            amount_str = str(amount)

        # Build the CLI command in proper positional order.
        command = self._build_command() + [
            "settxfee",
            amount_str,  # fee rate in EVR/kB
        ]

        try:
            # Run the RPC. Non-zero exit codes raise an exception (we’ll surface stderr nicely).
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            out = (result.stdout or "").strip()
            if not out:
                # Some builds return no payload on success.
                return "Success."

            # Try to parse JSON first (expected: true/false).
            try:
                parsed = json.loads(out)
                if isinstance(parsed, bool):
                    return parsed
                # If node returns something else JSON-y, return it as a string for transparency.
                return str(parsed)
            except json.JSONDecodeError:
                # Fallback: plain-text 'true'/'false' or other text.
                low = out.lower()
                if low == "true":
                    return True
                if low == "false":
                    return False
                return out

        except Exception as e:
            # Standardized error: prefer node stderr when available.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def signmessage(self, address, message):
        """
        Sign an arbitrary message with the private key of a wallet address.

        Invokes the `signmessage` RPC to produce a Base64-encoded signature for the
        exact message string you provide, using the private key corresponding to
        `address` (which must be present and unlocked in this wallet).

            signmessage "address" "message"

        Args:
            address (str):
                The Evrmore address whose private key will be used to sign.
                The address must belong to this wallet and have an available private key.
            message (str):
                The exact message to sign. The output signature is specific to this
                byte-for-byte content (including whitespace and casing).

        Returns:
            str:
                - On success: the Base64-encoded signature string.
                - If the node returns non-JSON text, that raw text is returned.
                - If no output: "No data returned."
                - On error: "Error: <node stderr or exception message>"

        Notes:
            - If the wallet is encrypted and locked, you must unlock it first
              (e.g., `walletpassphrase "pass" <timeout>`), otherwise the RPC will fail.
            - Verification can be done with `verifymessage(address, signature, message)`.
            - The message must match exactly at verification time.

        Example:
            >>> rpc = WalletRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> # (If encrypted) unlock first via walletpassphrase RPC
            >>> sig = rpc.signmessage("mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF", "hello world")
        """
        # Build the CLI command with auth/network flags followed by the RPC name and args.
        # Cast to str to be safe for subprocess argument handling.
        command = self._build_command() + [
            "signmessage",
            str(address),  # Must be a wallet-owned address with a private key
            str(message),  # Exact message to sign (whitespace/case sensitive)
        ]

        try:
            # Execute the RPC; non-zero exit status raises an exception with stderr attached.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Node typically returns a JSON-quoted string; parse if possible.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                # If not JSON, surface the raw output (may already be the signature string).
                return out

        except Exception as e:
            # Standardized error surface: prefer daemon stderr when present.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()
