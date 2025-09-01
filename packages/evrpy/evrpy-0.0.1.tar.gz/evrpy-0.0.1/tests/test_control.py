from evrpy import ControlRPC

# Testnet configuration — set these to valid testnet values before running
CLI_PATH = "/home/aethyn/mining/evrmore-2.0.0.test/bin/evrmore-cli"
DATA_DIR = "/home/aethyn/.evrmore-test"
RPC_USER = "neubtrino_testnet"
RPC_PASS = "pass_testnet"
USE_TESTNET = True

rpc = ControlRPC(
    cli_path=CLI_PATH,
    datadir=DATA_DIR,
    rpc_user=RPC_USER,
    rpc_pass=RPC_PASS,
    testnet=USE_TESTNET
)


def test_getinfo():

    result = rpc.getinfo(

    )

    print(f"getinfo: {result}")

    for key in result:
        print(f"{key}: {result[key]}")


def test_getmemoryinfo():

    result = rpc.getmemoryinfo(
        mode="stats"
    )

    for key in result:
        for key2 in result[key]:
            print(f"{key2}: {result[key][key2]}")


def test_getrpcinfo():

    result = rpc.getrpcinfo(

    )

    print(f"rpc info: {result}\n")

    active_commands_length = len(result['active_commands'])

    for i in range(active_commands_length):
        for key in result['active_commands'][i]:
            print(f"{key}: {result['active_commands'][i][key]}")


def test_help():

    result = rpc.help(
        rpccall=None
    )

    print(f"help result:\n{result}")


def test_stop():

    result = rpc.stop(

    )

    print(f"server status:\n{result}")


def test_uptime():

    result = rpc.uptime(

    )

    print(f"uptime dd:hh:mm:ss is {result}")

if __name__ == "__main__":
    # test_getinfo()
    # test_getmemoryinfo()
    # test_getrpcinfo()
    # test_help()
    # test_stop() # this will stop your server and you will have to restart it
    test_uptime()

