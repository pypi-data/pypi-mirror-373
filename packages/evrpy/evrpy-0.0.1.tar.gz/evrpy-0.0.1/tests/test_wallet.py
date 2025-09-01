from evrpy import WalletRPC

# Testnet configuration — set these to valid testnet values before running
CLI_PATH = "/home/aethyn/mining/evrmore-2.0.0.test/bin/evrmore-cli"
DATA_DIR = "/home/aethyn/.evrmore-test"
RPC_USER = "neubtrino_testnet"
RPC_PASS = "pass_testnet"
USE_TESTNET = True

rpc = WalletRPC(
    cli_path=CLI_PATH,
    datadir=DATA_DIR,
    rpc_user=RPC_USER,
    rpc_pass=RPC_PASS,
    testnet=USE_TESTNET
)

def test_abandontransaction():
    TXID = test_sendtoaddress()

    result = rpc.abandontransaction(
        txid= f"{TXID}"
    )
    print(f'abandon transaction: {TXID}\nresult: {result}')


def test_sendtoaddress():

    result = rpc.sendtoaddress(
        address="n4iLxDUVRsJrf4824Wdur2nVoZDAtGUtEv", # VPS address
        amount="1",
        comment="wen moon",
        comment_to="EVR v2.0.0 testnet",
        subtractfeefromamount=False,
        # conf_target="10",
        # estimate_mode="CONSERVATIVE"
    )

    print(f'txid:\n{result}')

    return result


def test_abortrescan():

    result = rpc.abortrescan(

    )
    print(f'abort rescan: {result}')

def test_addmultisigaddress():
    addresses_for_keys = ["mykyeu5VtJACsWiPytouAH6MRkqq5VmvsE", "mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF"]

    result = rpc.addmultisigaddress(
        nrequired=2,
        keys=addresses_for_keys,
        account="test"
    )
    print(f'multisig address: {result}\nwith signature addresses below')
    i = 1
    for addy in addresses_for_keys:
        print(f'address {i}: {addy}')
        i += 1

def test_addwitnessaddress():

    result = rpc.addwitnessaddress(
        address="mykyeu5VtJACsWiPytouAH6MRkqq5VmvsE"
    )

    print(f'witness address: {result}')

def test_backupwallet():
    DESTINATION="/tmp/evr_wallet_backup.dat"

    result = rpc.backupwallet(
        destination=DESTINATION
    )
    print(f'wallet backed up to destination {DESTINATION}\n{result}')

def test_dumpprivkey():
    ADDRESS = "mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF"

    result = rpc.dumpprivkey(
        address=ADDRESS
    )
    print(f'private key for address {ADDRESS}\n{result}')

def test_dumpwallet():
    DESTINATION="/tmp/evr_wallet_dump2.txt"

    result = rpc.dumpwallet(
        filename=DESTINATION
    )
    print(f'wallet dumped to destination {DESTINATION}\n{result}')
    print(f'\n\n(using the result as a key:value pair)\nwallet dumped to {result["filename"]}')

####################### not tested yet because 'walletpassphrase' is not clear ##########################
def test_encryptwallet():

    result = rpc.encryptwallet(
        passphrase="encryptMe"
    )

    print(f'wallet encryption initiated; node is shutting down.\n{result}')
#########################################################################################################

def test_getaccount():
    ADDRESS = "mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF"
    result = rpc.getaccount(
        address=ADDRESS
    )
    print(f'account for address {ADDRESS}\n{result}')

def test_getaccountaddress():
    NAME = "test"
    result = rpc.getaccountaddress(
        account=NAME
    )
    print(f'account address for account: {NAME}\n{result}')

def test_getaddressesbyaccount():
    NAME = "test"
    result = rpc.getaddressesbyaccount(
        account=NAME
    )
    print(f'addresses for account: {NAME}\n{result}\n')

    for addy in result:
        print(f'{addy}')

def test_getbalance():
    NAME = "test"
    result_account = rpc.getbalance(
        account=NAME
    )

    result = rpc.getbalance(

    )
    print(f'balance for wallet: \n{result} EVR\n')
    print(f'balance for account {NAME}:\n{result_account} EVR')

def test_getmasterkeyinfo():

    result = rpc.getmasterkeyinfo(

    )
    print(f'master key info:\n{result}\n')

    for key, value in result.items():
        print(f'{key}: {value}')

def test_getmywords():

    result = rpc.getmywords(

    )

    print(f'my words are: {result}')
    for key, value in result.items():
        print(f'\n{key}:\n{value}')

def test_getnewaddress():
    ACCOUNT = "getNewAddressAccount"
    result = rpc.getnewaddress(
        account=ACCOUNT
    )

    print(f'new address: {result}\nfor account: {ACCOUNT}')

def test_getrawchangeaddress():

    result = rpc.getrawchangeaddress(

    )

    print(f'new raw change address: {result}')

