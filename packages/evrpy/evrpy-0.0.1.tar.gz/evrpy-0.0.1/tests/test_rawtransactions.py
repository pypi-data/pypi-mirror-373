from evrpy import RawtransactionsRPC

# Testnet configuration — set these to valid testnet values before running
CLI_PATH = "/home/aethyn/mining/evrmore-2.0.0.test/bin/evrmore-cli"
DATA_DIR = "/home/aethyn/.evrmore-test"
RPC_USER = "neubtrino_testnet"
RPC_PASS = "pass_testnet"
USE_TESTNET = True

rpc = RawtransactionsRPC(
    cli_path=CLI_PATH,
    datadir=DATA_DIR,
    rpc_user=RPC_USER,
    rpc_pass=RPC_PASS,
    testnet=USE_TESTNET
)


def test_combinerawtransactions():
    print("nothing yet combinerawtransactions")


def test_createrawtransaction():
    print("nothing yet createrawtransaction")

def test_decoderawtransaction():
    print("nothing yet decoderawtransaction")

def test_decodescript():
    print("nothing yet decodescript")

def test_fundrawtransaction():
    print("nothing yet fundrawtransaction")

def test_getrawtransaction():
    print("nothing yet getrawtransaction")

def test_sendrawtransaction():
    print("nothing yet sendrawtransaction")

def test_signrawtransaction():
    print("nothing yet signrawtransaction")

def test_testmempoolaccept():
    print("nothing yet testmempoolaccept")

if __name__ == "__main__":
    test_combinerawtransactions()
    test_createrawtransaction()
    test_decoderawtransaction()
    test_decodescript()
    test_fundrawtransaction()
    test_getrawtransaction()
    test_sendrawtransaction()
    test_signrawtransaction()
    test_testmempoolaccept()