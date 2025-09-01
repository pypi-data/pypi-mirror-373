from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json


class RawtransactionsRPC:

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

    def combinerawtransaction(self, txs):
        """
        Combine multiple partially-signed raw transactions into a single transaction.

        This method invokes the `combinerawtransaction` RPC, which merges signatures
        from several hex-encoded raw transactions that spend the same inputs. The
        result may be another partially-signed transaction or a fully-signed,
        broadcast-ready transaction.

        Args:
            txs (Sequence[str]):
                A list/tuple of hex-encoded raw transactions (strings). Each element
                must be a valid transaction hex that references the same inputs.

        Returns:
            str:
                The hex-encoded raw transaction (combined with any available
                signatures). On failure, returns an error message string in the form:
                `"Error: <message>"`.

        Example:
            >>> rpc = RawtransactionsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                          rpc_user="user", rpc_pass="pass", testnet=True)
            >>> combined = rpc.combinerawtransaction(["myhex1", "myhex2", "myhex3"])
        """
        # Basic client-side validation for a clearer error message before spawning the subprocess.
        # The RPC expects a JSON array of hex strings; empty input isn’t meaningful here.
        if not txs or not isinstance(txs, (list, tuple)):
            return "Error: 'txs' must be a non-empty list/tuple of hex strings"

        # Ensure all items are strings (hex). We coerce to str defensively.
        tx_list = [str(x) for x in txs]

        # The CLI expects the array as a single JSON argument: ["hex1","hex2",...]
        # Using json.dumps ensures proper quoting and escaping as one argv element.
        import json
        txs_arg = json.dumps(tx_list)

        # Build the command: <evrmore-cli ..flags..> combinerawtransaction '["hex1","hex2"]'
        command = self._build_command() + [
            "combinerawtransaction",
            txs_arg,
        ]

        try:
            from subprocess import run, PIPE
            # Execute the command; check=True raises an exception on non-zero exit status.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # RPC usually returns a JSON string (quoted hex). Some builds may output plain hex.
            out = (result.stdout or "").strip()

            # Try JSON first; if it's a JSON-encoded string, this yields Python str.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                # Not JSON? Return the raw stdout (likely plain hex).
                return out or "Success, but no hex returned."
        except Exception as e:
            # Standardized concise error format you requested.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def createrawtransaction(self, inputs, outputs, locktime=None, replaceable=None):
        """
        Create a hex-encoded **unsigned** raw transaction from explicit inputs and a
        flexible outputs object (EVR, data, asset ops, qualifier/tagging, restricted ops).

        This is a thin subprocess wrapper around:
            evrmore-cli createrawtransaction <inputs_json> <outputs_json> [locktime] [replaceable]

        Important behavior:
        - **No signing and no broadcast.** The resulting hex must be signed and then
          (optionally) broadcast by subsequent RPCs (`signrawtransaction*`, `sendrawtransaction`).
        - **Output ordering matters** for asset operations:
            1) All EVR “coin” outputs (including *burn* outputs) first
            2) Owner token *change* output next (when applicable)
            3) Asset operations (issue/reissue/transfer) last
          This function does **not** reorder; pass `outputs` in the correct order.
        - **Burn requirements** (Evrmore testnet burn addresses shown in help; amounts are per op):
            transfer: 0; transferwithmessage: 0; issue: 500; issue (subasset): 100; issue_unique: 5;
            reissue: 100; issue_restricted: 1500; reissue_restricted: 100; issue_qualifier: 1000;
            issue_qualifier (sub): 100; tag/untag addresses: 0.1 per address; freeze/unfreeze: 0.

        Args:
            inputs (list[dict]):
                List of UTXO inputs. Each element must include:
                  - ``txid`` (str): Funding transaction id.
                  - ``vout`` (int): Output index.
                  - ``sequence`` (int, optional): Explicit sequence (useful for RBF/locktime).
                Example::
                    [
                      {"txid": "abcd...1234", "vout": 0},
                      {"txid": "beef...cafe", "vout": 1, "sequence": 0xfffffffd}
                    ]

            outputs (dict):
                A JSON-like mapping describing where value and/or assets go. The keys can be:
                  - A **destination address** (str) whose value is:
                      * EVR amount (number or string), **or**
                      * An object describing an asset op:
                        - ``{"transfer": {"ASSET": raw_units, ...}}``
                        - ``{"transferwithmessage": {"ASSET": raw_units, "message": "ipfs_or_txid", "expire_time": utc}}``
                        - ``{"issue": {"asset_name": "...", "asset_quantity": n, "units": 1..8,
                                       "reissuable": 0/1, "has_ipfs": 0/1, "ipfs_hash": "..."}}``
                        - ``{"issue_unique": {"root_name": "...", "asset_tags": [...], "ipfs_hashes": [...]}}``
                        - ``{"reissue": {"asset_name": "...", "asset_quantity": n, "reissuable": 0/1,
                                          "ipfs_hash": "...", "owner_change_address": "..."}}``
                        - ``{"issue_restricted": {"asset_name": "$...", "asset_quantity": n, "verifier_string": "...",
                                                   "units": 0..8, "reissuable": 0/1, "has_ipfs": 0/1,
                                                   "ipfs_hash": "...", "owner_change_address": "..."}}``
                        - ``{"reissue_restricted": {"asset_name": "$...", "asset_quantity": n, "reissuable": 0/1,
                                                    "verifier_string": "...", "ipfs_hash": "...",
                                                    "owner_change_address": "..."}}``
                        - ``{"issue_qualifier": {"asset_name": "#...", "asset_quantity": 1..10 (default 1),
                                                  "has_ipfs": 0/1, "ipfs_hash": "...",
                                                  "root_change_address": "...", "change_quantity": n}}``
                        - ``{"tag_addresses": {"qualifier": "#...", "addresses": ["addr", ...<=10],
                                                "change_quantity": n}}``  (burn 0.1 EVR per address)
                        - ``{"untag_addresses": {"qualifier": "#...", "addresses": ["addr", ...<=10],
                                                  "change_quantity": n}}`` (burn 0.1 EVR per address)
                        - ``{"freeze_addresses": {"asset_name": "$...", "addresses": ["addr", ...<=10]}}``
                        - ``{"unfreeze_addresses": {"asset_name": "$...", "addresses": ["addr", ...<=10]}}``
                        - ``{"freeze_asset": {"asset_name": "$..."}}`` / ``{"unfreeze_asset": {"asset_name": "$..."}}``
                  - The literal key ``"data"`` with a hex string value to embed OP_RETURN data:
                        ``{"data": "00ab..."}``

                Notes:
                - Each **address key must be unique** in the dict (JSON object cannot repeat keys).
                  If you need multiple outputs to the same address, structure them via separate entries
                  going to different addresses or merge amounts as appropriate for your use-case.
                - EVR amounts may be numbers or strings. For safety with high precision you may
                  pass strings.

            locktime (int | None):
                Optional raw locktime (block height or UNIX time). Non-zero locktime also
                activates inputs with non-final sequences.

            replaceable (bool | None):
                Optional BIP125/RBF flag. Some Evrmore builds accept this 4th param; others
                ignore it. If provided, it is passed as JSON `true`/`false`.

        Returns:
            str:
                The hex-encoded raw transaction on success. If the node returns no stdout,
                returns a friendly message. On error, returns:
                    ``"Error: <stderr-or-exception-text>"``

        Examples:
            Basic EVR payment (no assets)::

                rpc = RawtransactionsRPC(cli_path="evrmore-cli", datadir="/evrmore",
                                         rpc_user="user", rpc_pass="pass", testnet=True)
                tx_hex = rpc.createrawtransaction(
                    inputs=[{"txid": "abcd...1234", "vout": 0}],
                    outputs={"n4iLx...GUtEv": "1.00000000"}
                )

            Issue a new (non-restricted) asset and include required burn output first::

                outs = {
                    "n1issueAssetXXXXXXXXXXXXXXXXWdnemQ": 500,  # burn output FIRST
                    "mzKoqP...m91vAF": 0.0001,                  # optional EVR change/fee output(s)
                    "issuerAddrHere": {
                        "issue": {
                            "asset_name": "MYASSET",
                            "asset_quantity": 1_000_000,
                            "units": 1,
                            "reissuable": 0,
                            "has_ipfs": 1,
                            "ipfs_hash": "43f81c...0797"
                        }
                    }
                }
                tx_hex = rpc.createrawtransaction(
                    inputs=[{"txid": "beef...cafe", "vout": 1}],
                    outputs=outs
                )

        """

        # Serialize inputs/outputs to compact JSON strings exactly as the CLI expects.
        # - separators=(',', ':') removes spaces.
        # - ensure_ascii=False preserves any non-ASCII (not typical here, but harmless).
        # - default=str allows Decimal or other simple non-JSON types to be stringified.
        def _jdumps(obj):
            return json.dumps(obj, separators=(",", ":"), ensure_ascii=False, default=str)

        # Validate minimal shapes early (helps catch obvious mistakes before the subprocess call).
        if not isinstance(inputs, list) or not all(isinstance(x, dict) for x in inputs):
            return "Error: 'inputs' must be a list of dicts with keys like txid/vout/sequence"
        if not isinstance(outputs, dict):
            return "Error: 'outputs' must be a dict mapping addresses (or 'data') to values/objects"

        command = self._build_command() + [
            "createrawtransaction",
            _jdumps(inputs),  # JSON array of inputs
            _jdumps(outputs),  # JSON object of outputs (EVR, data, asset operations)
        ]

        # Optional locktime (numeric). Cast to int then back to str for strict JSON numeric encoding.
        if locktime is not None:
            try:
                command.append(str(int(locktime)))
            except Exception:
                return "Error: locktime must be an integer-compatible value"

        # Optional replaceable (boolean). Some builds accept this 4th param. Emit JSON true/false.
        if replaceable is not None:
            command.append(str(bool(replaceable)).lower())

        try:
            # Run the CLI. On success, stdout contains the tx hex string.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            return out if out else "Could not create raw transaction."
        except Exception as e:
            # Standardized, concise error surface per your preference.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def decoderawtransaction(self, hexstring):
        """
        Decode a serialized raw transaction (hex) into a rich JSON-like dict.

        Thin wrapper around:
            evrmore-cli decoderawtransaction "<hexstring>"

        The decoded structure includes standard Bitcoin-style fields plus Evrmore
        asset extensions under each vout’s ``scriptPubKey.asset`` (e.g., asset
        name, amount, optional message/expire_time).

        Args:
            hexstring (str):
                Hex-encoded raw transaction to decode.

        Returns:
            dict | str:
                - On success: a Python dict parsed from the node’s JSON.
                - If the node returns non-JSON (unexpected): the raw stdout string.
                - On error: ``"Error: <stderr-or-exception-text>"``

        Example:
            >>> rpc = RawtransactionsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                          rpc_user="user", rpc_pass="pass", testnet=True)
            >>> decoded = rpc.decoderawtransaction("02000000...")
        """
        # Build the CLI command.
        command = self._build_command() + [
            "decoderawtransaction",
            str(hexstring),
        ]

        try:
            # Execute the command; capture stdout/stderr.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()

            # Try to parse JSON. If it fails, return the raw text for transparency.
            try:
                return json.loads(out) if out else {}
            except json.JSONDecodeError:
                return out or "Success, but no content returned."
        except Exception as e:
            # Your preferred concise error format.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def decodescript(self, hexstring):
        """
        Decode a hex-encoded script (scriptPubKey or redeemscript) into a structured dict.

        Wraps:
            evrmore-cli decodescript "<hexstring>"

        The decoded result includes standard script fields (asm, hex, type, reqSigs, addresses, p2sh)
        and, when applicable, Evrmore asset metadata (under ``asset`` and/or top-level asset fields).

        Args:
            hexstring (str):
                Hex-encoded script to decode.

        Returns:
            dict | str:
                - On success: a Python dict parsed from the node’s JSON (keys like
                  "asm", "hex", "type", "reqSigs", "addresses", "p2sh", and optional "asset" object).
                - If the node returns non-JSON (unexpected): the raw stdout string.
                - On error: ``"Error: <stderr-or-exception-text>"``.

        Example:
            >>> rpc = RawtransactionsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                          rpc_user="user", rpc_pass="pass", testnet=True)
            >>> decoded = rpc.decodescript("0014d85a...")
        """
        # Build CLI command: network/auth flags + RPC method + required arg.
        command = self._build_command() + [
            "decodescript",
            str(hexstring),
        ]

        try:
            # Run the command and capture output.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()

            # Try parsing the JSON response; fall back to raw text if it isn't JSON.
            try:
                return json.loads(out) if out else {}
            except json.JSONDecodeError:
                return out or "Success, but no content returned."
        except Exception as e:
            # Standardized, concise error surface per your preference.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def fundrawtransaction(
            self,
            hexstring,
            *,
            change_address=None,
            change_position=None,
            include_watching=None,
            lock_unspents=None,
            fee_rate=None,
            subtract_fee_from_outputs=None,
            conf_target=None,
            estimate_mode=None,
            include_watching_compat=False,
    ):
        """
        Add inputs and (optionally) a change output to a raw transaction until its
        input value covers all outputs + fee. Returns a funded (still unsigned) tx.

        Wraps:
            evrmore-cli fundrawtransaction "<hexstring>" (<options object or true>)

        Notes:
          - Existing inputs are not altered; at most one change output is added.
          - No signing is performed; use `signrawtransaction` afterwards.
          - For backward-compatibility you may pass a bare `true` instead of an
            options object to enable `"includeWatching": true` (set `include_watching_compat=True`).

        Args:
            hexstring (str):
                Hex-encoded raw transaction to fund (created by `createrawtransaction`).
            change_address (str | None):
                Specific address to receive change. If omitted, wallet chooses.
            change_position (int | None):
                Zero-based vout index for the change output (random if omitted).
            include_watching (bool | None):
                If True, allows watch-only UTXOs to be selected (requires solvable scripts).
            lock_unspents (bool | None):
                If True, locks selected UTXOs so they aren't auto-selected by future sends.
            fee_rate (float | int | str | None):
                Feerate in EVR/kB. If omitted, wallet’s estimator is used.
            subtract_fee_from_outputs (list[int] | None):
                Zero-based indices (relative to *current* outputs before change) whose
                amounts should have the fee deducted equally.
            conf_target (int | None):
                Target confirmation time in blocks for fee estimation.
            estimate_mode (str | None):
                Fee estimation mode: "UNSET", "ECONOMICAL", or "CONSERVATIVE".
            include_watching_compat (bool):
                If True, passes a bare `true` as the second param (legacy behavior).
                When set, all other options are ignored.

        Returns:
            dict | str:
                - On success: dict with keys:
                    {"hex": <funded_tx_hex>, "fee": <fee_evr>, "changepos": <int_or_-1>}
                - If node emits unexpected non-JSON: raw stdout string.
                - On error: "Error: <stderr-or-exception-text>".

        Example:
            >>> rpc = RawtransactionsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                          rpc_user="user", rpc_pass="pass", testnet=True)
            >>> funded = rpc.fundrawtransaction(
            ...     "020000000001...",  # tx hex from createrawtransaction
            ...     change_address="mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF",
            ...     subtract_fee_from_outputs=[0],
            ... )
        """
        # Build the base CLI command.
        command = self._build_command() + ["fundrawtransaction", str(hexstring)]

        # If the caller explicitly wants the legacy bare `true`, append it and skip options.
        if include_watching_compat:
            command.append("true")
        else:
            # Construct the options object, including only keys that were provided.
            options = {}
            if change_address is not None:
                options["changeAddress"] = str(change_address)
            if change_position is not None:
                options["changePosition"] = int(change_position)
            if include_watching is not None:
                options["includeWatching"] = bool(include_watching)
            if lock_unspents is not None:
                options["lockUnspents"] = bool(lock_unspents)
            if fee_rate is not None:
                # Let json handle numeric/str; caller may pass float/int/decimal-as-str.
                options["feeRate"] = fee_rate
            if subtract_fee_from_outputs is not None:
                # Ensure it’s a list of ints; raise early if garbage sneaks in.
                try:
                    options["subtractFeeFromOutputs"] = [int(i) for i in subtract_fee_from_outputs]
                except Exception:
                    return "Error: subtract_fee_from_outputs must be a list of integers"
            if conf_target is not None:
                options["conf_target"] = int(conf_target)
            if estimate_mode is not None:
                options["estimate_mode"] = str(estimate_mode)

            # Append the options object only if at least one option is present.
            if options:
                command.append(json.dumps(options))

        try:
            # Execute the command. If it fails, `check=True` raises a CalledProcessError.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()

            # Parse JSON result: {"hex": "...", "fee": n, "changepos": n}
            try:
                return json.loads(out) if out else {}
            except json.JSONDecodeError:
                # Fallback: node returned non-JSON; surface raw output.
                return out or "Success, but no content returned."
        except Exception as e:
            # Standardized error message per your preference.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getrawtransaction(self, txid, verbose=False):
        """
        Fetch a raw transaction by txid.

        Wraps:
            evrmore-cli getrawtransaction "<txid>" (verbose)

        Behavior:
          - If `verbose` is False or omitted: returns the serialized hex string.
          - If `verbose` is True: returns a JSON object (dict) describing the tx.

        Important:
          By default, nodes return results only for mempool transactions.
          To fetch confirmed (on-chain) txs, start the node with `-txindex=1`
          or ensure the transaction has unspent outputs known to the wallet.

        Args:
            txid (str):
                The transaction id (hex).
            verbose (bool):
                When True, return a parsed JSON object. When False, return hex.

        Returns:
            str | dict:
                - If verbose=False → hex string (serialized tx).
                - If verbose=True  → dict with fields like hex, txid, vin, vout, etc.
                - If node returns unexpected non-JSON when verbose=True, the raw text.
                - On error, a string: "Error: <stderr-or-exception-text>".

        Example:
            >>> rpc = RawtransactionsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                          rpc_user="user", rpc_pass="pass", testnet=True)
            >>> tx_hex = rpc.getrawtransaction("e3...deadbeef")      # non-verbose
            >>> tx_obj = rpc.getrawtransaction("e3...deadbeef", True)  # verbose
        """
        # Base command + RPC name + required txid.
        command = self._build_command() + ["getrawtransaction", str(txid)]

        # Append the optional verbose flag only if explicitly provided.
        # The CLI expects JSON booleans; passing "true"/"false" as separate args is fine.
        if verbose is True:
            command.append("true")
        elif verbose is False:
            # Omit argument to use default false, OR pass explicit "false"—both are acceptable.
            # We'll omit it to mimic the default behavior.
            pass

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()

            if verbose:
                # Verbose should be JSON. Try to parse, but surface raw text if decode fails.
                try:
                    return json.loads(out) if out else {}
                except json.JSONDecodeError:
                    return out or "Success, but no content returned."
            else:
                # Non-verbose: raw hex string.
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def sendrawtransaction(self, hexstring, allowhighfees=False):
        """
        Broadcast a signed raw transaction to the node and network.

        Wraps:
            evrmore-cli sendrawtransaction "<hexstring>" (allowhighfees)

        Args:
            hexstring (str):
                The serialized transaction in hex (signed).
            allowhighfees (bool):
                If True, bypasses the wallet’s high-fee checks. Defaults to False.

        Returns:
            str:
                - On success: the transaction id (hex string).
                - On failure: "Error: <stderr-or-exception-text>".

        Notes:
            - Ensure the tx is fully signed (use signrawtransaction beforehand).
            - Nodes may reject for policy reasons (e.g., fee, dust, non-final, missing inputs).
              Those details appear in the returned error string.

        Example:
            >>> rpc = RawtransactionsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                          rpc_user="user", rpc_pass="pass", testnet=True)
            >>> txid = rpc.sendrawtransaction("02000000...signedhex...")
        """
        # Base command + RPC name + required tx hex
        command = self._build_command() + ["sendrawtransaction", str(hexstring)]

        # Only append the optional boolean if True; omitting keeps default False.
        if allowhighfees:
            command.append("true")

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            txid = (result.stdout or "").strip()
            return txid or "Could not broadcast transaction."
        except Exception as e:
            # Standardized, user-friendly error surface
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def signrawtransaction(self, hexstring, prevtxs=None, privkeys=None, sighashtype=None):
        """
        Sign inputs for a raw (hex-encoded) transaction.

        Wraps:
            evrmore-cli signrawtransaction "<hex>" (prevtxs) (privkeys) (sighashtype)

        Args:
            hexstring (str):
                The unsigned or partially signed transaction hex.
            prevtxs (list[dict] | None):
                Optional list of UTXO metadata for inputs that may not be known to the node.
                Each dict typically includes:
                    {
                      "txid": "<hex>",        # required
                      "vout": <int>,          # required
                      "scriptPubKey": "<hex>",# required
                      "redeemScript": "<hex>",# required for P2SH/P2WSH
                      "amount": <float>       # required (EVR)
                    }
                If you need to pass this but have no entries, use an empty list [].
            privkeys (list[str] | None):
                Optional list of base58-encoded WIF private keys to use exclusively for signing.
                If omitted, the wallet’s keys will be used where available.
            sighashtype (str | None):
                Signature hash type. One of:
                "ALL", "NONE", "SINGLE", "ALL|ANYONECANPAY",
                "NONE|ANYONECANPAY", "SINGLE|ANYONECANPAY".
                If provided while omitting prevtxs/privkeys, placeholders are added to keep
                positional parameters aligned.

        Returns:
            dict | str:
                - On success: a dict like:
                  {
                    "hex": "<signed-hex>",
                    "complete": true/false,
                    "errors": [ ...optional script errors... ]
                  }
                - On failure: "Error: <stderr-or-exception-text>".

        Notes:
            - If you only pass `hexstring`, the node will try to sign using wallet keys it controls.
            - When providing `sighashtype` but not `prevtxs`/`privkeys`, this method inserts `[]`
              placeholders so the CLI receives the correct argument positions.

        Example:
            >>> rpc = RawtransactionsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                          rpc_user="user", rpc_pass="pass", testnet=True)
            >>> res = rpc.signrawtransaction("02000000...hex...")
            >>> signed_hex = res.get("hex") if isinstance(res, dict) else None
        """
        import json
        from subprocess import run, PIPE

        # Start with the required parameters.
        command = self._build_command() + ["signrawtransaction", str(hexstring)]

        # Decide which optional parameters to append, keeping POSITIONS correct.
        append_prev = prevtxs is not None
        append_priv = privkeys is not None
        append_sighash = sighashtype is not None

        # If we need to pass privkeys or sighashtype but not prevtxs, we must add a placeholder for prevtxs.
        if append_prev:
            # If user passed a Python list/dict, serialize to JSON.
            # (If they accidentally passed a string, just pass it through.)
            if isinstance(prevtxs, (list, dict)):
                command.append(json.dumps(prevtxs))
            else:
                command.append(str(prevtxs))
        elif append_priv or append_sighash:
            command.append("[]")  # placeholder for prevtxs

        # Similarly handle privkeys and its placeholder if sighashtype is provided.
        if append_priv:
            if isinstance(privkeys, list):
                command.append(json.dumps(privkeys))
            else:
                command.append(str(privkeys))
        elif append_sighash:
            command.append("[]")  # placeholder for privkeys

        # Finally, the sighashtype if supplied.
        if append_sighash:
            command.append(str(sighashtype))

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()

            # The RPC returns a JSON object on success.
            try:
                return json.loads(out) if out else {"hex": "", "complete": False, "errors": []}
            except Exception:
                # If node returns non-JSON (unlikely here), surface the raw output.
                return out or "Success, but no JSON result returned."
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def testmempoolaccept(self, rawtxs, allowhighfees=None):
        """
        Check if a raw transaction would be accepted into the mempool.

        Wraps:
            evrmore-cli testmempoolaccept ["rawtxs"] (allowhighfees)

        Args:
            rawtxs (str | list[str]):
                A single hex string or a list of hex strings (the node currently
                expects a single tx; list length must be 1 for now).
            allowhighfees (bool | None):
                If True, allow high fees. If False, disallow. If None, omit the
                flag to use the node’s default (false).

        Returns:
            list | str:
                - On success: a list with one result object, e.g.
                  [
                    {
                      "txid": "<hex>",
                      "allowed": true/false,
                      "reject-reason": "<string, if not allowed>"
                    }
                  ]
                - On failure: "Error: <stderr-or-exception-text>".

        Notes:
            - We always pass the transactions as a JSON array to match the RPC spec.
            - If you provide multiple tx hex strings, the node will likely return an
              error (current implementations accept exactly one).
        """
        import json
        from subprocess import run, PIPE

        # Normalize input to a list of hex strings
        if isinstance(rawtxs, str):
            tx_list = [rawtxs]
        else:
            tx_list = list(rawtxs or [])

        command = self._build_command() + [
            "testmempoolaccept",
            json.dumps(tx_list)
        ]

        # Only append the optional boolean when explicitly provided
        if allowhighfees is not None:
            command.append("true" if allowhighfees else "false")

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            return json.loads(out) if out else []
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()