def test_getreceivedbyaccount():
    ACCOUNT = "getNewAddressAccount"
    result = rpc.getreceivedbyaccount(
        account=ACCOUNT,
        minconf=6
    )

    print(f'result for account {ACCOUNT}:\n{result}')

def test_getreceivedbyaddress():

    ADDRESS = "mtDqJjCEANbov6ipuQC7cL2AqRGT2rhacx"
    result = rpc.getreceivedbyaddress(
        address=ADDRESS,
        minconf=10
    )

    print(f'result for address {ADDRESS}:\n{result}')

def test_gettransaction():
    TXID = "03bd991b3fd2232609e73474a0cc02f1b22e0f7cca6245ce79021d33201f9bc6"
    result = rpc.gettransaction(
        txid=TXID,
        include_watchonly=None
    )

    print(f'result for transaction {TXID}:\n{result}\n')
    print(f'iterated results version')
    for key, value in result.items():
        print(f'{key}: {value}')

def test_getunconfirmedbalance():

    result = rpc.getunconfirmedbalance(

    )

    print(f'unconfirmed balance:\n{result}')

def test_getwalletinfo():

    result = rpc.getwalletinfo(

    )

    print(f'wallet info:\n{result}\n')
    print(f'iterated wallet info')
    for key, value in result.items():
        print(f'{key}: {value}')

def test_importaddress():
    ADDRESS = "n4iLxDUVRsJrf4824Wdur2nVoZDAtGUtEv"
    result = rpc.importaddress(
        address_or_script=ADDRESS,
        label="label",
        rescan=True,
        p2sh=False
    )

    print(f'imported address {ADDRESS}:\n{result}')


def test_importmulti():
    ADDR1 = "n3pUp4uT58hTtATHGvmkBsGP9tzMn8ZAQs"
    ADDR2 = "n3WJQJEDuJXvbSDrntZGKePgKHJXBfuN92"

    requests = [
        {
            "scriptPubKey": {"address": ADDR1},
            "timestamp": "now",      # skip historical scan for this address
            "label": "label-1",
            "watchonly": True
        },
        {
            "scriptPubKey": {"address": ADDR2},
            "timestamp": 0,          # scan full chain history for this address
            "label": "label-2",
            "watchonly": True
        }
    ]

    options = {
        "rescan": False             # set True if you actually want to rescan now
    }

    result = rpc.importmulti(
        requests=requests,
        options=options
    )

    print(f'imported addresses {ADDR1}, {ADDR2}:\n{result}\n')
    print(f'iterated result')
    for result_dict in result:
        print(f'result_dict: {result_dict}')
        for key, value in result_dict.items():
            print(f'{key}: {value}')



def test_importprivkey():
    PRIVKEY = "PRIVKEY"
    result = rpc.importprivkey(
        privkey=PRIVKEY,
        label=None,
        rescan=False
    )

    print(f'imported private key {PRIVKEY}:\n{result}')


def test_importprunedfunds():

    result = rpc.importprunedfunds(
        rawtransaction="RAW_TRANSACTION_HEX",
        txoutproof="TXOUTPROOF_HEX"
    )

    print(f'imported pruned funds:\n{result}')


def test_importpubkey():
    PUBKEY='pubkey'
    result=rpc.importpubkey(
        pubkey=PUBKEY
    )

    print(f'pubkey {PUBKEY} imported:\n{result}')


def test_importwallet():

    result = rpc.importwallet(
        filename="/tmp/evr_wallet_dump.txt"
    )

    print(f'wallet imported:\n{result}')

def test_keypoolrefill():

    result = rpc.keypoolrefill(
        newsize=200
    )

    print(f'keypool refilled:\n{result}')

def test_listaccounts():

    result = rpc.listaccounts(
        minconf=1,
        include_watchonly=True
    )

    print(f'accounts listed:\n{result}\n')
    print(f'iterated result')
    for key, value in result.items():
        print(f'{key}: {value}')

def test_listaddressgroupings():

    result = rpc.listaddressgroupings(

    )

    print(f'address groupings:\n{result}\n')
    print(f'iterated result')
    for group in result:
        for entry in group:
            print(f'  address: {entry[0]} balance: {entry[1]} EVR')


def test_listlockunspent():

    result = rpc.listlockunspent(

    )

    print(f'list lock unspent:{result}')

def test_listreceivedbyaccount():

    result = rpc.listreceivedbyaccount(
        minconf=10,
        include_empty=None,
        include_watchonly=None
    )

    print(f'list received by account result:\n{result}')


def test_listreceivedbyaddress():
    result = rpc.listreceivedbyaddress(
        minconf=10,
        include_empty=None,
        include_watchonly=None
    )

    # print(f'list received by address result:\n{result}')
    # print(f'type:{type(result)}')
    for i in result:
        print(f'\n')
        for key, value in i.items():
            print(f'{key}: {value}')


def test_listsinceblock():
    BLOCKHASH = "00000068900c74f8b20a63e594465bcf4e64d259400b0d634bd423aca166596d"
    result = rpc.listsinceblock(
        blockhash=BLOCKHASH,
        target_confirmations=None,
        include_watchonly=None,
        include_removed=None
    )

    print(f'list since block {BLOCKHASH} result:\n{result}')


