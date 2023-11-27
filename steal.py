import time

from bip_utils import Bip39MnemonicGenerator, Bip39SeedGenerator, Bip39WordsNum, Bip44, Bip44Changes, Bip44Coins
from web3 import Web3
import os
from dotenv import load_dotenv
from requests.exceptions import HTTPError

load_dotenv()

ADDR_NUM: int = 0
URL = 'https://rpc.ankr.com/eth'
Provider = os.environ.get("PROVIDER", URL)


def gen_wallet(addr_num: int = ADDR_NUM) -> tuple:
    # Generate random mnemonic
    mnemonic       = Bip39MnemonicGenerator().FromWordsNumber(Bip39WordsNum.WORDS_NUM_12)
    # Generate seed from mnemonic
    seed_bytes     = Bip39SeedGenerator(mnemonic).Generate()
    # Construct from seed
    bip44_mst_ctx  = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
    # Derive BIP44 account keys: m/44'/0'/0'
    bip44_acc_ctx  = bip44_mst_ctx.Purpose().Coin().Account(0)
    # Derive BIP44 chain keys: m/44'/0'/0'/0
    bip44_chg_ctx  = bip44_acc_ctx.Change(Bip44Changes.CHAIN_EXT)
    # Derive addresses: m/44'/0'/0'/0/i
    bip44_addr_ctx = bip44_chg_ctx.AddressIndex(addr_num)
    pk             = bip44_addr_ctx.PrivateKey().Raw().ToHex()
    addr           = bip44_addr_ctx.PublicKey().ToAddress()
    mnemonic       = mnemonic.ToStr()
    return mnemonic, pk, addr


def get_balance(addr : str = None) -> float:
    try:
        # Connect to a local Ethereum node
        web3 = Web3(Web3.HTTPProvider(Provider))
        bal = web3.eth.get_balance(Web3.to_checksum_address(addr))
        bal = float(bal) / 10 ** 18
        return bal
    except HTTPError as e:
        print(f"Error: {e}, retrying in 3s...")
        time.sleep(3)
        return get_balance(addr)


if __name__ == "__main__":
    for i in range(0, 10000000):
        seed_phrase, private_key, address = gen_wallet()
        # check balance of address
        balance = get_balance(address)
        print(f"Checking {i}: {address=} {balance=} {private_key=}")
        if balance > 0:
            print(f"Found: {address=} {private_key=} {seed_phrase=} ")
            break
