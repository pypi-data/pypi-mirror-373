"""
Base command builder for Evrmore CLI interactions.

This module provides a shared function for constructing the base
`evrmore-cli` command with authentication and network settings.
It is used by all RPC classes to maintain consistent CLI invocation.
"""

def build_base_command(cli_path, datadir, rpc_user, rpc_pass, testnet=True):
    """
    Build the base Evrmore CLI command.

    Parameters:
        cli_path (str): Full path to the `evrmore-cli` binary.
        datadir (str): Path to the Evrmore data directory.
        rpc_user (str): RPC username for authentication.
        rpc_pass (str): RPC password for authentication.
        testnet (bool): Whether to include the `-testnet` flag.

    Returns:
        list: A list of command-line arguments to pass to subprocess.
    """
    command = [
        cli_path,
        f"-datadir={datadir}",
        f"-rpcuser={rpc_user}",
        f"-rpcpassword={rpc_pass}",
    ]
    if testnet:
        command.append("-testnet")
    return command