def test_listtransactions():

    result = rpc.listtransactions(
        account=None,
        count=None,
        skip=None,
        include_watchonly=None
    )

    print(f'list transactions result:\n{result}')


def test_listunspent():
    result = rpc.listunspent(
        minconf=None,
        maxconf=None,
        addresses=None,
        include_unsafe=None,
        query_options=None
    )

    print(f'list unspent result:\n{result}')


def test_listwallets():

    result = rpc.listwallets(

    )

    print(f'list wallets result:\n{result}')

def test_lockunspent():
    result = rpc.lockunspent(
        unlock=True,
        transactions=None
    )

    print(f'lock unspent result:\n{result}')


def test_move():

    result = rpc.move(
        fromaccount="",
        toaccount="getNewAddressAccount",
        amount=0.01,
        minconf_or_dummy=0,
        comment="budget rebalancing"
    )

    print(f'move result:\n{result}')


def test_removeprunedfunds():

    result = rpc.removeprunedfunds(
        txid="a8d0c0184dde994a09ec054286f1ce58...ea0a5"
    )

    print(f'remove pruned funds result:\n{result}')


def test_rescanblockchain():

    result = rpc.rescanblockchain(
        start_height=1179421,
        stop_height=None
    )

    print(f'rescan blockchain result:\n{result}')

def test_sendfrom():

    result = rpc.sendfrom(
        fromaccount="",
        toaddress="mykyeu5VtJACsWiPytouAH6MRkqq5VmvsE",
        amount=1,
        minconf=0,
        comment="test send"
    )

    print(f'send from result:\n{result}')

def test_sendfromaddress():

    result = rpc.sendfromaddress(
        from_address="mvTaFnBRbVZRepLoxVonBQkNJYrRxMwtDW",
        to_address="n3pUp4uT58hTtATHGvmkBsGP9tzMn8ZAQs",
        amount=1,
        comment="test send"
    )

    print(f'send from address result:\n{result}')


def test_sendmany():
    amounts = {
        "n3pUp4uT58hTtATHGvmkBsGP9tzMn8ZAQs": 1,
        "mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF": 1,
    }

    # Subtract fee equally from all recipients in this batch
    subtract_list = list(amounts.keys())

    result = rpc.sendmany(
        fromaccount="",
        amounts=amounts,
        minconf=0,
        comment="comment",
        subtractfeefrom=subtract_list,  # must be a JSON array of addresses (wrapper will encode the list)
        # conf_target=None, # THIS BREAKS THE RPC CALL
        # estimate_mode="UNSET", # CANT GET TO THIS BECAUSE PREVIOUS ARG BREAKS
        # estimate_mode is optional; omit or set to "UNSET"/"ECONOMICAL"/"CONSERVATIVE"
        # estimate_mode="UNSET",
    )

    print(f"send many result:\n{result}")


def test_setaccount():
    result = rpc.setaccount(
        address="mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF",
        account="call me maybe"
    )
    print(f"set account result:\n{result}")


def test_settxfee():
    AMOUNT = 0.0001
    result = rpc.settxfee(
        amount=AMOUNT
    )

    print(f'set tx fee to {AMOUNT}\n{result}')

def test_signmessage():

    result = rpc.signmessage(
        address="mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF",
        message="hello world"
    )

    print(f'sign message result:\n{result}')

if __name__ == "__main__":
    # test_abandontransaction()
    # test_sendtoaddress()
    # test_abortrescan()
    # test_addmultisigaddress()
    # test_addwitnessaddress()
    # test_backupwallet()
    # test_dumpprivkey()
    # test_dumpwallet()
    # test_encryptwallet() # NOT TESTED YET | DO NOT RUN YET
    # test_getaccount()
    # test_getaccountaddress()
    # test_getaddressesbyaccount()
    # test_getbalance()
    # test_getmasterkeyinfo()
    # test_getmywords()
    # test_getnewaddress()
    # test_getrawchangeaddress()
    # test_getreceivedbyaccount()
    # test_getreceivedbyaddress()
    # test_gettransaction()
    # test_getunconfirmedbalance()
    # test_getwalletinfo()
    # test_importaddress()
    # test_importmulti()
    # test_importprivkey()
    # test_importprunedfunds()
    # test_importpubkey()
    # test_importwallet()
    # test_keypoolrefill()
    # test_listaccounts()
    # test_listaddressgroupings()
    # test_listlockunspent()
    # test_listreceivedbyaccount()
    # test_listreceivedbyaddress()
    # test_listsinceblock()
    # test_listtransactions()
    # test_listunspent()
    # test_listwallets()
    # test_lockunspent()
    # test_move()
    # test_removeprunedfunds()
    # test_rescanblockchain()
    # test_sendfrom()
    # test_sendfromaddress()
    # test_sendmany()
    # test_setaccount()
    # test_settxfee()
    test_signmessage()