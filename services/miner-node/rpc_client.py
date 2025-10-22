"""
Tensora RPC Client - Simplified
"""
import logging
from web3 import Web3
from eth_account import Account
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TensoraRPC:
    def __init__(self, rpc_url: str, private_key: str):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = Account.from_key(private_key)
        self.wallet_address = self.account.address
        logger.info(f"RPC connected to {rpc_url}")
        logger.info(f"Wallet: {self.wallet_address}")
    
    def sign_message(self, message: str) -> str:
        message_hash = hashlib.sha256(message.encode()).digest()
        signed = self.account.signHash(message_hash)
        return signed.signature.hex()
