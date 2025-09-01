# evrpy

> A thin, pragmatic Python wrapper around `evrmore-cli` for Evrmore (EVR) nodes.



## Why?

When you're working against a running `evrmored` node, sometimes you just want a clean Python API that mirrors the CLI *exactly*, without managing JSON-RPC servers, auth headers, or transport details. `evrpy` shells out to `evrmore-cli` with the flags you provide and returns the output (or a readable error string) so you can focus on your app logic.



## Features

- Batteries-included clients grouped by RPC domain (Wallet, Raw Transactions, Assets, Restricted, Rewards, Blockchain, Mining, Mempool, Network, Util, Address Index, Node).

- Mirrors the `evrmore-cli` help text and semantics.

- Predictable error handling — returns strings like `Error: <message>` instead of raising, so you can bubble up user-friendly errors.

- Works with **testnet** or **mainnet**, plus custom `-datadir`, `-rpcuser`, `-rpcpassword`.





## Requirements

- Python 3.9+

- A running `evrmored` with matching `evrmore-cli` on your PATH (or provide a full path).

- RPC enabled in your node config (the wrapper passes `-rpcuser`/`-rpcpassword`).

- For some endpoints you may need node indexes enabled, e.g.:

  - `-txindex=1` for `getrawtransaction` on historical txns

  - `-assetindex=1` for asset queries

  - `-addressindex=1` for address index calls



## Quickstart

```python

from evrpy import WalletRPC



rpc = WalletRPC(

    cli_path="evrmore-cli",               # or absolute path

    datadir="/home/you/.evrmore-test",    # your datadir

    rpc_user="username",

    rpc_password="password",

    testnet=True,

)



info = rpc.getwalletinfo()

print(info)

```



### Example: `sendmany` with fee split

```python

txid = rpc.sendmany(

    fromaccount="",  # deprecated in node, keep empty string

    amounts={

        "n3pUp4uT58hTtATHGvmkBsGP9tzMn8ZAQs": 1,

        "mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF": 1,

    },

    minconf=0,

    comment="example",

    subtractfeefrom=[

        "n3pUp4uT58hTtATHGvmkBsGP9tzMn8ZAQs",

        "mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF",

    ],

    conf_target=None,           # omit for now (see Known quirks)

    estimate_mode=None,

)

print(txid)

```



## Known node quirks

- `sendtoaddress` and `sendmany`: on Evrmore v2.0.0 (testnet), passing `conf_target` (even as an integer) sometimes triggers `JSON value is not an integer as expected`. Workaround: **omit `conf_target` and `estimate_mode`** — the wrapper will exclude them if `None`.

- CLI JSON vs shell quoting: when calling the CLI directly, ensure JSON objects/arrays are **single-quoted** to avoid shell expansion.



## API surface

Below is a generated snapshot of available clients and methods. Each method maps 1:1 to an `evrmore-cli` command and returns the CLI stdout on success, or a string beginning with `Error:` on failure.

### AddressindexRPC

A client for interacting with the Evrmore node's address index RPC commands via the `evrmore-cli` command-line interface.

This class provides functions for querying indexed blockchain data by address, such as balance, UTXO sets, mempool data,
and transaction IDs associated with given addresses. It is designed to work with an Evrmore node that has address index
functionality enabled.

Attributes:
    cli_path (str): Path to the `evrmore-cli` binary.
    datadir (str): Directory containing the Evrmore blockchain data.
    rpc_user (str): RPC username for node authentication.
    rpc_pass (str): RPC password for node authentication.
    testnet (bool): If True, connects to Evrmore testnet instead of mainnet.

Typical usage example:
    rpc = AddressindexRPC(
        cli_path="/usr/bin/evrmore-cli",
        datadir="/home/user/.evrmore",
        rpc_user="rpcusername",
        rpc_pass="rpcpassword",
        testnet=True
    )
    balance = rpc.getaddressbalance("EVRaddress")

**Methods (5):** getaddressbalance, getaddressdeltas, getaddressmempool, getaddresstxids, getaddressutxos



### AssetRPC

AssetRPC provides an interface for interacting with the Evrmore blockchain assets via the `evrmore-cli` command-line tool.

This class wraps common asset-related RPC commands and parses their responses, allowing you to manage, query, and transfer assets on the Evrmore blockchain. It handles command construction, execution, and result parsing, with support for both mainnet and testnet modes.

Attributes:
    cli_path (str): Path to the `evrmore-cli` binary.
    datadir (str): Path to the Evrmore node data directory.
    rpc_user (str): RPC authentication username.
    rpc_pass (str): RPC authentication password.
    testnet (bool): Run commands on testnet if True; mainnet otherwise.

Example:
    rpc = AssetRPC(
        cli_path="/path/to/evrmore-cli",
        datadir="/path/to/data",
        rpc_user="user",
        rpc_pass="password",
        testnet=True
    )

    asset_info = rpc.getassetdata("ASSETNAME")

