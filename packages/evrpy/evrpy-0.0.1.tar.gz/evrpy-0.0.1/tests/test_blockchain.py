from evrpy import BlockchainRPC

# Testnet configuration — set these to valid testnet values before running
CLI_PATH = "/home/aethyn/mining/evrmore-2.0.0.test/bin/evrmore-cli"
DATA_DIR = "/home/aethyn/.evrmore-test"
RPC_USER = "neubtrino_testnet"
RPC_PASS = "pass_testnet"
USE_TESTNET = True

rpc = BlockchainRPC(
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
BLOCKHEX = "0000005030d3ed0375fcd734ba5786ca7b6569e33648096f110d92d47a659f9b"
BLOCKHASH = "00000080628dfe8a91468b9f836c7da37e0a02376fbf35ac5eaf733867e17657"
HEIGHT = 1068455
HIGH =1749333274
LOW =1749323663
OPTIONS_DICT = {
    "noOrphans": True,
    "logicalTimes": True
}
mempool_ancestor_descendent_txid = "5873125e6d388fc58074da2f0a5019e7deb99f22f14f79d58641468953daa1db"

def test_clearmempool():

    result = rpc.clearmempool(

    )

    print(f'Is the mempool cleared?\n{result}\n')

def test_decodeblock():

    result = rpc.decodeblock(
        blockhex=BLOCKHEX
    )

    for key in result:
        print(f'{key}: {result[key]}')


def test_getbestblockhash():

    result = rpc.getbestblockhash(

    )

    print(f"\nbest block hash:\n{result}")

    return

def test_decodeblock2():

    result = rpc.decodeblock(
        blockhex=test_getbestblockhash()
    )

    # print(f"hex from best block hash returns:\n {result}")
    for key in result:
        print(f'{key}: {result[key]}')

def test_getblock():

    result = rpc.getblock(
        blockhash=BLOCKHEX,
        verbosity=2
    )

    for key in result:
        print(f'{key}: {result[key]}')

    print(f"\nTX LIST\n")

    # This part works with verbosity=2, not verbosity=1
    my_list = result['tx']  #  saves the list for key 'tx' to a variable
    inner_dict = my_list[0]  #  this list contains at least one dictionary
    for key in inner_dict:  #  iterates through key:value pairs in tx dictionary
        print(f'{key}: {inner_dict[key]}')


def test_getblockchaininfo():

     result = rpc.getblockchaininfo(

     )
     for key in result:
         print(f'{key}: {result[key]}')


def test_getblockcount():

    result = rpc.getblockcount(

    )

    print(f'\nthe block count is: {result}\n')


def test_getblockhash():

    result = rpc.getblockhash(
        height=HEIGHT
    )

    print(f'blockhash:\n{result}\n')


def test_getblockhashes():

    result = rpc.getblockhashes(
        high=HIGH,
        low=LOW,
        noOrphans=OPTIONS_DICT["noOrphans"],
        # noOrphans=False,
        logicalTimes=OPTIONS_DICT["logicalTimes"]
        # logicalTimes = False
    )

    print(f'blockhashes:\n{result}')  #  this gives the full return

    #  this iterates through each hash in the list in the dictionary
    result_length = len(result)
    for i in range(result_length):
        print(f"blockhash: {result[i]['blockhash']}")
        print(f"logicalts: {result[i]['logicalts']}\n")


def test_getblockheader():

    result = rpc.getblockheader(
        hash=BLOCKHASH,
        verbose=True
    )

    # print(f'block header:\n{result}')

    for key in result:
        print(f"{key}: {result[key]}")


def test_getchaintips():

    result = rpc.getchaintips(

    )

    print(f"result:\n{result}\n")
    print(f"result specific look:\n{result[0]}\n")

    chaintiplength = len(result)

    for i in range(chaintiplength):
        print("\n")
        for key in result[i]:
            print(f"{key}: {result[i][key]}")

def test_getchaintxstats():

    result1 = rpc.getchaintxstats(
        nblocks=43800,
        blockhash=None
    )

    result2 = rpc.getchaintxstats(
        nblocks=None,
        blockhash=None
    )

    result3 = rpc.getchaintxstats(

    )

    print(f"\nchain tx stats if statement: {result1}\niterating through dict")
    for key in result1:
        print(f"{key}: {result1[key]}")

    print(f"\nchain tx stats elif statement: {result2}\niterating through dict")
    for key in result2:
        print(f"{key}: {result2[key]}")

    print(f"\nchain tx stats else statement: {result3}\niterating through dict")
    for key in result3:
        print(f"{key}: {result3[key]}")


def test_getdifficulty():

    result = rpc.getdifficulty(

    )

    print(f"proof of work difficulty is: {result}")


def test_getmempoolancestors():

    result = rpc.getmempoolancestors(
        txid=mempool_ancestor_descendent_txid,
        verbose=True
    )
    #  This will return an error if the txid is not in the mempool
    print(f"\nmempool ancestors for txid {mempool_ancestor_descendent_txid}:\n{result}\n")


def test_getmempooldescendants():

    result = rpc.getmempooldescendants(
        txid=mempool_ancestor_descendent_txid,
        verbose=True
    )

    print(f"mempool descendants for txid {mempool_ancestor_descendent_txid}:\n{result}\n")


def test_getmempoolentry():

    result = rpc.getmempoolentry(
        txid=mempool_ancestor_descendent_txid
    )

    print(f"\nmempool entry: {mempool_ancestor_descendent_txid}")
    for key in result:
        print(f"{key}: {result[key]}")


def test_getmempoolinfo():

    result = rpc.getmempoolinfo(

    )

    # print(f"mempool info:\n{result}")

    for key in result:
        print(f"{key}: {result[key]}")


def test_getrawmempool():

    result = rpc.getrawmempool(
        verbose=True
    )

    print(f"\nraw mempool: {result}\nIf there is nothing here then there is nothing in the mempool")

    for txid, tx_data in result.items():
        print(f"\nTransaction ID: {txid}")
        for field, value in tx_data.items():
            print(f"  {field}: {value}")


def test_getspentinfo():

    result = rpc.getspentinfo(
        txid="652bc5977e05870c578a9012b9590ee938fc7731bd27e7496cf70244982069e8",
        index=0
    )

    print(f"spent info:\n{result}")



def test_gettxout():

    result = rpc.gettxout(
        txid="5360f6c0c49c32cbbec7f120349169c8eb972d7ca5335a901d18e247d9fc624d",
        n=1,
        include_mempool=True
    )

    print(f"tx out: {result}\n")

    print("components of tx out\n")
    for key in result:
        print(f"{key}: {result[key]}")


def test_gettxoutproof():

    result = rpc.gettxoutproof(
        txids=["e07d5f79fb614555f91a51b16280a3a894154152cad830b1051065b2749560d5"],
        blockhash=BLOCKHASH
    )

    print(f"tx out proof:\n{result}")


def test_gettxoutsetinfo():

    result = rpc.gettxoutsetinfo(

    )

    print(f"tx outset info:\n{result}\n\n\nIterated dictionary\n")

    for key in result:
        print(f"{key}: {result[key]}")


def test_preciousblock():

    result = rpc.preciousblock(
        blockhash=BLOCKHASH
    )

    print(f"precious block:\n{result}")


def test_pruneblockchain():

    result = rpc.pruneblockchain(
        n=100
    )

    print(f"height of last block pruned: {result}")


def test_savemempool():

    result = rpc.savemempool(

    )

    print(f"Where is the mempool?\n {result}")


def test_verifychain():

    result = rpc.verifychain(
        checklevel=4,
        nblocks=6
    )

    print(f"Is the chain verified: {result}")


def test_verifytxoutproof():

    result = rpc.verifytxoutproof(
        proof="000000302761b44990d1047290fccac559b6517fb8d490a46d1fac6fb32024718d000000321222d211ed7bb45fa8dbece5e813243ac0f7ebf28cf1705e2d0e170dd5dca8be0f466820c2001e662cc0010500000004a3d0da59672266a9156d2a269496b3e5fe9cd9c0a7af6f7397d68ae5065e3f51746d56d9a95b3bb5d24e383acfb1aa911af65a689101c0f780ba49fbf1b631039e50a5807ead057890159275cd07673f68bd844bc528364246a497e606eb5b08900aefb7c43eb64785d5f7d0ab8bd663367b1f90bbef7a0e04f67270a3f559fa012b"
    )

    print(f"txid the proof commits to:\n{result}\n\n")

    result_length = len(result)
    print(f"result type: {type(result)}\n\niterating through txids")
    for i in range(result_length):
        print(result[i])


if __name__ == "__main__":
    # test_clearmempool()
    # test_decodeblock()
    # test_getbestblockhash()
    # test_decodeblock2()
    test_getblock()
    # test_getblockchaininfo()
    # test_getblockcount()
    # test_getblockhash()
    # test_getblockhashes()
    # test_getblockheader()
    # test_getchaintips()
    # test_getchaintxstats()
    # test_getdifficulty()
    # test_getmempoolancestors()
    # test_getmempooldescendants()
    # test_getmempoolentry()
    # test_getmempoolinfo()
    # test_getrawmempool()
    # test_getspentinfo()
    # test_gettxout()
    # test_gettxoutproof()
    # test_gettxoutsetinfo()
    # test_preciousblock()
    # test_pruneblockchain()
    # test_savemempool()
    # test_verifychain()
    # test_verifytxoutproof()













