"""
Withdrawal script for a smart contract on the Rootstock (RSK) MAINNET blockchain.

Requirements:
    pip install web3
"""

import json


from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware




# ----------------------------------------------------------------------------
# 1) CONFIGURATION  -- fill these in
# ----------------------------------------------------------------------------

# Rootstock Mainnet
RPC_URL  = "https://public-node.rsk.co"
CHAIN_ID = 30

# The smart contract address (fill in later)
CONTRACT_ADDRESS = "0x5978c6153a06B141Cd0935569F600A83Eb44aeaA"

# Your wallet (the address that will SEND the withdraw transaction)
SENDER_ADDRESS     = "0x6Axxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"   #Your address / can be a different address
SENDER_PRIVATE_KEY = "0x68ed5c10c7xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx07d"     #private key

# ----------------------------------------------------------------------------
# 2) WITHDRAW PARAMETERS  -- fill these in manually
# ----------------------------------------------------------------------------

# Amount in wei (1 RBTC = 1e18 wei). Example: 0.001 RBTC = 1_000_000_000_000_000
AMOUNT     = 1_000_000_000_000_000   # change to the correct amount. This is 1 mRBTC

# Nonce expected by the contract (NOT the tx nonce; this is the contract-side nonce)
NONCE      = 129  #must be the same as in the burn validation.

# Address that should receive the withdrawn funds
RECEIVER   = "0xA8Ae4c712551f5b4b3FEc44ea8DddF0De3101875"  #must be the same as in the burn validation.

# A 32-byte transaction id (hex string starting with 0x, 64 hex chars)
TXID       = "8322C567F026D6DD443BE9F60FC827EF599CF3E82FD9484C4A905FF1B4326A47"  #must be the same as in the burn validation request
 
# Three signatures (hex strings starting with 0x)  at least two from three are required.
SIGNATURE  = "0x806f74f09533f22472bd6b800a87471af6d4d72f16b949f0cf196c91a67eeaa33ff0bfcb9324322cbe2eae51036ebef793f4fd5f99759f674fce83fa28b90d631b"
SIGNATURE2 = "0x08e1fc84a598c2a68da40c5cd9b833ba31a1511096952a755200f7a070593ba62775eb2125816b8ef9224c62d1d1200576e4c0f505976678c5477714945aa7511b"
SIGNATURE3 = "0xc09c9200095298cbd17d8a4de66c4927da1679079627cb1c6869030ea93d7f2c02908ba6946bd8c0a3bd83578b9ee44484d4093994ae1cee7c06921ad6f289881c"

# ----------------------------------------------------------------------------
# 3) ABI
# ----------------------------------------------------------------------------

CONTRACT_ABI = json.loads("""
[
    {"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"userId","type":"uint256"},{"indexed":false,"internalType":"string","name":"input","type":"string"}],"name":"Deposited","type":"event"},
    {"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"from","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"address","name":"tokenAddress","type":"address"}],"name":"ERC20Deposited","type":"event"},
    {"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"address","name":"tokenAddress","type":"address"}],"name":"ERC20Withdraw","type":"event"},
    {"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"recovered","type":"address"},{"indexed":false,"internalType":"address","name":"owner","type":"address"},{"indexed":false,"internalType":"uint8","name":"errorType","type":"uint8"}],"name":"Validate","type":"event"},
    {"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"receiver","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Withdraw","type":"event"},
    {"inputs":[{"internalType":"bytes","name":"pubKey","type":"bytes"}],"name":"changePubKey","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"userId","type":"uint256"},{"internalType":"string","name":"input","type":"string"}],"name":"deposit","outputs":[],"stateMutability":"payable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"amountSeconds","type":"uint256"}],"name":"pause","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[],"name":"resetWithdrawalLimit","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[],"name":"resume","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"address","name":"receiver","type":"address"},{"internalType":"bytes32","name":"txid","type":"bytes32"},{"internalType":"bytes","name":"signature","type":"bytes"},{"internalType":"bytes","name":"signature2","type":"bytes"},{"internalType":"bytes","name":"signature3","type":"bytes"}],"name":"withdraw","outputs":[],"stateMutability":"payable","type":"function"},
    {"inputs":[],"name":"getBalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"getPubKey","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}
]
""")

# ----------------------------------------------------------------------------
# 4) MAIN
# ----------------------------------------------------------------------------

def main():
    # Connect to Rootstock Mainnet
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    # Rootstock has fields that are not strictly EVM-compatible: inject PoA middleware
    #w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)


    if not w3.is_connected():
        raise RuntimeError(f"Could not connect to RPC at {RPC_URL}")

    print(f"Connected to Rootstock Mainnet. Latest block: {w3.eth.block_number}")

    # Validate / checksum addresses
    sender        = Web3.to_checksum_address(SENDER_ADDRESS)
    contract_addr = Web3.to_checksum_address(CONTRACT_ADDRESS)
    receiver      = Web3.to_checksum_address(RECEIVER)

    # Build contract object
    contract = w3.eth.contract(address=contract_addr, abi=CONTRACT_ABI)

    # Convert hex strings to bytes
    txid_bytes = Web3.to_bytes(hexstr=TXID)
    if len(txid_bytes) != 32:
        raise ValueError("TXID must be exactly 32 bytes (0x + 64 hex chars).")

    sig_bytes  = Web3.to_bytes(hexstr=SIGNATURE)
    sig2_bytes = Web3.to_bytes(hexstr=SIGNATURE2)
    sig3_bytes = Web3.to_bytes(hexstr=SIGNATURE3)

    # Get tx nonce from network
    tx_nonce = w3.eth.get_transaction_count(sender)

    # Gas price on Rootstock is generally low; use eth.gas_price
    gas_price = w3.eth.gas_price

    print("Building withdraw transaction...")
    print(f"  amount:    {AMOUNT}")
    print(f"  nonce:     {NONCE}")
    print(f"  receiver:  {receiver}")
    print(f"  txid:      {TXID}")

    # Build the transaction
    tx = contract.functions.withdraw(
        AMOUNT,
        NONCE,
        receiver,
        txid_bytes,
        sig_bytes,
        sig2_bytes,
        sig3_bytes,
    ).build_transaction({
        "from": sender,
        "chainId": CHAIN_ID,
        "nonce": tx_nonce,
        "gasPrice": gas_price,
        "value": 0,   # withdraw is payable, but we don't need to send RBTC
    })

    # Estimate gas (with a small safety margin)
    try:
        estimated = w3.eth.estimate_gas(tx)
        tx["gas"] = int(estimated * 1.2)
    except Exception as e:
        print(f"Gas estimation failed ({e}); falling back to 300000.")
        tx["gas"] = 300_000

    # Sign and send
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=SENDER_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"Transaction sent: {tx_hash.hex()}")

    # Wait for receipt
    print("Waiting for confirmation...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)

    if receipt.status == 1:
        print(f"✅ Withdraw confirmed in block {receipt.blockNumber}")
        print(f"   Gas used: {receipt.gasUsed}")
    else:
        print("❌ Transaction failed (status = 0). Check the parameters & signatures.")

    return receipt


if __name__ == "__main__":
    main()
