from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json



class RestrictedassetsRPC:

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

    def addtagtoaddress(self, tag_name, to_address, change_address=None, asset_data=None):
        """
        Assigns a qualifier tag to a specific Evrmore address.

        This method invokes the `addtagtoaddress` RPC, which transfers a qualifier tag (implemented
        as a qualifier asset, typically starting with `#`) to the target address. If the provided
        tag name does not begin with `#`, the node will automatically prefix it.

        Mirrors native help:

            addtagtoaddress tag_name to_address (change_address) (asset_data)

            1. "tag_name"       (string, required) the name of the tag you are assigning to the address;
                                 if it doesn't have '#' at the front it will be added
            2. "to_address"     (string, required) the address that will be assigned the tag
            3. "change_address" (string, optional) the change address for the qualifier token to be sent to
            4. "asset_data"     (string, optional) IPFS or other hash applied to the transfer of the qualifier token

        Args:
            tag_name (str):
                The qualifier tag to assign (e.g., "#KYC"). If missing the `#`, the node adds it automatically.
            to_address (str):
                The Evrmore address that will receive the tag.
            change_address (str, optional):
                Address to receive change for the qualifier-token transfer. Pass `""` to let the node choose,
                or `None` to omit the parameter entirely (no placeholder sent).
            asset_data (str, optional):
                Optional metadata to attach (IPFS hash or other string). Pass `""` to set empty metadata explicitly,
                or `None` to omit the parameter entirely.

        Returns:
            str:
                On success, returns the transaction ID (`txid`) as a string. If the RPC ever returns a list of
                TXIDs, they are joined into a comma-separated string. If output is empty or non-JSON, a descriptive
                string is returned. On error, returns `"Error: <message>"`.

        Notes:
            - Tags are qualifier assets and typically start with `#` (the node will enforce the prefix).
            - The argument order is positional: `(change_address)` comes **before** `(asset_data)`.
              If you want to pass only `asset_data`, you must still occupy the `(change_address)` slot (we do this
              by inserting `""` automatically when `change_address is None` and `asset_data is not None`).

        Example:
            Assign a tag, letting the node pick the change address and with no metadata:

            >>> rpc = RestrictedassetsRPC(cli_path="evrmore-cli", datadir="/evrmore",rpc_user="user", rpc_pass="pass", testnet=True)
            >>> txid = rpc.addtagtoaddress("#KYC", "mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF")
        """

        # Start with required arguments in the exact order expected by the node.
        args = [
            "addtagtoaddress",
            str(tag_name),  # Tag name; node will add '#' if missing
            str(to_address),  # Recipient address for the tag
        ]

        # Maintain positional correctness for optional args.
        # Use `is not None` so empty strings "" are treated as intentional values.
        if change_address is not None or asset_data is not None:
            # Append the change_address slot (empty string if not provided but asset_data is provided).
            args.append("" if change_address is None else str(change_address))

        if asset_data is not None:
            # Append asset_data only when the caller provided it (None means omit entirely).
            args.append(str(asset_data))

        # Build final command with auth/network flags + RPC + args.
        command = self._build_command() + args

        try:
            # Execute the CLI command and capture stdout/stderr.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()

            if not out:
                return "Could not add tag to address."

            # Try to parse JSON (expected: a single txid string).
            try:
                parsed = json.loads(out)
                if isinstance(parsed, list):
                    return ", ".join(map(str, parsed))
                return str(parsed)
            except json.JSONDecodeError:
                # If it's not JSON, just return the raw output (some nodes emit plain text).
                return out


        except Exception as e:
            # Standardized error surface (prefer daemon stderr, fallback to exception text).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()



    def checkaddressrestriction(self, address, restricted_name):
        """
        Checks whether an address is **frozen** for a given restricted asset.

        Invokes the `checkaddressrestriction` RPC to determine if transfers of the
        specified restricted asset are disallowed for the given address.

        Args:
            address (str): The Evrmore address to check.
            restricted_name (str): The restricted asset name (e.g., "$SECURITY").

        Returns:
            bool | str:
                - `True` if the address is frozen for this restricted asset.
                - `False` if not frozen.
                - On unexpected output or failure to parse, returns the raw output string.
                - On error, returns `"Error: <message>"`.

        Example:
            >>> rpc = RestrictedassetsRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> result = rpc.checkaddressrestriction("mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF", "$SECURITY")
        """

        # Build the CLI command with required arguments only.
        command = self._build_command() + [
            "checkaddressrestriction",
            str(address),
            str(restricted_name),
        ]

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()

            # Try JSON first (node often emits true/false as JSON).
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
                return str(parsed)
            except json.JSONDecodeError:
                # Fall back to plain text "true"/"false".
                low = out.lower()
                if low == "true":
                    return True
                if low == "false":
                    return False
                return out or "Success, but no boolean result returned."
        except Exception as e:
            # Standardized error surface (prefer daemon stderr, fallback to exception text).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def checkaddresstag(self, address, tag_name):
        """
        Checks whether an address currently holds a specific qualifier tag.

        This method invokes the `checkaddresstag` RPC, which returns a boolean indicating
        whether the provided Evrmore address has been assigned the given tag (e.g., "#KYC").
        Tags are implemented as qualifier assets; they typically start with '#'. For clarity
        and consistency, pass the canonical tag form (e.g., "#KYC" rather than "KYC").

        Args:
            address (str):
                The Evrmore address to check (e.g., "mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF").
            tag_name (str):
                The tag to search for (e.g., "#KYC"). If a caller omits '#', node-side logic
                elsewhere often normalizes tags, but docstrings/examples assume canonical form.

        Returns:
            bool | str:
                - `True`  → the address **has** the tag.
                - `False` → the address **does not have** the tag.
                - If the node returns unexpected non-JSON output, the raw string is returned.
                - On error, returns a string of the form `"Error: <message>"`.

        Example:
            >>> rpc = RestrictedassetsRPC(cli_path="evrmore-cli", datadir="/evrmore",rpc_user="user", rpc_pass="pass", testnet=True)
            >>> has_tag = rpc.checkaddresstag("mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF", "#KYC")
        """

        # Build the base Evrmore CLI command with authentication/network options, then append
        # the RPC name and its required arguments in the exact order expected by the node.
        # NOTE: We cast to str to ensure robust joining/serialization into the subprocess call.
        command = self._build_command() + [
            "checkaddresstag",
            str(address),  # EVR address to check
            str(tag_name),  # Qualifier tag to look for (canonical form recommended, e.g., "#KYC")
        ]

        try:
            # Execute the command as a subprocess. `check=True` raises CalledProcessError on nonzero exit.
            # We request text output so stdout/stderr are str rather than bytes.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout; guard against None and trim whitespace/newlines.
            out = (result.stdout or "").strip()

            # First attempt: parse as JSON. Many RPCs return JSON booleans (`true`/`false`),
            # which `json.loads` converts directly to Python True/False.
            try:
                parsed = json.loads(out)

                # If the node emitted a proper JSON boolean, return it directly.
                if isinstance(parsed, bool):
                    return parsed

                # Some nodes/layers occasionally return JSON strings "true"/"false";
                # coerce those to booleans if encountered. Otherwise, return as string.
                if isinstance(parsed, str):
                    low = parsed.strip().lower()
                    if low == "true":
                        return True
                    if low == "false":
                        return False
                return str(parsed)

            except json.JSONDecodeError:
                # Fallback: handle plain text responses like 'true' or 'false' (non-JSON).
                low = out.lower()
                if low == "true":
                    return True
                if low == "false":
                    return False

                # If the node returned an empty string or an unexpected payload,
                # surface something informative rather than masking the response.
                return out or "Success, but no boolean result returned."

        except Exception as e:
            # Standardized error surface (prefer daemon stderr, fallback to exception text).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def checkglobalrestriction(self, restricted_name):
        """
        Checks whether a restricted asset is **globally frozen**.

        Invokes the `checkglobalrestriction` RPC to determine if *all transfers* of the specified
        restricted asset are currently disallowed (i.e., the asset is globally frozen, independent
        of any per-address restrictions).

        Args:
            restricted_name (str):
                The restricted asset name to query (canonical form recommended, e.g., "$SECURITY").
                Restricted asset names begin with '$'; the node typically enforces/normalizes this at
                issuance time, but pass the canonical name for lookups.

        Returns:
            bool | str:
                - `True`  → the restricted asset **is** globally frozen.
                - `False` → the restricted asset is **not** globally frozen.
                - If unexpected (non-JSON) output is returned, the raw string is surfaced.
                - On error, returns a string of the form `"Error: <message>"`.

        Example:
            >>> rpc = RestrictedassetsRPC(cli_path="evrmore-cli", datadir="/evrmore",rpc_user="user", rpc_pass="pass", testnet=True)
            >>> is_global = rpc.checkglobalrestriction("$SECURITY")

        """

        # Construct the CLI command with network/auth flags and the RPC name + required arg.
        # We cast to str to ensure safe joining/serialization in the subprocess invocation.
        command = self._build_command() + [
            "checkglobalrestriction",
            str(restricted_name),  # The restricted asset to query, e.g., "$SECURITY"
        ]

        try:
            # Execute the command; check=True raises on non-zero exit codes.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize stdout to a stripped string for parsing.
            out = (result.stdout or "").strip()

            # Attempt JSON parsing first. If the node emits proper JSON booleans,
            # json.loads will produce Python True/False directly.
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
                return str(parsed)  # Unrecognized JSON type; return as string for transparency.
            except json.JSONDecodeError:
                # Fallback for plain-text 'true'/'false' responses.
                low = out.lower()
                if low == "true":
                    return True
                if low == "false":
                    return False
                return out or "Success, but no boolean result returned."

        except Exception as e:
            # Standardized error surface (prefer daemon stderr, fallback to exception text).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def freezeaddress(self, asset_name, address, change_address=None, asset_data=None):
        """
        Freezes a specific address from transferring a restricted asset.

        Invokes the `freezeaddress` RPC to prevent the given `address` from transferring
        the specified restricted asset. This action is performed with the asset’s **owner
        token**, so you may optionally specify a `change_address` for that owner token
        change output, and attach `asset_data` (e.g., IPFS hash) to the owner-token
        transfer metadata.

        Args:
            asset_name (str):
                The restricted asset name to enforce (canonical form recommended, e.g., "$SECURITY").
            address (str):
                The Evrmore address to freeze (it will no longer be able to transfer `asset_name`).
            change_address (str, optional):
                The change address for the **owner token** of the restricted asset. Pass `""` or leave
                as `None` to let the node choose a change address automatically.
            asset_data (str, optional):
                Optional metadata (e.g., IPFS or other hash) to attach to the owner-token transfer.
                Pass `""` or leave as `None` if not needed.

        Returns:
            str:
                On success, returns the transaction ID (`txid`) as a string. If the RPC returns a list
                of txids (unlikely), they are joined into a comma-separated string.
                On unexpected or empty output, returns a descriptive string.
                On error, returns `"Error: <message>"`.

        Notes:
            - This freezes *per-address*. It does **not** globally freeze the asset; use
              `checkglobalrestriction` / global freeze RPCs for asset-wide status/actions.
            - `asset_name` should be a restricted asset (starts with `$`).

        Example:
            >>> rpc = RestrictedassetsRPC(cli_path="evrmore-cli", datadir="/evrmore",rpc_user="user", rpc_pass="pass", testnet=True)
            >>> txid = rpc.freezeaddress("$SECURITY", "mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF")
        """

        # Build the Evrmore CLI command with base auth/network flags, the RPC name,
        # and required arguments in the exact order expected by the node.
        command = self._build_command() + [
            "freezeaddress",
            str(asset_name),  # Restricted asset to enforce (e.g., "$SECURITY")
            str(address),  # Address to be frozen
        ]

        # Append optional arguments ONLY if provided, to mirror native CLI semantics.
        if change_address is not None:
            command.append(str(change_address))  # Owner-token change address or ""
        if asset_data is not None:
            command.append(str(asset_data))  # Optional metadata/IPFS hash or ""

        try:
            # Execute the command and capture stdout/stderr. check=True -> raises on nonzero exit code.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()

            if not out:
                # Node returned no output; surface something informative.
                return "Could not freeze address."

            # RPCs commonly emit JSON. Attempt to parse:
            try:
                parsed = json.loads(out)
            except json.JSONDecodeError:
                # Fallback: return raw string as-is if not valid JSON.
                return out

            # Expected: a single txid string. If a list arrives, join defensively.
            if isinstance(parsed, list):
                return ", ".join(map(str, parsed))
            return str(parsed)

        except Exception as e:
            # Standardized error surface (prefer daemon stderr, fallback to exception text).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def freezerestrictedasset(self, asset_name, change_address=None, asset_data=None):
        """
        Freeze all transfers for a specific *restricted asset* (global freeze).

        Invokes the `freezerestrictedasset` RPC to globally freeze trading of the given
        restricted asset. After a successful call, **all** transfers of that asset are
        blocked until explicitly un-frozen (via the corresponding unfreeze call).

            freezerestrictedasset asset_name (change_address) (asset_data)

        Args:
            asset_name (str):
                The restricted asset to freeze (canonical form recommended, e.g., "$ASSET").
                If '$' is omitted, the node may normalize/require it depending on policy.
            change_address (str, optional):
                Destination for any owner-token change. Pass "" to let the node pick one.
                Omit or pass None to exclude this argument entirely.
            asset_data (str, optional):
                Optional metadata (IPFS hash or arbitrary string) to attach to the owner
                token transfer. Pass "" if unused, or omit/None to exclude.

        Returns:
            str:
                - On success: the transaction ID (txid) as a string.
                - If the node returns JSON (rare for this call), the parsed value is
                  converted to string (lists joined with commas).
                - "No data returned." if stdout is empty.
                - On error: "Error: <node stderr or exception message>"

        Notes:
            - This operation requires ownership (the *owner token*) of the restricted asset.
            - Use the matching unfreeze RPC to lift the global freeze later.
            - If you pass `""` for optional args, they are forwarded literally; passing
              `None` omits them from the CLI argument list.

        Example:
            >>> rpc = RestrictedassetsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                           rpc_user="user", rpc_pass="pass", testnet=True)
            >>> txid = rpc.freezerestrictedasset("$MY_RESTRICTED", "", "")
        """
        # --- Build the CLI command in exact positional order ----------------------
        command = self._build_command() + [
            "freezerestrictedasset",
            str(asset_name),  # Restricted asset to freeze, e.g., "$ASSET"
        ]

        # Append optional args only when the caller provided them (None means omit).
        if change_address is not None:
            command.append(str(change_address))  # "" lets the node choose a change address
        if asset_data is not None:
            command.append(str(asset_data))  # "" if unused

        try:
            # Execute RPC; non-zero exit raises with stderr captured by Python.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Try JSON first (defensive). If it's a bare string/array, normalize to str.
            try:
                parsed = json.loads(out)
                if isinstance(parsed, list):
                    return ", ".join(map(str, parsed))
                return str(parsed)
            except json.JSONDecodeError:
                # Typical path: daemon prints a bare txid string (no JSON).
                return out

        except Exception as e:
            # Standardized error message preferred for user surfacing.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getverifierstring(self, restricted_name):
        """
        Retrieve the verifier string for a restricted asset.

        Invokes the `getverifierstring` RPC to fetch the verifier expression associated
        with a given restricted asset. The verifier string encodes the logical/tag
        requirements (e.g., `#KYC & !#SANCTIONED`) that must be satisfied for transfers.

            getverifierstring restricted_name

        Args:
            restricted_name (str):
                The restricted asset name (canonical form recommended, e.g., "$ASSET").
                If the leading '$' is omitted, the node may normalize/require it
                depending on policy.

        Returns:
            str:
                - On success: the verifier string (e.g., `#KYC & !#AML`).
                - If the node emits JSON, the parsed value is coerced to string.
                - "No data returned." if stdout is empty.
                - On error: "Error: <node stderr or exception message>"

        Notes:
            - The verifier string defines *who can receive or send* the asset by using
              tags/qualifiers and boolean operators.
            - Use `setverifier` (if available in your build) or reissuance controls to
              change a verifier on assets that allow it.

        Example:
            >>> rpc = RestrictedassetsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                           rpc_user="user", rpc_pass="pass", testnet=True)
            >>> verifier = rpc.getverifierstring("$MY_RESTRICTED")
        """
        # Build the CLI command. Keep arguments positional and cast to str for safety.
        command = self._build_command() + [
            "getverifierstring",
            str(restricted_name),  # e.g., "$MY_RESTRICTED"
        ]

        try:
            # Execute the RPC; non-zero exit codes raise an exception with stderr attached.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize/strip the output first (many nodes return a bare string).
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Try to parse JSON in case the daemon wraps the result as a JSON string.
            try:
                parsed = json.loads(out)
                # If it's already a string, return directly; otherwise stringify.
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                # Not JSON—return the raw text (likely already the verifier string).
                return out

        except Exception as e:
            # Standardized error surfacing preferred for user-facing error messages.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def issuequalifierasset(self, asset_name, qty, to_address, change_address, has_ipfs,
                            ipfs_hash, permanent_ipfs_hash):
        """
        Issues a qualifier (or sub-qualifier) asset on the Evrmore blockchain.

        This method invokes the `issuequalifierasset` RPC to create a new **qualifier** asset,
        automatically enforcing qualifier semantics:
          - If the asset name is missing a leading '#', it will be **prefixed automatically**.
          - **Units** are always fixed at **0** (non-divisible).
          - **Reissuable** is always **false** (qualifier assets cannot be reissued).
          - **Quantity (`qty`) must be an integer in [1, 10]**.  (Note: some native help examples
            show larger values like 1000, but the accepted range is **1–10** for qualifier assets.)

        Although the underlying RPC treats many arguments as optional, this wrapper requires explicit
        values for all parameters to make intent unambiguous. Pass empty strings (`""`) or `False`
        for fields that you do not wish to set.

        Args:
            asset_name (str):
                The unique asset name to issue. If it does not begin with `#`, the RPC will
                automatically add it (e.g., `KYC` becomes `#KYC`).
            qty (int):
                Number of units to issue, **1–10 inclusive**.
            to_address (str):
                The recipient address for the issued asset. Pass `""` to let the node generate
                a new address automatically.
            change_address (str):
                The address to receive any Evr change. Pass `""` to let the node choose a change
                address automatically.
            has_ipfs (bool):
                Whether to attach an IPFS (or RIP-5 txid) hash to the asset’s metadata.
            ipfs_hash (str):
                The IPFS hash (or txid hash once RIP-5 is active). **Required if** `has_ipfs` is `True`.
                Otherwise pass `""`.
            permanent_ipfs_hash (str):
                An optional “permanent” IPFS hash for the asset. Pass `""` if not used.

        Returns:
            str:
                On success, returns the transaction ID (`txid`) as a string. If the RPC returns a list
                of TXIDs (rare), they will be joined into a comma-separated string.
                On failure, a string describing the error is returned (including the attempted command
                and any stderr captured, when available).

        Notes:
            - **Qualifier invariants**: units=0, reissuable=false, and `#` prefix is enforced by the node.
            - **Quantity**: must be **1 ≤ qty ≤ 10** for qualifier assets.
            - **IPFS**: If `has_ipfs=True`, `ipfs_hash` must be a non-empty string.

        Example:
            Issue a qualifier with no IPFS and auto-generated addresses:

            >>> rpc = RestrictedassetsRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> txid = rpc.issuequalifierasset("ACCREDITED", 3, "mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF", "", True, "QmTqu3Lk3gmTsQVtjU7rYYM37EAW4xNmbuEAp2Mjr4AV7E", "")
        """

        # Build the Evrmore CLI command with network/auth options, then append the RPC.
        # NOTE: Although the RPC has optional params, we pass all explicitly to preserve clarity.
        command = self._build_command() + [
            "issuequalifierasset",
            str(asset_name),  # Asset name; node will auto-prefix '#' if missing
            str(qty),  # Quantity; must be an integer in [1, 10]
            str(to_address),  # Recipient address, or "" to auto-generate
            str(change_address),  # Change address for EVR, or "" to auto-select
            str(has_ipfs).lower(),  # JSON-RPC expects `true`/`false` (lowercase)
            str(ipfs_hash),  # Required if has_ipfs=True; else pass ""
            str(permanent_ipfs_hash)  # Optional permanent IPFS hash; pass "" if unused
        ]

        try:
            # Execute the command and capture output (stdout/stderr) from the subprocess.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                # RPCs typically return a JSON string or array; try decoding.
                # For this RPC, the expected result is a single "txid" string.
                txids = json.loads(result.stdout.strip())

                if isinstance(txids, list):
                    # Defensive: if a list arrives, join for a consistent string return type.
                    return ", ".join(txids)
                else:
                    # Standard case: a single txid string.
                    return str(txids)
            else:
                # No data returned (unexpected on success).
                return "Could not issue qualifier asset."
        except Exception as e:
            # Standardized error surface (prefer daemon stderr, fallback to exception text).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def issuerestrictedasset(self, asset_name, qty, verifier, to_address, change_address=None, units=None,
                             reissuable=None, has_ipfs=None, ipfs_hash=None, permanent_ipfs_hash=None,
                             toll_amount=None, toll_address=None,
                             toll_amount_mutability=None, toll_address_mutability=None, remintable=None):
        """
        Issues a restricted asset on the Evrmore blockchain.

        Restricted assets differ from normal or qualifier assets in that they are bound by a **verifier string**
        that controls who can send/receive the asset. They are typically used for compliance-driven tokens
        (e.g., requiring a `#KYC` tag).

        This method invokes the `issuerestrictedasset` RPC, creating a new restricted asset.
        The asset name must begin with `$` (added automatically if omitted).

        Args:
            asset_name (str):
                The unique name of the asset. Must be unique on-chain. If it does not begin with `$`,
                the node will automatically prepend it (e.g., `"SECURITY"` → `"$SECURITY"`).
            qty (int):
                Quantity of the asset to issue. No enforced small limit (unlike qualifiers).
            verifier (str):
                The verifier string (e.g., `"#KYC & !#AML"`) that defines transfer restrictions.
                This string is checked whenever the asset is moved.
            to_address (str):
                Recipient address for the issued asset. Must satisfy the `verifier` string rules.
            change_address (str, optional):
                Address to receive EVR change from the issuance transaction. If `""` or omitted,
                the node will generate a change address.
            units (int, optional):
                Decimal precision for the asset (0 = whole units, 8 = maximum precision).
                Defaults to `0`.
            reissuable (bool, optional):
                Whether more of this asset can be created in the future (and whether the verifier
                string can be changed). Defaults to `True`.
            has_ipfs (bool, optional):
                Whether to attach an IPFS (or RIP-5 txid) hash. Defaults to `False`.
            ipfs_hash (str, optional):
                The IPFS hash (or txid hash once RIP-5 is active). Required if `has_ipfs=True`.
            permanent_ipfs_hash (str, optional):
                A permanent IPFS hash tied to the asset. Defaults to `""`.
            toll_amount (float, optional):
                The toll fee amount associated with the asset. Defaults to `0.0`.
            toll_address (str, optional):
                Address that will receive the toll fee. Defaults to the protocol’s toll address
                if omitted.
            toll_amount_mutability (bool, optional):
                Whether the toll amount can be changed in the future. Defaults to `False`.
            toll_address_mutability (bool, optional):
                Whether the toll address can be changed in the future. Defaults to `False`.
            remintable (bool, optional):
                Whether burned tokens can be reminted. Defaults to `True`.

        Returns:
            str:
                On success, returns the transaction ID (`txid`) of the issuance transaction.
                On error, returns a formatted string describing the failure, including:
                  - the error message,
                  - the CLI command executed,
                  - any stderr output from the node.

        Notes:
            - Restricted assets always start with `$`.
            - Unlike qualifiers, restricted assets **can** be reissuable (unless specified otherwise).
            - A verifier string is mandatory and will be enforced by the node.

        Example:
            Issue a restricted asset with verifier rules, sending to a known address:

            >>> rpc = RestrictedassetsRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> txid = rpc.issuerestrictedasset("$SECURITY", 1000, "#KYC & !#AML","mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF")


            Issue a restricted asset with 2 decimal places and IPFS metadata:

            >>> txid = rpc.issuerestrictedasset("$BOND", 5000, "#ACCREDITED","mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF",units=2, has_ipfs=True,ipfs_hash="QmTqu3Lk3gmTsQVtjU7rYYM37EAW4xNmbuEAp2Mjr4AV7E")
        """

        # Build the Evrmore CLI command with required arguments first.
        # asset_name: node will enforce '$' prefix if not provided
        # qty: total quantity to issue
        # verifier: transfer restrictions (e.g., "#KYC & !#AML")
        # to_address: must satisfy verifier requirements
        command = self._build_command() + [
            "issuerestrictedasset",
            str(asset_name),
            str(qty),
            str(verifier),
            str(to_address)
        ]

        # Append optional arguments only if provided by the caller.
        if change_address is not None:
            command.append(str(change_address))
        if units is not None:
            command.append(str(units))
        if reissuable is not None:
            command.append(str(reissuable).lower())  # convert bool to 'true'/'false'
        if has_ipfs is not None:
            command.append(str(has_ipfs).lower())
        if ipfs_hash is not None:
            command.append(str(ipfs_hash))
        if permanent_ipfs_hash is not None:
            command.append(str(permanent_ipfs_hash))
        if toll_amount is not None:
            command.append(str(toll_amount))
        if toll_address is not None:
            command.append(str(toll_address))
        if toll_amount_mutability is not None:
            command.append(str(toll_amount_mutability).lower())
        if toll_address_mutability is not None:
            command.append(str(toll_address_mutability).lower())
        if remintable is not None:
            command.append(str(remintable).lower())

        try:
            # Execute the command and capture stdout/stderr from the subprocess.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = result.stdout.strip()

            try:
                # Attempt to parse the response as JSON (typically a txid string).
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                # Fallback: return raw output if not valid JSON.
                return out or "Success, but no txid returned."
        except Exception as e:
            # Standardized error surface (prefer daemon stderr, fallback to exception text).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def isvalidverifierstring(self, verifier_string):
        """
        Check whether a verifier string is syntactically valid for restricted assets.

        Invokes the `isvalidverifierstring` RPC, which parses and validates a verifier
        expression used by restricted assets to gate transfers based on tags/qualifiers.
        A typical verifier might look like: ``#KYC & !#SANCTIONED`` or
        ``(#ACCREDITED | #PRO) & !#BLOCKED``.

            isvalidverifierstring verifier_string

        Args:
            verifier_string (str):
                The verifier expression to check. Use `#TAG` notation for qualifier tags
                and boolean operators like `&` (AND), `|` (OR), and `!` (NOT). Parentheses
                are allowed for grouping.

        Returns:
            str:
                - On success: a human-readable status string from the node indicating
                  whether the verifier string is valid (and, if not, why).
                  (The RPC returns a string, not a boolean.)
                - If the node emits JSON instead of plain text, the parsed value is
                  coerced to `str`.
                - "No data returned." if stdout is empty.
                - On error: "Error: <node stderr or exception message>"

        Notes:
            - This checks **syntax/validity**, not whether referenced tags currently
              exist or are assigned to any addresses.
            - Common operators:
                * `&`  → logical AND
                * `|`  → logical OR
                * `!`  → logical NOT
              Use parentheses to make precedence explicit.
            - Tags should be prefixed with `#` (e.g., `#KYC`). The parser typically
              expects the prefix.

        Example:
            >>> rpc = RestrictedassetsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                           rpc_user="user", rpc_pass="pass", testnet=True)
            >>> msg = rpc.isvalidverifierstring("(#KYC | #PRO) & !#SANCTIONED")
        """
        # Build the CLI command exactly as the daemon expects: RPC name + argument.
        command = self._build_command() + [
            "isvalidverifierstring",
            str(verifier_string),  # e.g., "(#KYC | #PRO) & !#SANCTIONED"
        ]

        try:
            # Run the command; non-zero exit codes raise a CalledProcessError that
            # includes stderr (which we will surface in the error message).
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # The daemon typically returns a plain text line like "Valid" or an error reason.
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Be defensive: if a build returns JSON (string or object), parse it then coerce.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                # Most common path: already a plain string result.
                return out

        except Exception as e:
            # Standardized, user-friendly error format (prefer daemon stderr).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def listaddressesfortag(self, tag_name):
        """
        List all addresses that have been assigned a specific tag (qualifier).

        Invokes the `listaddressesfortag` RPC to retrieve the set of wallet and
        non-wallet addresses that currently hold the given tag (qualifier asset),
        e.g., `#KYC`.

            listaddressesfortag tag_name

        Args:
            tag_name (str):
                The tag (qualifier asset) to query. If not prefixed with `#`, the
                node may add/require it depending on policy (recommended: pass the
                canonical form, e.g., "#KYC").

        Returns:
            list[str] | str:
                - On success (typical): a Python list of address strings.
                - If the daemon returns a plain string or unexpected JSON, the raw
                  or stringified output is returned.
                - "No data returned." if stdout is empty.
                - On error: "Error: <node stderr or exception message>"

        Notes:
            - Tags are implemented as **qualifier assets**; this call introspects
              current tag assignments on-chain (not historical).
            - Results are not restricted to wallet-owned addresses.

        Example:
            >>> rpc = RestrictedassetsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                           rpc_user="user", rpc_pass="pass", testnet=True)
            >>> addrs = rpc.listaddressesfortag("#KYC")
        """
        # Build the CLI command with positional arguments in the exact order expected.
        command = self._build_command() + [
            "listaddressesfortag",
            str(tag_name),  # e.g., "#KYC"
        ]

        try:
            # Execute the RPC; non-zero exit codes raise CalledProcessError with stderr.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()

            if not out:
                return "No data returned."

            # Try JSON first: expected shape is a JSON array of address strings.
            try:
                parsed = json.loads(out)
                if isinstance(parsed, list):
                    # Ensure everything is string-typed for downstream consumers.
                    return [str(x) for x in parsed]
                # Unexpected shape; surface as a string for transparency.
                return str(parsed)
            except json.JSONDecodeError:
                # Fallback: some builds might emit newline- or comma-separated text.
                if "\n" in out:
                    return [line.strip() for line in out.splitlines() if line.strip()]
                if "," in out:
                    return [part.strip() for part in out.split(",") if part.strip()]
                # Otherwise, return the raw text.
                return out

        except Exception as e:
            # Standardized, user-friendly error message (prefer daemon stderr).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def listaddressrestrictions(self, address):
        """
        List all restricted assets that have **frozen** the specified address.

        Invokes the `listaddressrestrictions` RPC to retrieve the set of restricted
        asset names that currently have an address-level freeze applied to `address`.

            listaddressrestrictions address

        Args:
            address (str):
                The EVR address to query for active per-asset freezes.

        Returns:
            list[str] | str:
                - On success (typical): a list of restricted asset names (e.g., ["$ASSET1", "$ASSET2"]).
                - If the daemon returns plain text or unexpected JSON, a string is returned.
                - "No data returned." if stdout is empty.
                - On error: "Error: <node stderr or exception message>"

        Notes:
            - This reports **address-level freezes** (not global freezes). To check if an
              asset is globally frozen, use the appropriate global-freeze query.
            - Results are based on current chain state (not historical).

        Example:
            >>> rpc = RestrictedassetsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                           rpc_user="user", rpc_pass="pass", testnet=True)
            >>> frozen_by = rpc.listaddressrestrictions("mxSognf8BrWSgG4pxiko7XsAkPVLsMGnch")
        """
        # Build the CLI command in the exact positional order the daemon expects.
        command = self._build_command() + [
            "listaddressrestrictions",
            str(address),  # Address to inspect for per-asset freezes
        ]

        try:
            # Execute the RPC; non-zero exit codes raise with stderr captured.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Preferred path: daemon returns a JSON array of strings.
            try:
                parsed = json.loads(out)
                if isinstance(parsed, list):
                    return [str(x) for x in parsed]
                # Unexpected JSON shape; stringify for transparency.
                return str(parsed)
            except json.JSONDecodeError:
                # Fallbacks for non-JSON outputs (some builds/tools echo plain text).
                if "\n" in out:
                    return [line.strip() for line in out.splitlines() if line.strip()]
                if "," in out:
                    return [part.strip() for part in out.split(",") if part.strip()]
                # If it's just one asset name as a bare string, return it raw.
                return out

        except Exception as e:
            # Standardized, user-friendly error message (prefer daemon stderr if present).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def listglobalrestrictions(self):
        """
        List all restricted assets that are currently **globally frozen**.

        Invokes the `listglobalrestrictions` RPC, which returns the set of restricted
        asset names (e.g., "$ASSET") that have an active **global freeze**. When an
        asset is globally frozen, *all* transfers are disallowed regardless of any
        per-address state.

            listglobalrestrictions

        Args:
            None

        Returns:
            list[str] | str:
                - On success (typical): a list of restricted asset names (e.g., ["$SECURITY", "$TOKENX"]).
                - If the daemon returns plain text or an unexpected JSON structure, a string is returned.
                - "No data returned." if stdout is empty.
                - On error: "Error: <node stderr or exception message>"

        Notes:
            - This call reports **global** freeze status only. For **address-level**
              freezes, use `listaddressrestrictions(address)`.

        Example:
            >>> rpc = RestrictedassetsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                           rpc_user="user", rpc_pass="pass", testnet=True)
            >>> frozen_assets = rpc.listglobalrestrictions()
        """
        # Build the CLI command exactly as expected by the daemon (no arguments).
        command = self._build_command() + [
            "listglobalrestrictions",
        ]

        try:
            # Execute the RPC; check=True will raise on non-zero exit codes and include stderr.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()

            if not out:
                return "No data returned."

            # Preferred: node returns JSON array of strings.
            try:
                parsed = json.loads(out)
                if isinstance(parsed, list):
                    # Normalize each entry to string for downstream consumers.
                    return [str(x) for x in parsed]
                # Unexpected JSON shape; stringify for transparency.
                return str(parsed)
            except json.JSONDecodeError:
                # Fallbacks for non-JSON outputs (some builds/tools echo plain text).
                if "\n" in out:
                    return [line.strip() for line in out.splitlines() if line.strip()]
                if "," in out:
                    return [part.strip() for part in out.split(",") if part.strip()]
                # If it's a single bare value, return it as-is.
                return out

        except Exception as e:
            # Standard, user-friendly error surface (prefer daemon stderr if present).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def listtagsforaddress(self, address):
        """
        List all tags (qualifier asset names) currently assigned to a specific address.

        Invokes the `listtagsforaddress` RPC to fetch the set of tag assets (e.g., `#KYC`,
        `#ACCREDITED`) that are presently applied to the given EVR address.

            listtagsforaddress address

        Args:
            address (str):
                The EVR address to inspect for tag assignments.

        Returns:
            list[str] | str:
                - On success (typical): a Python list of tag names (strings), e.g., ["#KYC", "#AML"].
                - If the daemon returns plain text or an unexpected JSON structure, a string is returned.
                - "No data returned." if stdout is empty.
                - On error: "Error: <node stderr or exception message>"

        Notes:
            - Tags are implemented as **qualifier assets** (prefixed with `#`).
            - This reflects current chain state, not historical tagging events.

        Example:
            >>> rpc = RestrictedassetsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                           rpc_user="user", rpc_pass="pass", testnet=True)
            >>> tags = rpc.listtagsforaddress("mxSognf8BrWSgG4pxiko7XsAkPVLsMGnch")
        """
        # Build the CLI command in the exact order expected by the node.
        command = self._build_command() + [
            "listtagsforaddress",
            str(address),  # Address whose tag assignments we want to list
        ]

        try:
            # Run the command. Non-zero return codes raise an exception with stderr attached.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()

            # If the daemon returned nothing, surface a helpful message.
            if not out:
                return "No data returned."

            # Primary path: node returns a JSON array of tag names.
            try:
                parsed = json.loads(out)
                if isinstance(parsed, list):
                    # Normalize to strings to keep consumers safe.
                    return [str(x) for x in parsed]
                # Unexpected JSON shape; return as string for transparency.
                return str(parsed)
            except json.JSONDecodeError:
                # Fallbacks for builds that may echo non-JSON outputs:
                # - newline-separated or comma-separated lists
                if "\n" in out:
                    return [line.strip() for line in out.splitlines() if line.strip()]
                if "," in out:
                    return [part.strip() for part in out.split(",") if part.strip()]
                # Otherwise, a single bare value; return as-is.
                return out

        except Exception as e:
            # Standardized error surface: prefer stderr if present, else the exception message.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def reissuerestrictedasset(
            self,
            asset_name,
            qty,
            to_address,
            change_verifier=None,
            new_verifier=None,
            change_address=None,
            new_units=None,
            reissuable=None,
            new_ipfs=None,
            permanent_ipfs=None,
            change_toll_amount=None,
            toll_amount=None,
            toll_address=None,
            toll_amount_mutability=None,
            toll_address_mutability=None,
    ):
        """
        Reissue (add supply and/or change properties for) an existing **restricted asset**.

        Invokes the `reissuerestrictedasset` RPC. You can increase quantity, optionally change the
        verifier string, adjust units, toggle reissuability, update IPFS fields, and manage toll
        parameters. All positional optionals must be supplied **in order**. This wrapper helps by
        auto-filling omitted earlier arguments with the node’s defaults whenever a later argument is
        provided.

            reissuerestrictedasset "asset_name" qty to_address ( change_verifier ) ( "new_verifier" )
                                    "( change_address )" ( new_units ) ( reissuable ) "( new_ipfs )"
                                    "( permanent_ipfs )" ( change_toll_amount ) ( toll_amount )
                                    "( toll_address ) ( toll_amount_mutability ) ( toll_address_mutability )"

        Args:
            asset_name (str):
                The restricted asset to reissue (e.g., "$ASSET"). Must already exist.
            qty (int | float | str):
                Additional quantity to issue. Supply 0 if only changing flags/metadata.
            to_address (str):
                Destination address for the newly issued amount; **must satisfy** the current (or new)
                verifier string.
            change_verifier (bool, optional):
                If True, you must also provide `new_verifier`. Default: False.
            new_verifier (str, optional):
                New verifier expression (only used if `change_verifier=True`). Default: "".
            change_address (str, optional):
                Address to receive EVR change. Default: "" (node auto-generates).
            new_units (int, optional):
                New units/decimals (0–8). Use -1 to leave unchanged. Default: -1.
            reissuable (bool, optional):
                Whether future reissuance remains allowed. Default: True.
            new_ipfs (str, optional):
                New IPFS or txid hash (per RIP5). Default: "".
            permanent_ipfs (str, optional):
                New permanent IPFS hash. Default: "".
            change_toll_amount (bool, optional):
                True to change toll amount; then set `toll_amount`. Default: False.
            toll_amount (int | float | str, optional):
                New toll amount (if changing). Default: 0.
            toll_address (str, optional):
                New toll address. Default: "".
            toll_amount_mutability (bool, optional):
                Whether the toll amount can be changed in the future. Default: True.
            toll_address_mutability (bool, optional):
                Whether the toll address can be changed in the future. Default: True.

        Returns:
            str:
                - On success: the transaction ID (`txid`) as a string.
                - If the daemon responds with JSON that isn’t a bare string, it is stringified.
                - If no stdout is returned: "Success, but no txid returned."
                - On error: "Error: <node stderr or exception message>"

        Notes:
            - Because the RPC uses **positional** optionals, when you want to set a *later* optional
              you must include *all prior* optionals. This wrapper auto-fills any omitted earlier
              arguments with the node’s defaults to keep positions aligned.
            - Booleans are serialized as lowercase `"true"` / `"false"` to match CLI expectations.
            - `new_units=-1` is the sentinel to leave units unchanged.

        Example:
            Issue more supply and change the verifier:

            >>> rpc = RestrictedassetsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                           rpc_user="user", rpc_pass="pass", testnet=True)
            >>> txid = rpc.reissuerestrictedasset(
            ...     asset_name="$ASSET",
            ...     qty=1000,
            ...     to_address="myaddress",
            ...     change_verifier=True,
            ...     new_verifier="#KYC & !#SANCTIONED",
            ... )
        """
        # --- Build the base command with the required positional arguments ---
        command = self._build_command() + [
            "reissuerestrictedasset",
            str(asset_name),  # Restricted asset name (e.g., "$ASSET")
            str(qty),  # Additional quantity to issue
            str(to_address),  # Destination (must satisfy verifier)
        ]

        # Ordered optional parameters exactly as the RPC expects them.
        # We’ll collect provided values or defaults up to the last provided index.
        optional_values = [
            change_verifier,  # 4: bool (default False)
            new_verifier,  # 5: str  (default "")
            change_address,  # 6: str  (default "")
            new_units,  # 7: int  (default -1)
            reissuable,  # 8: bool (default True)
            new_ipfs,  # 9: str  (default "")
            permanent_ipfs,  # 10: str (default "")
            change_toll_amount,  # 11: bool (default False)
            toll_amount,  # 12: num (default 0)
            toll_address,  # 13: str (default "")
            toll_amount_mutability,  # 14: bool (default True)
            toll_address_mutability,  # 15: bool (default True)
        ]

        # Node defaults for each optional position (used when later args are supplied).
        defaults = [
            False,  # change_verifier
            "",  # new_verifier
            "",  # change_address
            -1,  # new_units
            True,  # reissuable
            "",  # new_ipfs
            "",  # permanent_ipfs
            False,  # change_toll_amount
            0,  # toll_amount
            "",  # toll_address
            True,  # toll_amount_mutability
            True,  # toll_address_mutability
        ]

        # Determine the highest index of user-supplied optionals.
        last_supplied = -1
        for i, val in enumerate(optional_values):
            if val is not None:
                last_supplied = i

        # If anything beyond the required args was provided, append a complete slice
        # of optionals through the last supplied index, filling gaps with defaults.
        if last_supplied >= 0:
            for i in range(0, last_supplied + 1):
                val = optional_values[i]
                # Use default when this positional slot was not provided by the caller.
                if val is None:
                    val = defaults[i]

                # CLI expects lowercase 'true'/'false' for booleans.
                if isinstance(val, bool):
                    command.append(str(val).lower())
                else:
                    command.append(str(val))

        try:
            # Execute the command; errors (non-zero exit) raise with stderr captured.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()

            if not out:
                return "Success, but no txid returned."

            # Try to parse JSON first; most nodes return a JSON string for txid.
            try:
                parsed = json.loads(out)
                if isinstance(parsed, list):
                    # Defensive: join if a list of txids is ever returned.
                    return ", ".join(str(x) for x in parsed)
                return str(parsed)
            except json.JSONDecodeError:
                # Fallback for plain-text txid response.
                return out

        except Exception as e:
            # Your standardized, user-friendly error surface.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def removetagfromaddress(self, tag_name, to_address, change_address=None, asset_data=None):
        """
        Remove a qualifier **tag** (e.g., "#KYC") from a specific address.

        Invokes the `removetagfromaddress` RPC, which transfers the corresponding qualifier
        token **away** from the target address, effectively removing the tag assignment.

            removetagfromaddress tag_name to_address (change_address) (asset_data)

        Args:
            tag_name (str):
                The tag asset name to remove (e.g., "#KYC"). If the leading '#' is omitted,
                the node will typically normalize it for you, but passing the canonical form
                is recommended.
            to_address (str):
                The Evrmore address to remove the tag from.
            change_address (str, optional):
                Address to receive change from the qualifier token transfer. Pass `""` to let
                the node generate a change address. If you want to provide `asset_data`
                without specifying `change_address`, the wrapper will pass an empty string as
                a placeholder to keep RPC argument positions aligned.
            asset_data (str, optional):
                Optional metadata (e.g., an IPFS hash or other string) to attach to the tag
                transfer. Pass `""` if not used.

        Returns:
            str:
                On success, the transaction id (`txid`) as a string. If the node returns JSON
                that is not a simple string, it is stringified. If stdout is empty, a helpful
                message is returned. On failure, returns:
                `"Error: <daemon stderr or exception message>"`.

        Notes:
            - The RPC uses **positional** optional arguments. If you provide `asset_data`
              while omitting `change_address`, this wrapper inserts `""` for the missing
              `change_address` to keep parameters in the correct order.
            - Booleans are not involved here; strings are sent as provided.

        Example:
            Remove the `#KYC` tag from an address, letting the node choose the change address:

            >>> rpc = RestrictedassetsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                           rpc_user="user", rpc_pass="pass", testnet=True)
            >>> txid = rpc.removetagfromaddress("#KYC", "mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF")
        """
        # -----------------------------
        # Build the base CLI invocation
        # -----------------------------
        command = self._build_command() + [
            "removetagfromaddress",
            str(tag_name),  # Tag asset name (e.g., "#KYC")
            str(to_address),  # Address from which the tag will be removed
        ]

        # --------------------------------------------------------------------
        # Handle positional optionals:
        #   order is: tag_name, to_address, (change_address), (asset_data)
        #
        # If asset_data is provided but change_address is omitted, we MUST pass
        # an empty string "" as a placeholder for change_address so that asset_data
        # occupies the 4th positional slot (not the 3rd).
        # --------------------------------------------------------------------
        if change_address is not None:
            command.append(str(change_address))
            if asset_data is not None:
                command.append(str(asset_data))
        else:
            if asset_data is not None:
                # Insert placeholder for change_address, then pass asset_data
                command.extend(["", str(asset_data)])

        try:
            # Execute the command; non-zero exit raises CalledProcessError with stderr captured.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()

            if not out:
                return "Could not remove tag from address."

            # Try JSON first (some builds may emit JSON); fall back to raw text.
            try:
                parsed = json.loads(out)
                if isinstance(parsed, list):
                    # Defensive: join if a list of txids is ever returned
                    return ", ".join(str(x) for x in parsed)
                return str(parsed)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized, user-friendly error reporting (your requested format).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def transferqualifier(self,
                          qualifier_name,
                          qty,
                          to_address,
                          change_address=None,
                          message=None,
                          expire_time=None):
        """
        Transfer a **qualifier asset** (e.g., "#KYC") owned by this wallet to a target address.

        Invokes the `transferqualifier` RPC:

            transferqualifier "qualifier_name" qty "to_address" ("change_address") ("message") (expire_time)

        This will send the given quantity of the qualifier token to `to_address`. Qualifiers are
        typically used as tags/attributes that can be assigned to addresses.

        Args:
            qualifier_name (str):
                The qualifier asset name (e.g., "#KYC"). Pass canonical form with leading '#'.
            qty (int | float | str):
                Number of qualifier units to send.
            to_address (str):
                Destination Evrmore address.
            change_address (str, optional):
                Address to receive evr/change from this transaction. Pass `""` to auto-generate.
                If you want to provide `message` or `expire_time` without a `change_address`,
                this wrapper inserts `""` as a placeholder to keep the RPC’s positional order.
            message (str, optional):
                Optional memo to attach (e.g., IPFS hash or a txid hash once RIP5 is active).
                If you provide `expire_time` without a `message`, we pass an empty string `""`
                placeholder for `message` to keep ordering correct.
            expire_time (int | str, optional):
                Optional **UTC timestamp** when the message expires.

        Returns:
            str:
                - On success: the transaction id (`txid`) as a string. If the RPC returns a JSON
                  array of txids, they’re joined into a comma-separated string.
                - If stdout is empty: a helpful message string.
                - On failure: `"Error: <daemon stderr or exception message>"`.

        Notes:
            - The RPC uses **positional** optional parameters. This wrapper ensures argument
              alignment by inserting empty-string placeholders when needed.
            - No booleans are used here; quantities and timestamps are serialized as strings.

        Example:
            >>> rpc = RestrictedassetsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                           rpc_user="user", rpc_pass="pass", testnet=True)
            >>> txid = rpc.transferqualifier("#KYC", 1, "mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF", "", "QmHash", 1700000000)
        """
        # ------------------------------------------------------
        # Build base CLI command with required positional args.
        # Everything is cast to str for safe subprocess invocation.
        # ------------------------------------------------------
        command = self._build_command() + [
            "transferqualifier",
            str(qualifier_name),  # Qualifier asset, e.g., "#KYC"
            str(qty),  # Quantity to send
            str(to_address),  # Destination address
        ]

        # ----------------------------------------------------------------------
        # Handle positional optionals in order:
        #   4) change_address (default ""), 5) message, 6) expire_time
        #
        # We must preserve positions. If a later argument is provided while an
        # earlier one is omitted, insert "" placeholders to keep ordering intact.
        # ----------------------------------------------------------------------
        if change_address is not None:
            # change_address provided
            command.append(str(change_address))
            if message is not None:
                # message provided
                command.append(str(message))
                if expire_time is not None:
                    command.append(str(expire_time))
            else:
                # message omitted
                if expire_time is not None:
                    # Need "" placeholder for message before expire_time
                    command.extend(["", str(expire_time)])
        else:
            # change_address omitted
            if (message is not None) or (expire_time is not None):
                # Insert "" placeholder for change_address
                command.append("")
                if message is not None:
                    command.append(str(message))
                    if expire_time is not None:
                        command.append(str(expire_time))
                else:
                    # message omitted, but expire_time provided:
                    # need "" placeholder for message
                    if expire_time is not None:
                        command.extend(["", str(expire_time)])
            # else: neither message nor expire_time provided → nothing to add

        try:
            # Execute the RPC; non-zero exit returns CalledProcessError with stderr set.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()

            if not out:
                return "No txid returned by node."

            # Try to parse JSON first; some builds may return JSON arrays of txids.
            try:
                parsed = json.loads(out)
                if isinstance(parsed, list):
                    return ", ".join(str(x) for x in parsed)
                return str(parsed)
            except json.JSONDecodeError:
                # Not JSON; return raw output (often a single txid string).
                return out

        except Exception as e:
            # Your standardized, user-friendly error reporting.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def unfreezeaddress(self,
                        asset_name,
                        address,
                        change_address=None,
                        asset_data=None):
        """
        Unfreeze a specific address for a restricted asset, allowing transfers again.

        Invokes the `unfreezeaddress` RPC:

            unfreezeaddress asset_name address (change_address) (asset_data)

        This sends the restricted asset's **owner token** as needed to lift the freeze on
        `address`. Optional metadata (e.g., an IPFS or txid hash) can be attached to the
        owner-token transfer via `asset_data`.

        Args:
            asset_name (str):
                The **restricted asset** name (canonical form recommended, e.g., "$SECURITY").
            address (str):
                The Evrmore address to unfreeze (i.e., re-enable transfers of `asset_name`).
            change_address (str, optional):
                The change address for the **owner token** transfer. Pass `""` to let the node
                choose a change address automatically. If you want to supply `asset_data`
                without a `change_address`, this wrapper will insert `""` as a positional
                placeholder to keep the RPC’s argument order correct.
            asset_data (str, optional):
                Optional metadata string (IPFS hash or other hash per RIP5) to attach to the
                owner-token transfer that performs the unfreeze.

        Returns:
            str:
                - On success, returns the transaction id (`txid`) as a string.
                - If the node returns a JSON array of txids, they are joined with commas.
                - If stdout is empty, returns a helpful message string.
                - On failure, returns: `"Error: <daemon stderr or exception message>"`.

        Notes:
            - The optional arguments are **positional**; when `asset_data` is provided without
              `change_address`, an empty string is inserted for `change_address` to satisfy the
              RPC’s parameter order.

        Example:
            >>> rpc = RestrictedassetsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                           rpc_user="user", rpc_pass="pass", testnet=True)
            >>> txid = rpc.unfreezeaddress("$RESTRICTED_ASSET", "mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF", "", "QmHashOrTxid")
        """
        # ---------------------------------------------------------------------
        # Build base command with required positional parameters.
        # Cast everything to str to avoid type issues in subprocess.
        # ---------------------------------------------------------------------
        command = self._build_command() + [
            "unfreezeaddress",
            str(asset_name),  # Restricted asset name (e.g., "$ASSET")
            str(address),  # Address to unfreeze
        ]

        # ---------------------------------------------------------------------
        # Handle optional positional parameters:
        #   (3) change_address, (4) asset_data
        # If asset_data is provided but change_address is not, insert "" to keep order.
        # ---------------------------------------------------------------------
        if change_address is not None:
            command.append(str(change_address))
            if asset_data is not None:
                command.append(str(asset_data))
        else:
            if asset_data is not None:
                command.extend(["", str(asset_data)])
            # else: neither optional provided → nothing to append

        try:
            # Execute the RPC; non-zero exit triggers CalledProcessError with stderr set.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()

            if not out:
                return "No txid returned by node."

            # Try JSON first (some builds respond with JSON arrays/strings).
            try:
                parsed = json.loads(out)
                if isinstance(parsed, list):
                    return ", ".join(str(x) for x in parsed)
                return str(parsed)
            except json.JSONDecodeError:
                # Not JSON; return raw string (often a single txid).
                return out

        except Exception as e:
            # Standardized, user-friendly error format you requested.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def unfreezerestrictedasset(self, asset_name, change_address=None, asset_data=None):
        """
        Unfreeze all trading for a specific restricted asset.

        Invokes the `unfreezerestrictedasset` RPC:

            unfreezerestrictedasset asset_name (change_address) (asset_data)

        This sends the restricted asset’s **owner token** as required to lift the
        *global freeze* on the asset so transfers are allowed again. Optional
        metadata (e.g., an IPFS or txid hash) can be attached to the owner-token
        transfer via `asset_data`.

        Args:
            asset_name (str):
                The **restricted asset** name (canonical form recommended, e.g., "$SECURITY").
            change_address (str, optional):
                The change address for the **owner token** transfer. Pass `""` to let the node
                select a change address automatically. If you supply `asset_data` without
                a `change_address`, this wrapper inserts `""` as a positional placeholder
                to keep the RPC’s argument order correct.
            asset_data (str, optional):
                Optional metadata string (IPFS hash or other hash per RIP5) to attach to the
                owner-token transfer that performs the unfreeze.

        Returns:
            str:
                - On success, returns the transaction id (`txid`) as a string.
                - If the node returns a JSON array of txids, they are joined with commas.
                - If stdout is empty, returns a helpful message string.
                - On failure, returns: `"Error: <daemon stderr or exception message>"`.

        Notes:
            - The optional parameters are **positional**. If `asset_data` is provided
              without `change_address`, an empty string is inserted for `change_address`
              to satisfy the RPC’s parameter order.

        Example:
            >>> rpc = RestrictedassetsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                           rpc_user="user", rpc_pass="pass", testnet=True)
            >>> txid = rpc.unfreezerestrictedasset("$RESTRICTED_ASSET")

            With explicit change address and metadata:

            >>> txid = rpc.unfreezerestrictedasset("$RESTRICTED_ASSET",
            ...                                    change_address="myChangeAddr",
            ...                                    asset_data="QmHashOrTxid")
        """
        # ---------------------------------------------------------------------
        # Build base command with required positional parameter.
        # Cast to str for safe subprocess joining/serialization.
        # ---------------------------------------------------------------------
        command = self._build_command() + [
            "unfreezerestrictedasset",
            str(asset_name),  # Restricted asset name (e.g., "$ASSET")
        ]

        # ---------------------------------------------------------------------
        # Handle optional positional parameters:
        #   (2) change_address, (3) asset_data
        # If asset_data is provided without change_address, insert "" to keep order.
        # ---------------------------------------------------------------------
        if change_address is not None:
            command.append(str(change_address))
            if asset_data is not None:
                command.append(str(asset_data))
        else:
            if asset_data is not None:
                command.extend(["", str(asset_data)])
            # else: neither optional provided → nothing to append

        try:
            # Execute the RPC; non-zero exit triggers CalledProcessError with stderr.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()

            if not out:
                return "No txid returned by node."

            # Try JSON first (some builds return JSON strings/arrays).
            try:
                parsed = json.loads(out)
                if isinstance(parsed, list):
                    return ", ".join(str(x) for x in parsed)
                return str(parsed)
            except json.JSONDecodeError:
                # Not JSON; return raw string (often a single txid).
                return out

        except Exception as e:
            # Standardized, user-friendly error format you requested.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()
