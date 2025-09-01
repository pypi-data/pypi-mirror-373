from evrpy import GeneratingRPC

# Testnet configuration — set these to valid testnet values before running
CLI_PATH = "/home/aethyn/mining/evrmore-2.0.0.test/bin/evrmore-cli"
DATA_DIR = "/home/aethyn/.evrmore-test"
RPC_USER = "neubtrino_testnet"
RPC_PASS = "pass_testnet"
USE_TESTNET = True

rpc = GeneratingRPC(
    cli_path=CLI_PATH,
    datadir=DATA_DIR,
    rpc_user=RPC_USER,
    rpc_pass=RPC_PASS,
    testnet=USE_TESTNET
)


def test_generate():

    result = rpc.generate(
        nblocks=4,
        maxtries=1000000000
    )

    print(f"hashes of found blocks:\n{result}")

    num_blocks = len(result)

    for i in range(num_blocks):
        print(result[i])


def test_generatetoaddress():

    result = rpc.generatetoaddress(
        nblocks=4,
        address="n2drG5vkvkgyXDbgYLAJHcriR2bfitXE6C",
        maxtries=1000000000
    )

    result_length = len(result)
    for i in range(result_length):
        print(result[i])


def test_getgenerate():

    result = rpc.getgenerate(

    )

    print(f" result: {result}")


def test_setgenerate():

    result = rpc.setgenerate(
        generate=False,
        num_processors=2
    )

    print(f"result:\n{result}")


if __name__ == "__main__":
    # test_generate()
    # test_generatetoaddress()
    # test_getgenerate()
    test_setgenerate()