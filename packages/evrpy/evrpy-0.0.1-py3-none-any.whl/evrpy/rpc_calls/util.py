from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json



class UtilRPC:

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

    def createmultisig(self, nrequired, keys):
        """
        Create a bare multi-signature (m-of-n) script and return its address + redeem script.

        Invokes the `createmultisig` RPC to build a P2SH/P2WSH-compatible multisig script
        requiring `nrequired` signatures out of the provided `keys` (addresses or hex pubkeys).
        This **does not** add the multisig to your wallet — it only returns the computed
        address and the hex-encoded redeem script. To track it in-wallet, use
        `addmultisigaddress` (Wallet RPC) or import the redeem script appropriately.

            createmultisig nrequired ["key", ...]

        Args:
            nrequired (int | str):
                The number of required signatures (m). Must be <= len(keys). Strings are
                accepted if they parse cleanly to an integer.
            keys (list[str]):
                A list of Evrmore addresses **or** hex-encoded public keys.
                - Order matters for some signing flows — keep a consistent order across parties.
                - If providing addresses, the node will derive pubkeys from its knowledge;
                  when constructing multisig *offline* or among multiple parties, prefer
                  raw public keys to avoid ambiguity.

        Returns:
            dict | str:
                - On success (JSON output expected): a dict with:
                    {
                      "address": "<multisig address>",
                      "redeemScript": "<hex redeem script>"
                    }
                - If non-JSON text is returned: that text verbatim.
                - If no output: "No data returned."
                - On error: "Error: <node stderr or exception message>"

        Notes:
            - This call does **not** store keys or scripts in the wallet.
            - To watch the address in-wallet, use:
                - `addmultisigaddress(nrequired, keys, account=...)` (deprecated account arg),
                  or
                - import the redeem script / witness script as needed.
            - If `nrequired` > number of provided keys, the daemon will error.
            - Duplicate or invalid keys will cause RPC failure.

        Example:
            >>> rpc = UtilRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...               rpc_user="user", rpc_pass="pass", testnet=True)
            >>> res = rpc.createmultisig(2, [
            ...     "mykyeu5VtJACsWiPytouAH6MRkqq5VmvsE",
            ...     "029a3c...<hex pubkey>..."
            ... ])
        """
        # --- Normalize/validate arguments ------------------------------------------
        # Ensure nrequired is an integer string; the daemon expects a numeric here.
        try:
            nreq_str = str(int(nrequired))
        except Exception as e:
            # Surface a clear, standardized error if caller passed a non-integer.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

        # The RPC expects the second arg to be a JSON array **string**. We serialize the
        # Python list to JSON so quoting/brackets are correct for the CLI.
        try:
            keys_json = json.dumps(list(map(str, keys)))
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

        # --- Build the CLI command in exact positional order -----------------------
        command = self._build_command() + [
            "createmultisig",
            nreq_str,  # m (number of required signatures)
            keys_json,  # JSON array string of addresses or hex pubkeys
        ]

        try:
            # Execute the RPC; check=True -> non-zero exit raises with stderr captured.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Prefer JSON parsing. The node should return {"address": "...", "redeemScript": "..."}.
            try:
                parsed = json.loads(out)
                # Return dict directly if that’s what we got; otherwise, stringify to be safe.
                return parsed if isinstance(parsed, dict) else str(parsed)
            except json.JSONDecodeError:
                # Fallback: return raw output if daemon didn’t emit JSON.
                return out

        except Exception as e:
            # Standardized, user-friendly error surfacing (prefer daemon stderr).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def estimatefee(self, nblocks):
        """
        (DEPRECATED) Estimate the fee rate (EVR/kB) to confirm within N blocks.

        Invokes the `estimatefee` RPC to return the approximate fee **per kilobyte**
        required for a transaction to begin confirming within `nblocks` blocks.
        This call is deprecated upstream; prefer `estimatesmartfee` if available.

            estimatefee nblocks

        Args:
            nblocks (int | str):
                Target confirmation window in blocks. Must be an integer ≥ 1.
                (Note: this RPC commonly returns -1 for 1-block targets.)

        Returns:
            float | int | str:
                - A numeric fee-per-kilobyte (float or int) if the node returns a
                  plain number that parses cleanly (e.g., 0.0001 or -1).
                - Raw text if the output isn’t JSON/number.
                - "No data returned." if stdout is empty.
                - On error: "Error: <node stderr or exception message>"

        Notes:
            - Negative values indicate insufficient data to estimate.
            - `-1` is always returned for `nblocks == 1`.
            - Prefer `estimatesmartfee` for more accurate estimates.

        Example:
            >>> rpc = UtilRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...               rpc_user="user", rpc_pass="pass", testnet=True)
            >>> fee = rpc.estimatefee(6)
        """
        # Ensure we pass an integer string to the daemon (CLI expects a number).
        try:
            nblocks_str = str(int(nblocks))
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

        # Build the command in exact positional order.
        command = self._build_command() + [
            "estimatefee",
            nblocks_str,
        ]

        try:
            # Execute the RPC. Non-zero exit codes raise with stderr captured.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Try JSON parse first: numbers like 0.0001 or -1 parse fine via json.loads.
            try:
                parsed = json.loads(out)
                # The node should return a bare number; if so, just return it.
                if isinstance(parsed, (int, float)):
                    return parsed
                # If the node returns an unexpected type, return it as string for transparency.
                return str(parsed)
            except json.JSONDecodeError:
                # Not JSON; attempt a simple numeric cast, else return raw text.
                try:
                    # Some builds print as plain number without JSON—handle that gracefully.
                    if "." in out:
                        return float(out)
                    return int(out)
                except ValueError:
                    return out

        except Exception as e:
            # Standardized, user-friendly error surfacing (prefer daemon stderr).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def estimatesmartfee(self, conf_target, estimate_mode=None):
        """
        Estimate the fee rate (EVR/kB) needed to start confirming within a target window.

        Invokes the `estimatesmartfee` RPC, which returns an estimate of the fee **per kilobyte**
        required for a transaction to begin confirming within `conf_target` blocks, plus the
        number of blocks for which the estimate is considered valid.

            estimatesmartfee conf_target ("estimate_mode")

        Args:
            conf_target (int | str):
                Desired confirmation target in blocks (1–1008). The node may clamp this
                internally (typically to ≥2 and ≤ the maximum it supports).
            estimate_mode (str | None, optional):
                Fee estimation mode. One of:
                  - "UNSET" (defaults internally to CONSERVATIVE)
                  - "ECONOMICAL"
                  - "CONSERVATIVE"
                Omit or pass None to let the node use its default.

        Returns:
            dict | str:
                - On success (JSON expected), a dict like:
                    {
                      "feerate": <numeric, optional>,  # EVR/kB
                      "errors": [<str>...],            # optional
                      "blocks": <int>                  # target where estimate was found
                    }
                  Note: "feerate" may be missing if estimation failed; check "errors".
                - If non-JSON text is returned: raw text string.
                - If no output: "No data returned."
                - On error: "Error: <node stderr or exception message>"

        Notes:
            - Prefer this over the deprecated `estimatefee`.
            - If insufficient data exists, the node may return no "feerate" and include
              messages in "errors".

        Example:
            >>> rpc = UtilRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...               rpc_user="user", rpc_pass="pass", testnet=True)
            >>> res = rpc.estimatesmartfee(6, "ECONOMICAL")
        """
        # --- Normalize & validate inputs ------------------------------------------
        # Ensure `conf_target` is an integer string for the CLI.
        try:
            conf_str = str(int(conf_target))
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

        # Normalize estimate_mode to the accepted set if provided.
        mode_arg = None
        if estimate_mode is not None:
            mode = str(estimate_mode).upper()
            allowed = {"UNSET", "ECONOMICAL", "CONSERVATIVE"}
            if mode not in allowed:
                return f"Error: invalid estimate_mode '{estimate_mode}'. Use UNSET, ECONOMICAL, or CONSERVATIVE."
            mode_arg = mode

        # --- Build the CLI command in positional order ----------------------------
        command = self._build_command() + ["estimatesmartfee", conf_str]
        if mode_arg is not None:
            command.append(mode_arg)

        try:
            # Execute the RPC; non-zero exit will raise with stderr captured.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Prefer JSON parsing; node should return a small JSON object.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, dict) else str(parsed)
            except json.JSONDecodeError:
                # Fallback: return raw output so caller sees exactly what the node said.
                return out

        except Exception as e:
            # Standardized error surfacing (prefer daemon stderr, then exception text).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def signmessagewithprivkey(self, privkey, message):
        """
        Sign an arbitrary message using a raw private key (WIF).

        Invokes the `signmessagewithprivkey` RPC to produce a Base64-encoded signature
        over the provided message using the given private key. This does **not** require
        the key to be in the wallet (and does not require wallet unlock).

            signmessagewithprivkey "privkey" "message"

        Args:
            privkey (str):
                The private key in WIF format used to sign the message.
            message (str):
                The message to sign. The signature covers the exact bytes passed here.

        Returns:
            str:
                - On success: the Base64-encoded signature string.
                - If the node returns non-JSON text: that text verbatim.
                - If no output: "No data returned."
                - On error: "Error: <node stderr or exception message>"

        Security Notes:
            - **Do not** log or persist `privkey`. Keep it in memory only.
            - Prefer wallet-based `signmessage(address, message)` when possible to avoid
              handling raw private keys directly.

        Example:
            >>> rpc = UtilRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...               rpc_user="user", rpc_pass="pass", testnet=True)
            >>> sig = rpc.signmessagewithprivkey("L3...<WIF>...", "hello world")
        """
        # Build the CLI command with exact positional arguments.
        # IMPORTANT: Never print or log `privkey`.
        command = self._build_command() + [
            "signmessagewithprivkey",
            str(privkey),
            str(message),
        ]

        try:
            # Execute RPC; check=True raises on non-zero exit (stderr captured).
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize output (expected: a JSON string with the Base64 signature).
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Try JSON first (daemon often returns a JSON string).
            try:
                parsed = json.loads(out)
                # If it's a JSON string, return it; otherwise stringify for transparency.
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                # Not JSON—return raw text (may already be the Base64 signature).
                return out

        except Exception as e:
            # Standardized error: prefer daemon stderr, fallback to exception text.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def validateaddress(self, address):
        """
        Validate an Evrmore address and return detailed information about it.

        Invokes the `validateaddress` RPC, which checks whether the provided address
        is syntactically valid and (if known to the wallet) returns metadata such as
        ownership flags, script details, and the corresponding public key.

            validateaddress "address"

        Args:
            address (str):
                The Evrmore address to validate.

        Returns:
            dict | str:
                - On success (JSON expected), a dictionary with fields like:
                    - isvalid (bool): True if the address is syntactically valid.
                    - address (str): The validated Evrmore address.
                    - scriptPubKey (str): Hex-encoded scriptPubKey generated by the address.
                    - ismine (bool): True if this wallet controls the private key (if known).
                    - iswatchonly (bool): True if the address is watch-only.
                    - isscript (bool): True if the address corresponds to a script (P2SH, etc.).
                    - script (str, optional): Output script type; e.g., pubkeyhash, scripthash, multisig,
                      witness_v0_keyhash, witness_v0_scripthash, etc.
                    - hex (str, optional): Redeem script for P2SH addresses.
                    - addresses (list[str], optional): Addresses contained in a known redeem script (multisig).
                    - sigsrequired (int, optional): Required signatures for multisig.
                    - pubkey (str, optional): Hex public key (present if wallet knows it).
                    - iscompressed (bool, optional): Whether the pubkey/address is compressed.
                    - account (str, optional, DEPRECATED): Historical account label.
                    - timestamp (int, optional): Key creation time (Unix epoch seconds), if known.
                    - hdkeypath (str, optional): HD derivation path, if available.
                    - hdmasterkeyid (str, optional): Hash160 of the HD master pubkey, if available.
                  Note: If `isvalid` is False, the node typically returns only `isvalid: false`.
                - If non-JSON text is returned: that text verbatim.
                - If no output: "No data returned."
                - On error: "Error: <node stderr or exception message>"

        Notes:
            - The `pubkey` field appears only when the wallet actually knows the key
              (e.g., it generated or imported it). For external addresses, `pubkey`
              is generally unavailable until the address spends and reveals it on-chain.
            - For richer wallet-owned address details prefer `getaddressinfo` (if available).

        Example:
            >>> rpc = UtilRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...               rpc_user="user", rpc_pass="pass", testnet=True)
            >>> info = rpc.validateaddress("mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF")

        """
        # Build the CLI command with exact positional arguments.
        command = self._build_command() + [
            "validateaddress",
            str(address),
        ]

        try:
            # Execute the RPC; non-zero exit codes raise with stderr captured.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize output (daemon should return a JSON object).
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Parse JSON if possible; otherwise return the raw response text.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, dict) else str(parsed)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized, user-friendly error surface: prefer daemon stderr.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def verifymessage(self, address, signature, message):
        """
        Verify that a Base64 signature corresponds to a message and an address.

        Invokes the `verifymessage` RPC to check whether `signature` (Base64-encoded)
        is a valid signature over `message` produced by the private key controlling
        `address`.

            verifymessage "address" "signature" "message"

        Args:
            address (str):
                The Evrmore address that purportedly signed the message.
            signature (str):
                The Base64-encoded message signature (from `signmessage` or
                `signmessagewithprivkey`).
            message (str):
                The exact message that was signed.

        Returns:
            bool | str:
                - `True` if the signature verifies for the given address and message.
                - `False` if verification fails.
                - Raw text if the node returns non-JSON output.
                - "No data returned." if stdout is empty.
                - On error: "Error: <node stderr or exception message>"

        Notes:
            - The message must match **exactly** (same bytes) what the signer used.
            - The address must correspond to the public key that produced the signature.
            - Use `signmessage` (wallet-owned address) or `signmessagewithprivkey` (raw WIF).

        Example:
            >>> rpc = UtilRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...               rpc_user="user", rpc_pass="pass", testnet=True)
            >>> ok = rpc.verifymessage(
            ...     "mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF",
            ...     "H4b3...<Base64>...",
            ...     "hello world"
            ... )
        """
        # Build the CLI command with exact positional arguments.
        command = self._build_command() + [
            "verifymessage",
            str(address),
            str(signature),
            str(message),
        ]

        try:
            # Execute the RPC; non-zero exit raises with stderr captured.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()

            if not out:
                return "No data returned."

            # Try JSON first (some builds emit true/false as JSON).
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
                # Unexpected JSON type; stringify for transparency.
                return str(parsed)
            except json.JSONDecodeError:
                # Fallback for plain-text 'true'/'false'
                low = out.lower()
                if low == "true":
                    return True
                if low == "false":
                    return False
                return out

        except Exception as e:
            # Standardized error surface (prefer daemon stderr, fallback to exception text).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()
