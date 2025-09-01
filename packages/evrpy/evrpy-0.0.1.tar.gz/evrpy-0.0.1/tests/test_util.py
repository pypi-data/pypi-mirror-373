from evrpy import UtilRPC

# Testnet configuration — set these to valid testnet values before running
CLI_PATH = "/home/aethyn/mining/evrmore-2.0.0.test/bin/evrmore-cli"
DATA_DIR = "/home/aethyn/.evrmore-test"
RPC_USER = "neubtrino_testnet"
RPC_PASS = "pass_testnet"
USE_TESTNET = True

rpc = UtilRPC(
    cli_path=CLI_PATH,
    datadir=DATA_DIR,
    rpc_user=RPC_USER,
    rpc_pass=RPC_PASS,
    testnet=USE_TESTNET
)


def test_createmultisig():

    # result_hex_pubkey = rpc.createmultisig(
    #     nrequired=2,
    #     keys=[
    #         "029a3c...<hex pubkey>...",
    #         "029a3c...<hex pubkey>..."
    #     ]
    # )

    result_addys = rpc.createmultisig(
        nrequired=2,
        keys=[
            "mwogs94cSAnE6bvTQWWep4MnowtsdqFU2Z",
            "mt9SMCXuqpdxdANbginxLrhUCF2iqkz34r"
        ]
    )

    print(f'created multisig with addresses\n{result_addys}')
    print(f'\niterated result')
    for key, value in result_addys.items():
        print(f'{key}: {value}')

def test_estimatefee():
    NBLOCKS=10
    result = rpc.estimatefee(
        nblocks=NBLOCKS
    )

    print(f'for nblocks={NBLOCKS} the estimated fee is {result}')


def test_estimatesmartfee():
    CONF_TARGET=100
    result = rpc.estimatesmartfee(
        conf_target=CONF_TARGET,
        estimate_mode="UNSET"
    )

    print(f'for conf_target={CONF_TARGET} the estimated smart fee is {result}')
    print(f'\niterated result')
    for key, value in result.items():
        print(f'{key}: {value}')

def test_signmessagewithprivkey():
    MESSAGE="wen moon"
    ADDRESS="mwogs94cSAnE6bvTQWWep4MnowtsdqFU2Z"

    # privkey is for address "mvTaFnBRbVZRepLoxVonBQkNJYrRxM"
    # address needs to be known for using this with test_verifymessage
    # use dumpprivkey to get privkey pertaining to address
    result = rpc.signmessagewithprivkey(
        privkey="cTz1wwabGc6MEMoUPEVMMtuTXJtY8xtdGZYSMtjGyovy9DwUw9Bb",
        message=MESSAGE
    )

    print(f'signature: {result}\nsignature type: {type(result)}')

    return result, MESSAGE, ADDRESS

def test_validateaddress():

    result = rpc.validateaddress(
        address="mwogs94cSAnE6bvTQWWep4MnowtsdqFU2Z"
    )

    print(f'validate result:\n{result}')
    print(f'\niterated result')
    for key,value in result.items():
        print(f'{key}: {value}')

def test_verifymessage():
    SIGNATURE, MESSAGE, ADDRESS = test_signmessagewithprivkey()
    result = rpc.verifymessage(
        address=ADDRESS,
        signature=SIGNATURE,
        message=MESSAGE
    )

    print(f'\nabove outputs are from calling test_signmessagewithprivkey()\n'
          f'\nbelow is from test_verifymessage()'
          f'\nverify message result: {result}')

if __name__ == "__main__":
    # test_createmultisig()
    # test_estimatefee()
    # test_estimatesmartfee()
    # test_signmessagewithprivkey()
    # test_validateaddress()
    test_verifymessage()