Methods provide access to:
    - Checking if an address has a specified asset balance.
    - Querying asset metadata.
    - Getting burn addresses.
    - Retrieving cache information.
    - Calculating tolls for asset transactions.
    - Issuing, reissuing, transferring, and updating asset metadata.
    - Listing assets and balances.
    - Other asset operations supported by Evrmore CLI.

**Methods (17):** addresshasasset, getassetdata, getburnaddresses, getcacheinfo, getcalculatedtoll, issue, issueunique, listaddressesbyasset, listassetbalancesbyaddress, listassets, listmyassets, reissue, remint, transfer, transferfromaddress, transferfromaddresses, updatemetadata



### BlockchainRPC

**Methods (26):** clearmempool, decodeblock, getbestblockhash, getblock, getblockchaininfo, getblockcount, getblockhash, getblockhashes, getblockheader, getchaintips, getchaintxstats, getdifficulty, getmempoolancestors, getmempooldescendants, getmempoolentry, getmempoolinfo, getrawmempool, getspentinfo, gettxout, gettxoutproof, gettxoutsetinfo, preciousblock, pruneblockchain, savemempool, verifychain, verifytxoutproof



### ControlRPC

**Methods (6):** getinfo, getmemoryinfo, getrpcinfo, help, stop, uptime



### GeneratingRPC

**Methods (4):** generate, generatetoaddress, getgenerate, setgenerate



### MessagesRPC

**Methods (6):** clearmessages, sendmessage, subscribetochannel, unsubscribefromchannel, viewallmessagechannels, viewallmessages



### MiningRPC

**Methods (7):** getblocktemplate, getevrprogpowhash, getmininginfo, getnetworkhashps, pprpcsb, prioritisetransaction, submitblock



### NetworkRPC

**Methods (12):** addnode, clearbanned, disconnectnode, getaddednodeinfo, getconnectioncount, getnettotals, getnetworkinfo, getpeerinfo, listbanned, ping, setban, setnetworkactive



### RawtransactionsRPC
NEEDS EXTENSIVE TESTING

**Methods (9):** combinerawtransaction, createrawtransaction, decoderawtransaction, decodescript, fundrawtransaction, getrawtransaction, sendrawtransaction, signrawtransaction, testmempoolaccept



### RestrictedassetsRPC
NEEDS FURTHER TESTING

**Methods (19):** addtagtoaddress, checkaddressrestriction, checkaddresstag, checkglobalrestriction, freezeaddress, freezerestrictedasset, getverifierstring, issuequalifierasset, issuerestrictedasset, isvalidverifierstring, listaddressesfortag, listaddressrestrictions, listglobalrestrictions, listtagsforaddress, reissuerestrictedasset, removetagfromaddress, transferqualifier, unfreezeaddress, unfreezerestrictedasset



### RestrictedRPC

**Methods (2):** viewmyrestrictedaddresses, viewmytaggedaddresses



### RewardsRPC

**Methods (6):** cancelsnapshotrequest, distributereward, getdistributestatus, getsnapshotrequest, listsnapshotrequests, requestsnapshot



### UtilRPC

**Methods (6):** createmultisig, estimatefee, estimatesmartfee, signmessagewithprivkey, validateaddress, verifymessage



### WalletRPC

**Methods (48):** abandontransaction, abortrescan, addmultisigaddress, addwitnessaddress, backupwallet, dumpprivkey, dumpwallet, encryptwallet, getaccount, getaccountaddress, getaddressesbyaccount, getbalance, getmasterkeyinfo, getmywords, getnewaddress, getrawchangeaddress, getreceivedbyaccount, getreceivedbyaddress, gettransaction, getunconfirmedbalance, getwalletinfo, importaddress, importmulti, importprivkey, importprunedfunds, importpubkey, importwallet, keypoolrefill, listaccounts, listaddressgroupings, listlockunspent, listreceivedbyaccount, listreceivedbyaddress, listsinceblock, listtransactions, listunspent, listwallets, lockunspent, move, removeprunedfunds, rescanblockchain, sendfrom, sendfromaddress, sendmany, sendtoaddress, setaccount, settxfee, signmessage



## Error handling

Most client methods wrap `subprocess.CalledProcessError` and format errors as readable strings so you can surface them directly to users:

```python

return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

```
The methods that do not currently have this output will be updated.  They currently just return the error e




Note: Many tests expect a synced node with funds and appropriate indexes enabled.



## Contributing

PRs welcome! If you spot mismatches with CLI help or encounter args that the node rejects (e.g. `conf_target`), please include:

- The exact CLI you ran and its output

- The wrapper call and its return value

- Node version and network (mainnet/testnet)



## License

MIT © 2025 neubtrino