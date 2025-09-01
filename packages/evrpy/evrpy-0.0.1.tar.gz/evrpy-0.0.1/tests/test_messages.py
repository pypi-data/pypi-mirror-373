from evrpy import MessagesRPC

# Testnet configuration — set these to valid testnet values before running
CLI_PATH = "/home/aethyn/mining/evrmore-2.0.0.test/bin/evrmore-cli"
DATA_DIR = "/home/aethyn/.evrmore-test"
RPC_USER = "neubtrino_testnet"
RPC_PASS = "pass_testnet"
USE_TESTNET = True

rpc = MessagesRPC(
    cli_path=CLI_PATH,
    datadir=DATA_DIR,
    rpc_user=RPC_USER,
    rpc_pass=RPC_PASS,
    testnet=USE_TESTNET
)


def test_clearmessages():

    result = rpc.clearmessages(

    )

    print(f"result: {result}")


def test_sendmessage():

    result = rpc.sendmessage(
        channel_name="NEUBTRINO_DEFI!",
        ipfs_hash="QmYwhataboutfromherehowmanydoesittakeZdnvkhdzR",
        expire_time=None
    )

    print(f"result:\n{result[0]}")


def test_subscribetochannel():

    result = rpc.subscribetochannel(
        channel_name="NEUBTRINO_DEFI"
    )

    print(f"result: {result}")


def test_unsubscribefromchannel():

    result = rpc.unsubscribefromchannel(
        channel_name="NEUBTRINO_DEFI"
    )

    print(f"result: {result}")


def test_viewallmessagechannels():

    result = rpc.viewallmessagechannels(

    )

    print(f"result:\n{result}")

    result_length = len(result)
    for i in range(result_length):
        print(result[i])


def test_viewallmessages():

    result = rpc.viewallmessages(

    )

    result_length = len(result)
    for i in range(result_length):
        # print(result[i])
        print(f"\n")
        for key in result[i]:
            print(f"{key}: {result[i][key]}")

if __name__ == "__main__":
    # test_clearmessages()
    test_sendmessage()
    # test_subscribetochannel()
    # test_unsubscribefromchannel()
    # test_viewallmessagechannels()
    # test_viewallmessages()