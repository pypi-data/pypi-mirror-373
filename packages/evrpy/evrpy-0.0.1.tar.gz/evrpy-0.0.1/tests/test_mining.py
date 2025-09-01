from evrpy import MiningRPC
from evrpy import BlockchainRPC
from evrpy import MessagesRPC
# Testnet configuration — set these to valid testnet values before running
CLI_PATH = "/home/aethyn/mining/evrmore-2.0.0.test/bin/evrmore-cli"
DATA_DIR = "/home/aethyn/.evrmore-test"
RPC_USER = "neubtrino_testnet"
RPC_PASS = "pass_testnet"
USE_TESTNET = True

rpc = MiningRPC(
    cli_path=CLI_PATH,
    datadir=DATA_DIR,
    rpc_user=RPC_USER,
    rpc_pass=RPC_PASS,
    testnet=USE_TESTNET
)

blockrpc = BlockchainRPC(
    cli_path=CLI_PATH,
    datadir=DATA_DIR,
    rpc_user=RPC_USER,
    rpc_pass=RPC_PASS,
    testnet=USE_TESTNET
)

messagesrpc = MessagesRPC(
    cli_path=CLI_PATH,
    datadir=DATA_DIR,
    rpc_user=RPC_USER,
    rpc_pass=RPC_PASS,
    testnet=USE_TESTNET
)


BLOCKHEX = "020000000001010000000000000000000000000000000000000000000000000000000000000000ffffffff0603404e100101ffffffff0300715a363a00000023210220476a5d2acfc37ac55b1cf3220480cf8755d6557666e6cc37c01381c72aa42fac0029d177060000001976a914ea234ab400ccbb0ae2ec1870a75671104b5bfc0688ac0000000000000000266a24aa21a9ede2f61c3f71d1defd3fa999dfa36953755c690689799962b48bebd836974e8cf90120000000000000000000000000000000000000000000000000000000000000000000000000"



def test_getblocktemplate():

    result = rpc.getblocktemplate(

    )

    print(f"block template\n {result}\n")

    for key in result:
        print(f"{key}: {result[key]}")


def test_getevrprogpowhash():

    get_block = blockrpc.getblock(blockhash=BLOCKHEX, verbosity=2)

    """
    These values are fillers to see if the rpc call works.
    """
    result = rpc.getevrprogpowhash(
        header_hash=get_block['headerhash'],
        mix_hash=get_block['mixhash'],
        nonce=hex(get_block['nonce']),
        height=get_block['height'],
        target=get_block['bits'],
    )

    print(f"result:\n{result}\n")

    for key in result:
        print(f"{key}: {result[key]}")



def test_getmininginfo():

    result = rpc.getmininginfo(

    )

    for key in result:
        print(f"{key}: {result[key]}")


def test_getnetworkhashps():

    result = rpc.getnetworkhashps(
        nblocks=200,
        height=-1
    )

    print(f"network hashes per second: {result}")


def test_pprpcsb():

    get_block = blockrpc.getblock(blockhash=BLOCKHEX, verbosity=2)
    """
    These values are fillers to see if the rpc call works.
    """

    result = rpc.pprpcsb(
        header_hash=get_block['headerhash'],
        mix_hash=get_block['mixhash'],
        nonce=hex(get_block['nonce']),
    )

    print(f"result of pprpcsb:\n{result}")


def test_prioritisetransaction():

    TXID = messagesrpc.sendmessage(
        channel_name="NEUBTRINO_DEFI!",
        ipfs_hash="QmYwhataboutfromherehowmanydoesittakeZdnvkhdzR",
        expire_time=None
    )

    result = rpc.prioritisetransaction(
        txid=f"{TXID[0]}",
        fee_delta=10000 #  this value is in Satoshis
    )

    print(f"result:\n{result}")



def test_submitblock():

    result = rpc.submitblock(
        hexdata=BLOCKHEX
    )

    print(f"dummy block submit result:\n{result}")


if __name__ == "__main__":
    # test_getblocktemplate()
    # test_getevrprogpowhash()
    # test_getmininginfo()
    # test_getnetworkhashps()
    # test_pprpcsb()
    # test_prioritisetransaction()
    test_submitblock()