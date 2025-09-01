from evrpy import RestrictedassetsRPC

# Testnet configuration — set these to valid testnet values before running
CLI_PATH = "/home/aethyn/mining/evrmore-2.0.0.test/bin/evrmore-cli"
DATA_DIR = "/home/aethyn/.evrmore-test"
RPC_USER = "neubtrino_testnet"
RPC_PASS = "pass_testnet"
USE_TESTNET = True

rpc = RestrictedassetsRPC(
    cli_path=CLI_PATH,
    datadir=DATA_DIR,
    rpc_user=RPC_USER,
    rpc_pass=RPC_PASS,
    testnet=USE_TESTNET
)

def test_addtagtoaddress():

    result = rpc.addtagtoaddress(
        tag_name="#KYCAML",
        to_address="n4bpZEyAm2hbhNPoKWicf82C4RX44Ung4Z",
    )

    print(f"txid:\n{result}")


def test_issuequalifierasset():

    result = rpc.issuequalifierasset(
        asset_name="AMLKYC",
        qty=10,
        to_address="mxSognf8BrWSgG4pxiko7XsAkPVLsMGnch",
        change_address="n4iLxDUVRsJrf4824Wdur2nVoZDAtGUtEv",
        has_ipfs=True,
        ipfs_hash="QmcUqJaj6QjALDPgwCX14a7bVZDKA954gBptkd699LpLQL",
        permanent_ipfs_hash="QmcUqJaj6QjALDPgwCX14a7bVZDKA954gBptkd699LpLQL"
    )

    print(f"txid:\n{result}")


def test_issuerestrictedasset():

    result = rpc.issuerestrictedasset(
        asset_name="$NEUBTRINO_RESTRICTED_2",
        qty=21000000000,
        verifier="#KYC",
        to_address="n4bpZEyAm2hbhNPoKWicf82C4RX44Ung4Z"
    )

    print(f"txid:\n{result}")


def test_checkaddressrestriction():

    result = rpc.checkaddressrestriction(
        address="mxSognf8BrWSgG4pxiko7XsAkPVLsMGnch",
        restricted_name="$NEUBTRINO_RESTRICTED_1"
    )

    print(f"result:\n{result}")


def test_checkaddresstag():

    result = rpc.checkaddresstag(
        address="mxSognf8BrWSgG4pxiko7XsAkPVLsMGnch",
        tag_name="#KYC"
    )

    print(f'result:\n{result}')


def test_checkglobalrestriction():

    result = rpc.checkglobalrestriction(
        restricted_name="NEUBTRINO_RESTRICTED_1"
    )

    print(f'result:\n{result}')


def test_freezeaddress():

    result = rpc.freezeaddress(
        asset_name="$NEUBTRINO_RESTRICTED_1",
        address="mxSognf8BrWSgG4pxiko7XsAkPVLsMGnch",
    )

    print(f"txid:\n{result}")

def test_freezerestrictedasset():

    result = rpc.freezerestrictedasset(
        asset_name="$NEUBTRINO_RESTRICTED_1",
    )

    print(f'restricted asset frozen:\n{result}')

def test_getverifierstring():

    result = rpc.getverifierstring(
        restricted_name="$NEUBTRINO_RESTRICTED_1"
    )

    print(f'verifier string:\n{result}')

def test_isvalidverifierstring():

    result = rpc.isvalidverifierstring(
        verifier_string="KYC"
    )

    print(f'is valid verifier string:\n{result}')


def test_listaddressesfortag():

    result = rpc.listaddressesfortag(
        tag_name="#KYC"
    )

    print(f'addresses:\n{result}')

def test_listaddressrestrictions():

    result = rpc.listaddressrestrictions(
        address="mxSognf8BrWSgG4pxiko7XsAkPVLsMGnch"
    )

    print(f'address restrictions:\n{result}')

def test_listglobalrestrictions():

    result = rpc.listglobalrestrictions(

    )

    print(f'global restrictions:\n{result}')

def test_listtagsforaddress():

    result = rpc.listtagsforaddress(
        address="mxSognf8BrWSgG4pxiko7XsAkPVLsMGnch"
    )

    print(f'tags for address:\n{result}')

def test_reissuerestrictedasset():

    result = rpc.reissuerestrictedasset(
        asset_name="NEUBTRINO_RESTRICTED_1",
        qty=100,
        to_address="mxSognf8BrWSgG4pxiko7XsAkPVLsMGnch"
    )

    print(f'reissue restricted asset txid:\n{result}')

def test_removetagfromaddress():

    result = rpc.removetagfromaddress(
        tag_name="KYC",
        to_address="mxSognf8BrWSgG4pxiko7XsAkPVLsMGnch"
    )

    print(f'remove tag from address txid:\n{result}')

def test_transferqualifier():

    result = rpc.transferqualifier(
        qualifier_name="#KYC",
        qty=10,
        to_address="mxSognf8BrWSgG4pxiko7XsAkPVLsMGnch"
    )

    print(f'transfer qualifier txid:\n{result}')

def test_unfreezeaddress():

    result = rpc.unfreezeaddress(
        asset_name="NEUBTRINO_RESTRICTED_1",
        address="mxSognf8BrWSgG4pxiko7XsAkPVLsMGnch"
    )

    print(f'unfreeze address txid:\n{result}')

def test_unfreezerestrictedasset():

    result = rpc.unfreezerestrictedasset(
        asset_name="NEUBTRINO_RESTRICTED_1"
    )

    print(f'unfreeze restricted asset txid:\n{result}')


if __name__ == "__main__":
   # test_addtagtoaddress()
    # test_checkaddressrestriction()
    # test_checkaddresstag()
    # test_checkglobalrestriction()
    # test_freezeaddress()
    # test_freezerestrictedasset()
    # test_getverifierstring()
    # test_issuequalifierasset()
    # test_issuerestrictedasset()
    # test_isvalidverifierstring()
    # test_listaddressesfortag()
    # test_listaddressrestrictions()
    # test_listglobalrestrictions()
    # test_listtagsforaddress()
    # test_reissuerestrictedasset()
    # test_removetagfromaddress()
    # test_transferqualifier()
    # test_unfreezeaddress()
    test_unfreezerestrictedasset()