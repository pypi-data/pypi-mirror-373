"""
Unit test for WalletRPC using testnet configuration.

This test assumes that `evrmored` is running in testnet mode and that
the test addresses and assets exist with appropriate balances.

Note:
- No mocking is used. This will execute a real transaction on testnet.
- Use with caution and only on testnet.
"""

from evrpy import AddressindexRPC
import random

# Testnet configuration — set these to valid testnet values before running
CLI_PATH = "/home/aethyn/mining/evrmore-2.0.0.test/bin/evrmore-cli"
DATA_DIR = "/home/aethyn/.evrmore-test"
RPC_USER = "neubtrino_testnet"
RPC_PASS = "pass_testnet"
USE_TESTNET = True

rpc = AddressindexRPC(
    cli_path=CLI_PATH,
    datadir=DATA_DIR,
    rpc_user=RPC_USER,
    rpc_pass=RPC_PASS,
    testnet=USE_TESTNET
)

FROM_ADDRESS = "mgi2ZK972fgzPYkkXUpGp4CDni3nqEeo3k"
TO_ADDRESS = "mpBNmmYYqxYAJK9UPnU5n7XJ3HcTjhrch1"
INCLUDE_ASSETS = [True, False]
SATOSHI_VALUE_CONVERTER = 10**(-8)

def test_getaddressbalance():
    asset_inclusion = random.choice(INCLUDE_ASSETS)
    address = FROM_ADDRESS
    print(asset_inclusion)
    result = rpc.getaddressbalance(
        address=address,
        includeassets=asset_inclusion
    )


    if asset_inclusion:
        for i in range(len(result)):
            print(f'Address: {address}\n'
                  f'Asset Name: {result[i]["assetName"]}\n'
                  f'Balance: {result[i]["balance"]*SATOSHI_VALUE_CONVERTER}\n'
                  f'Received: {result[i]["received"]*SATOSHI_VALUE_CONVERTER}\n\n')

    else:
        print(f"\nEVR balance information for {address}:\n"
              f"EVR Balance  = {result['balance']*SATOSHI_VALUE_CONVERTER}\n"
              f"EVR Balance  = {result['received']*SATOSHI_VALUE_CONVERTER}\n"
              f"\nfull result below(NOT converted from satoshis):\n{result}")


def test_getaddressdeltas():
    address = FROM_ADDRESS
    result = rpc.getaddressdeltas(
        address=address,
        start=1,
        end=1062559,
        chaininfo="True",
        assetname="Neubtrino"
    )

    print(f'address deltas:\n{result}')


def test_getaddressmempool():
    address = FROM_ADDRESS
    result = rpc.getaddressmempool(
        address=address,
        includeassets=True
    )

    print(f'address mempool:\n{result}')


def test_getaddresstxids():
    address = FROM_ADDRESS
    result = rpc.getaddresstxids(
        address=address,
        includeassets=True
    )

    print(f'address TXIDs:\n{result}')


def test_getaddressutxos():
    address = FROM_ADDRESS
    result = rpc.getaddressutxos(
        address=address,
        chaininfo=True,
        assetname='*'
    )

    print(f'address UTXOs:\n{result}')




if __name__ == "__main__":
    test_getaddressbalance()
    test_getaddressdeltas()
    test_getaddressmempool()
    test_getaddresstxids()
    test_getaddressutxos()