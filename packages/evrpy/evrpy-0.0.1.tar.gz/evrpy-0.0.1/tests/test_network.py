from evrpy import NetworkRPC

# Testnet configuration — set these to valid testnet values before running
CLI_PATH = "/home/aethyn/mining/evrmore-2.0.0.test/bin/evrmore-cli"
DATA_DIR = "/home/aethyn/.evrmore-test"
RPC_USER = "neubtrino_testnet"
RPC_PASS = "pass_testnet"
USE_TESTNET = True

rpc = NetworkRPC(
    cli_path=CLI_PATH,
    datadir=DATA_DIR,
    rpc_user=RPC_USER,
    rpc_pass=RPC_PASS,
    testnet=USE_TESTNET
)

def test_addnode():

    result = rpc.addnode(
        node="74.208.127.203:18820",
        node_command="add"
    )

    print(f"result:\n{result}")


def test_clearbanned():

    result = rpc.clearbanned(

    )

    print(f"result: {result}")


def test_disconnectnode():

    result = rpc.disconnectnode(
        # ip_address="74.208.127.203:18820",
        ip_address=None,
        node_id=2
    )

    print(f"node disconnection: {result}")


def test_getaddednodeinfo():

    result = rpc.getaddednodeinfo(
        ip_address=None
        # ip_address="74.208.127.203:18820",
    )

    print(f"added node(s) information\n{result}\n\nbelow is iterated information\n")

    result_length = len(result)
    for i in range(result_length):
        for key in result[i]:
            print(f"{key}: {result[i][key]}")


def test_getconnectioncount():

    result = rpc.getconnectioncount(

    )

    print(f"result:\n{result}")


def test_getnettotals():

    result = rpc.getnettotals(

    )

    print(f"result:\n {result}\n\niterated results\n")

    for key in result:
        print(f"{key}: {result[key]}")


    print(f"\nupload target\n{result['uploadtarget']}\n\niterated upload target\n")

    for key in result['uploadtarget']:
        print(f'{key}: {result["uploadtarget"]}')



def test_getnetworkinfo():

    result = rpc.getnetworkinfo(

    )

    for key in result:
        print(f"{key}: {result[key]}")


def test_getpeerinfo():

    result = rpc.getpeerinfo(

    )

    print(f"result:\n{result}\n\niterated example")

    result_length = len(result)
    for i in range(result_length):
        for key in result[i]:
            print(f"{key}: {result[i][key]}")


def test_listbanned():

    result = rpc.listbanned(

    )

    print(f"result:\n{result}")


def test_ping():

    result = rpc.ping(

    )

    print(f"result:\n{result}")


def test_setban():

    result = rpc.setban(
        subnet="74.208.127.203",
        rpc_command="remove",
        bantime=None,
        absolute=None
    )

    print(f"result: {result}")

def test_setnetworkactive():

    result = rpc.setnetworkactive(
        state=True
    )

    print(f'result:\n{result}')

if __name__ == "__main__":
    # test_addnode()
    # test_clearbanned()
    # test_disconnectnode()
    # test_getaddednodeinfo()
    # test_getconnectioncount()
    # test_getnettotals()
    # test_getnetworkinfo()
    # test_getpeerinfo()
    # test_listbanned()
    # test_ping()
    # test_setban()
    test_setnetworkactive()