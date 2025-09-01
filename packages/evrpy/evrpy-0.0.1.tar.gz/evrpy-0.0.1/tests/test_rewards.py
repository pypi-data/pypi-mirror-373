from evrpy import RewardsRPC

# Testnet configuration — set these to valid testnet values before running
CLI_PATH = "/home/aethyn/mining/evrmore-2.0.0.test/bin/evrmore-cli"
DATA_DIR = "/home/aethyn/.evrmore-test"
RPC_USER = "neubtrino_testnet"
RPC_PASS = "pass_testnet"
USE_TESTNET = True

rpc = RewardsRPC(
    cli_path=CLI_PATH,
    datadir=DATA_DIR,
    rpc_user=RPC_USER,
    rpc_pass=RPC_PASS,
    testnet=USE_TESTNET
)

def test_cancelsnapshotrequest():

    result = rpc.cancelsnapshotrequest(
        asset_name="PHATSTACKS",
        block_height=34987
    )

    print(f'result: {result}')

def test_distributereward():

    result = rpc.distributereward(
        asset_name="NEUBTRINO_DEFI",
        snapshot_height=1179625,
        distribution_asset_name="EVR",
        gross_distribution_amount=10000,
        exception_addresses=None,
        change_address=None,
        dry_run=None,
    )

    print(f'result: {result}')

def test_requestsnapshot():

    result = rpc.requestsnapshot(
        asset_name="NEUBTRINO_DEFI",
        block_height=1179625
    )

    print(f'result: {result}')

def test_getdistributestatus():

    result = rpc.getdistributestatus(
        asset_name="NEUBTRINO_DEFI",
        snapshot_height=1179625,
        distribution_asset_name="EVR",
        gross_distribution_amount=10000,
    )

    print(f'result: {result}')
    print(f'\niterated result')
    for key, value in result.items():
        print(f'{key}: {value}')


def test_getsnapshotrequest():

    result = rpc.getsnapshotrequest(
        asset_name="NEUBTRINO_DEFI",
        block_height=1179625
    )

    print(f'result: {result}')


def test_listsnapshotrequest():

    result = rpc.listsnapshotrequests(
        asset_name="NEUBTRINO_DEFI",
        block_height=1179625
    )
if __name__ == "__main__":
    # test_cancelsnapshotrequest()
    # test_distributereward()
    # test_requestsnapshot()
    # test_getdistributestatus()
    test_getsnapshotrequest()