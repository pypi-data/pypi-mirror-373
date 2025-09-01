from evrpy import RestrictedRPC

# Testnet configuration — set these to valid testnet values before running
CLI_PATH = "/home/aethyn/mining/evrmore-2.0.0.test/bin/evrmore-cli"
DATA_DIR = "/home/aethyn/.evrmore-test"
RPC_USER = "neubtrino_testnet"
RPC_PASS = "pass_testnet"
USE_TESTNET = True

rpc = RestrictedRPC(
    cli_path=CLI_PATH,
    datadir=DATA_DIR,
    rpc_user=RPC_USER,
    rpc_pass=RPC_PASS,
    testnet=USE_TESTNET
)

def test_viewmyrestrictedaddresses():

    result = rpc.viewmyrestrictedaddresses(

    )

    print(f'my restricted addresses:\n{result}')


def test_viewmytaggedaddresses():

    result = rpc.viewmytaggedaddresses(

    )

    print(f'my tagged addresses:\n{result}')

if __name__ == "__main__":
    test_viewmyrestrictedaddresses()
    test_viewmytaggedaddresses()
