from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json



class RewardsRPC:

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

    def cancelsnapshotrequest(self, asset_name, block_height):
        """
        Cancel a previously scheduled rewards snapshot for an asset at a given height.

        Invokes the `cancelsnapshotrequest` RPC, which removes a snapshot request
        identified by the asset name and the target block height.

            cancelsnapshotrequest "asset_name" block_height

        Args:
            asset_name (str):
                The asset for which the snapshot was scheduled (e.g., "TRONCO").
                Use the exact on-chain asset name.
            block_height (int | str):
                The chain height at which the snapshot was to be taken.
                Must be an integer height; if a string is provided, it should parse to an int.

        Returns:
            dict | str:
                - On success: a dict (e.g., {"request_status": "canceled"}), if the node returns JSON.
                - If the node returns non-JSON text, that raw text is returned.
                - If no output is produced: "No data returned."
                - On error: "Error: <node stderr or exception message>"

        Notes:
            - This cancels the specific snapshot for the given (asset_name, block_height) pair.
            - If no such request exists, the node may return an error.

        Example:
            >>> rpc = RewardsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                  rpc_user="user", rpc_pass="pass", testnet=True)
            >>> res = rpc.cancelsnapshotrequest("PHATSTACKS", 34987)
            >>> isinstance(res, (dict, str))
            True
        """
        # --- Build the CLI command in the exact positional order the node expects ---
        # Convert height to int for early validation (ensures we pass a proper integer to the daemon).
        try:
            height_str = str(int(block_height))
        except Exception as e:
            # Surface a friendly error if caller passed a non-integer height.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

        command = self._build_command() + [
            "cancelsnapshotrequest",
            str(asset_name),  # Asset name exactly as scheduled for the snapshot
            height_str,  # Target block height of the snapshot request
        ]

        try:
            # Execute the RPC; check=True raises on non-zero exit codes with stderr captured.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize and parse the output. Expected JSON like: {"request_status": "..."}
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            try:
                parsed = json.loads(out)
                # Return the parsed dict directly for ergonomic consumption.
                return parsed if isinstance(parsed, dict) else str(parsed)
            except json.JSONDecodeError:
                # If node returned plain text, surface it as-is.
                return out

        except Exception as e:
            # Standardized, user-friendly error surfacing (prefer node stderr when available).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def distributereward(
            self,
            asset_name,
            snapshot_height,
            distribution_asset_name,
            gross_distribution_amount,
            exception_addresses=None,
            change_address=None,
            dry_run=None,
    ):
        """
        Distribute an asset (or EVR) to all owners of another asset based on a snapshot.

        Invokes the `distributereward` RPC to split a specified total (gross) amount of
        a *distribution asset* across all holders of `asset_name` as of `snapshot_height`.
        You can optionally exclude specific ownership addresses and/or direct any remainder
        (change) to a specific address.

            distributereward "asset_name" snapshot_height "distribution_asset_name"
                             gross_distribution_amount ( "exception_addresses" )
                             ( "change_address" ) ( "dry_run" )

        Args:
            asset_name (str):
                The source asset whose holders receive the reward (e.g., "TRONCO").
            snapshot_height (int | str):
                The block height at which holdings were snapshotted. Must be an integer.
            distribution_asset_name (str):
                The asset being distributed, or `"EVR"` to distribute EVR.
            gross_distribution_amount (int | float | str | Decimal):
                The total amount of the distribution asset to split among eligible holders.
                For precision, pass a string or `Decimal` (floats can introduce rounding issues).
            exception_addresses (str | None, optional):
                Comma-separated list of addresses to exclude from receiving the reward, e.g.:
                `"addr1,addr2,addr3"`. Leave `None`/empty to include everyone.
            change_address (str | None, optional):
                If the full amount cannot be exactly distributed, any remainder is sent here.
                Leave `None`/empty to let the node choose (or handle internally).
            dry_run (bool | str | None, optional):
                If supported by your daemon build, toggle a simulation-only run.
                - If `bool`, this wrapper passes `"true"`/`"false"`.
                - If `str`, it is sent verbatim (e.g., `"true"`).
                - Omit (`None`) to perform a real distribution.

        Returns:
            dict | str:
                - On success with JSON output: a dict containing fields like
                  `error_txn_gen_failed`, `error_nsf`, `error_rejects`, `error_db_update`,
                  and `batch_results` (with per-batch txn details).
                - If non-JSON text is returned: that text verbatim.
                - If no output: `"No data returned."`
                - On error: `"Error: <node stderr or exception message>"`.

        Notes:
            - **Positional parameters:** If you provide `dry_run` but omit `exception_addresses`
              and/or `change_address`, placeholders (empty strings) are inserted to preserve
              the expected positions.
            - **Large distributions** may be processed in batches. Check `batch_results` for
              transaction IDs, fees, and counts.
            - **EVR vs assets:** Set `distribution_asset_name="EVR"` to pay in EVR; otherwise,
              provide the asset name you’re distributing.
            - **Exclusions:** `exception_addresses` filters by ownership addresses—not labels.

        Example:
            >>> rpc = RewardsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                  rpc_user="user", rpc_pass="pass", testnet=True)
            >>> result = rpc.distributereward(
            ...     asset_name="PHATSTACKS",
            ...     snapshot_height=34987,
            ...     distribution_asset_name="EVR",
            ...     gross_distribution_amount="1000.00000000",
            ...     exception_addresses="mwN7xC3yomYdvJuVXkVC7ymY9wNBjWNduD,n4Rf18edydDaRBh7t6gHUbuByLbWEoWUTg",
            ...     # change_address=None,
            ...     # dry_run=True,
            ... )

        """
        # ---- Validate & normalize numerics safely ---------------------------------
        # Snapshot height must be an integer height.
        try:
            height_str = str(int(snapshot_height))
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

        # Gross amount: preserve precision using Decimal when possible.
        try:
            from decimal import Decimal
            if isinstance(gross_distribution_amount, float):
                gross_str = str(Decimal(str(gross_distribution_amount)))
            elif isinstance(gross_distribution_amount, Decimal):
                gross_str = str(gross_distribution_amount)
            else:
                gross_str = str(gross_distribution_amount)
        except Exception:
            gross_str = str(gross_distribution_amount)

        # ---- Build positional argument list in exact RPC order --------------------
        args = [
            "distributereward",
            str(asset_name),  # 1: source asset whose holders receive reward
            height_str,  # 2: snapshot height (integer)
            str(distribution_asset_name),  # 3: distribution asset name or "EVR"
            gross_str,  # 4: gross amount to split
        ]

        # Determine if any optional arg is present. If later args are provided,
        # insert placeholders for the earlier ones to maintain positions.
        any_optional = exception_addresses is not None or change_address is not None or dry_run is not None
        if any_optional:
            # Slot 5: exception_addresses (comma-separated string)
            args.append("" if exception_addresses is None else str(exception_addresses))

            # Slot 6: change_address (requires previous slot to exist even if empty)
            if change_address is not None or dry_run is not None:
                args.append("" if change_address is None else str(change_address))

            # Slot 7: dry_run (boolean/string)
            if dry_run is not None:
                if isinstance(dry_run, bool):
                    args.append("true" if dry_run else "false")
                else:
                    args.append(str(dry_run))

        # Compose the full command.
        command = self._build_command() + args

        try:
            # Execute the RPC; check=True ensures non-zero exit raises with stderr captured.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Prefer JSON parsing (expected for this RPC).
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, dict) else str(parsed)
            except json.JSONDecodeError:
                # Fallback for plain text responses.
                return out

        except Exception as e:
            # Standardized, user-friendly error surfacing (prefer daemon stderr when present).
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getdistributestatus(
            self,
            asset_name,
            snapshot_height,
            distribution_asset_name,
            gross_distribution_amount,
            exception_addresses=None,
    ):
        """
        Get the status of a (planned or executed) rewards distribution.

        Invokes the `getdistributestatus` RPC to retrieve information about a distribution
        that would (or did) pay out `distribution_asset_name` to all holders of `asset_name`
        as of `snapshot_height`, optionally excluding specific addresses.

            getdistributestatus "asset_name" snapshot_height
                                "distribution_asset_name" gross_distribution_amount
                                ( "exception_addresses" )

        Args:
            asset_name (str):
                The source asset whose holders are (or would be) rewarded (e.g., "TRONCO").
            snapshot_height (int | str):
                Block height at which the ownership snapshot was (or will be) taken.
                Must be an integer height; strings are accepted if they parse cleanly.
            distribution_asset_name (str):
                Asset being distributed, or the literal `"EVR"` to distribute EVR.
            gross_distribution_amount (int | float | str | Decimal):
                Total amount of the *distribution* asset to split among eligible holders.
                For precision, prefer a `str` (e.g., `"1000.00000000"`) or `Decimal`.
            exception_addresses (str | None, optional):
                Comma-separated list of addresses to exclude from the distribution,
                e.g. `"addr1,addr2,addr3"`. Omit or pass `None` to include everyone.

        Returns:
            dict | list | str:
                - On success with JSON output: a parsed Python object (commonly a dict,
                  but some builds may return an array).
                - If non-JSON text is returned: the raw text string.
                - If no output: `"No data returned."`
                - On error: `"Error: <node stderr or exception message>"`

        Notes:
            - This call is informational; it **does not** perform any distribution.
            - Use `requestsnapshot` / `cancelsnapshotrequest` to manage snapshots and
              `distributereward` to execute distributions.
            - The “status” payload format can vary by build/version; this wrapper
              returns whatever JSON the node emits.

        Example:
            >>> rpc = RewardsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                  rpc_user="user", rpc_pass="pass", testnet=True)
            >>> res = rpc.getdistributestatus(
            ...     asset_name="PHATSTACKS",
            ...     snapshot_height=34987,
            ...     distribution_asset_name="EVR",
            ...     gross_distribution_amount="1000.00000000",
            ...     exception_addresses="mwN7xC3yomYdvJuVXkVC7ymY9wNBjWNduD,n4Rf18edydDaRBh7t6gHUbuByLbWEoWUTg",
            ... )
            >>> isinstance(res, (dict, list, str))
            True
        """
        # ---- Validate & normalize numerics safely ---------------------------------
        # Ensure snapshot height is an integer to avoid daemon parse errors.
        try:
            height_str = str(int(snapshot_height))
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

        # Preserve precision for the gross amount (Decimal if available).
        try:
            from decimal import Decimal
            if isinstance(gross_distribution_amount, float):
                gross_str = str(Decimal(str(gross_distribution_amount)))
            elif isinstance(gross_distribution_amount, Decimal):
                gross_str = str(gross_distribution_amount)
            else:
                gross_str = str(gross_distribution_amount)
        except Exception:
            gross_str = str(gross_distribution_amount)

        # ---- Build the CLI command in exact positional order ----------------------
        command = self._build_command() + [
            "getdistributestatus",
            str(asset_name),  # 1: source asset
            height_str,  # 2: snapshot height
            str(distribution_asset_name),  # 3: asset being distributed (or "EVR")
            gross_str,  # 4: gross distribution amount
        ]

        # Slot 5 is optional: exception_addresses (comma-separated string)
        if exception_addresses is not None:
            command.append(str(exception_addresses))

        try:
            # Execute the RPC. Non-zero exit status raises; we standardize the error below.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Prefer JSON parsing; return native Python (dict/list/etc.) if possible.
            try:
                parsed = json.loads(out)
                return parsed
            except json.JSONDecodeError:
                # Not JSON—return the raw string so the caller sees exactly what the node said.
                return out

        except Exception as e:
            # Standard error surface: prefer daemon stderr if present.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getsnapshotrequest(self, asset_name, block_height):
        """
        Retrieve the details for a previously scheduled snapshot request.

        Invokes the `getsnapshotrequest` RPC to fetch the snapshot record identified by
        (`asset_name`, `block_height`). Useful to confirm that a snapshot is queued and to
        inspect its stored parameters.

            getsnapshotrequest "asset_name" block_height

        Args:
            asset_name (str):
                The on-chain asset name the snapshot pertains to (e.g., "TRONCO").
            block_height (int | str):
                The chain height of the scheduled snapshot. Must be an integer height;
                string values are accepted if they cleanly parse to an int.

        Returns:
            dict | str:
                - On success with JSON output: a dict such as:
                  {"asset_name": "<name>", "block_height": <int>}
                - If non-JSON text is returned: that text verbatim.
                - If no output is produced: "No data returned."
                - On error: "Error: <node stderr or exception message>"

        Notes:
            - If the snapshot was not found, the daemon will typically return an error.
            - To create or cancel snapshots, see `requestsnapshot` and `cancelsnapshotrequest`.

        Example:
            >>> rpc = RewardsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                  rpc_user="user", rpc_pass="pass", testnet=True)
            >>> info = rpc.getsnapshotrequest("PHATSTACKS", 34987)
            >>> isinstance(info, (dict, str))
            True
        """
        # --- Normalize & validate the height so we pass a proper integer to the daemon.
        try:
            height_str = str(int(block_height))
        except Exception as e:
            # Surface a clear message if height wasn't an integer.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

        # Build the CLI command with auth/network flags and positional args in exact RPC order.
        command = self._build_command() + [
            "getsnapshotrequest",
            str(asset_name),  # asset name exactly as scheduled
            height_str,  # integer block height
        ]

        try:
            # Execute the RPC; non-zero exit codes raise with stderr captured by subprocess.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Normalize the output (daemon usually returns a small JSON object).
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Prefer JSON parsing; return native Python if possible.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, dict) else str(parsed)
            except json.JSONDecodeError:
                # Not JSON—return raw text so the caller sees exactly what the node said.
                return out

        except Exception as e:
            # Standardized error: prefer daemon stderr when available, otherwise exception text.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def listsnapshotrequests(self, asset_name=None, block_height=None):
        """
        List scheduled snapshot requests, optionally filtered by asset and/or height.

        Invokes the `listsnapshotrequests` RPC to retrieve snapshot request records.
        Both filters are optional. If only `block_height` is provided, this wrapper
        inserts an empty string placeholder for `asset_name` to maintain the RPC's
        positional argument order.

            listsnapshotrequests ["asset_name" [block_height]]

        Args:
            asset_name (str | None, optional):
                Filter to a specific asset name. Use `None` or `""` to include all assets.
            block_height (int | str | None, optional):
                Filter to a specific snapshot height. Use `None` or `0` to include all heights.
                If provided as a string, it must parse cleanly to an integer.

        Returns:
            list[dict] | dict | str:
                - Typically: a list of objects like:
                  `[{"asset_name": "<NAME>", "block_height": <INT>}, ...]`
                - If the daemon returns other JSON (e.g., a dict), that JSON is returned.
                - If non-JSON text is returned: the raw text string.
                - If no output: `"No data returned."`
                - On error: `"Error: <node stderr or exception message>"`

        Notes:
            - **Positional parameters:** If you specify `block_height` but not `asset_name`,
              an empty string `""` is passed as the first optional parameter so that the
              height lands in the correct positional slot.
            - Either filter may be omitted to broaden results.

        Example:
            >>> rpc = RewardsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                  rpc_user="user", rpc_pass="pass", testnet=True)
            >>> # All snapshot requests:
            >>> all_req = rpc.listsnapshotrequests()
            >>> # Requests for one asset at all heights:
            >>> tronco_req = rpc.listsnapshotrequests(asset_name="TRONCO")
            >>> # Requests for any asset at a specific height:
            >>> h_req = rpc.listsnapshotrequests(block_height=345333)
        """
        # --- Build the CLI command in strict positional order ---
        command = self._build_command() + ["listsnapshotrequests"]

        # If neither filter is provided, call with no extra args.
        if asset_name is None and block_height is None:
            pass
        else:
            # Normalize asset_name (empty string means "no asset filter")
            asset_arg = "" if asset_name in (None, "") else str(asset_name)

            if block_height is None:
                # Only asset_name provided
                command.append(asset_arg)
            else:
                # Height provided; ensure it's an integer string
                try:
                    height_str = str(int(block_height))
                except Exception as e:
                    return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

                # Append both args in order (asset placeholder + height)
                command.extend([asset_arg, height_str])

        try:
            # Execute the RPC; non-zero exit codes raise with stderr captured.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Prefer JSON parsing; return native Python (list/dict/etc.) if possible.
            try:
                parsed = json.loads(out)
                return parsed
            except json.JSONDecodeError:
                # Not JSON—return raw text so the caller sees exactly what the node said.
                return out

        except Exception as e:
            # Standardized error surface: prefer daemon stderr when present.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()


    def requestsnapshot(self, asset_name, block_height):
        """
        Schedule a rewards snapshot for an asset at a specific block height.

        Invokes the `requestsnapshot` RPC to queue a snapshot of ownership for `asset_name`
        at `block_height`. This snapshot can later be used by reward distribution routines.

            requestsnapshot "asset_name" block_height

        Args:
            asset_name (str):
                The on-chain asset name to snapshot (e.g., "TRONCO").
            block_height (int | str):
                The chain height at which the snapshot should be taken. Must be an integer
                (string values are accepted if they parse cleanly to an int).

        Returns:
            dict | str:
                - On success with JSON output: a dict like {"request_status": "Added"}.
                - If non-JSON text is returned: that text verbatim.
                - If no output: "No data returned."
                - On error: "Error: <node stderr or exception message>"

        Notes:
            - The snapshot is identified by the pair (asset_name, block_height).
            - To cancel a scheduled snapshot, use `cancelsnapshotrequest(asset_name, block_height)`.

        Example:
            >>> rpc = RewardsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                  rpc_user="user", rpc_pass="pass", testnet=True)
            >>> res = rpc.requestsnapshot("PHATSTACKS", 34987)
            >>> isinstance(res, (dict, str))
            True
        """
        # --- Validate/normalize the height early so we pass a proper integer to the daemon.
        try:
            height_str = str(int(block_height))
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

        # Build the CLI command with auth/network flags and positional args in RPC order.
        command = self._build_command() + [
            "requestsnapshot",
            str(asset_name),  # Asset name to snapshot
            height_str,  # Target block height for the snapshot
        ]

        try:
            # Execute the command; non-zero exit codes raise with stderr captured by subprocess.
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Read and normalize stdout (daemon typically returns a small JSON object).
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Prefer JSON parsing; fall back to raw text if not JSON.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, dict) else str(parsed)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            # Standardized error surface: prefer daemon stderr, fall back to exception text.
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()
