"""
Tensora RPC Client
Interact with SubnetJobs and other contracts
"""

import logging
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from typing import Any, List, Dict

logger = logging.getLogger(__name__)


class TensoraRPC:
    """
    RPC client for Tensora L2 and BSC contracts
    """
    
    def __init__(self, rpc_url: str, private_key: str):
        """
        Initialize RPC client
        
        Args:
            rpc_url: RPC endpoint URL
            private_key: Wallet private key (with 0x prefix)
        """
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        
        # Add PoA middleware for BSC
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Load wallet
        self.account = Account.from_key(private_key)
        self.wallet_address = self.account.address
        
        logger.info(f"Connected to {rpc_url}")
        logger.info(f"Wallet: {self.wallet_address}")
        
        # Verify connection
        if not self.web3.is_connected():
            raise ConnectionError(f"Failed to connect to {rpc_url}")
        
        chain_id = self.web3.eth.chain_id
        logger.info(f"Chain ID: {chain_id}")
    
    async def call_contract(
        self,
        contract_address: str,
        function_name: str,
        args: List[Any],
        abi: Optional[List[Dict]] = None
    ) -> Any:
        """
        Call contract view function
        
        Args:
            contract_address: Contract address
            function_name: Function to call
            args: Function arguments
            abi: Contract ABI (optional, will load from file)
            
        Returns:
            Function return value
        """
        try:
            if abi is None:
                # Load ABI from file (simplified)
                abi = self._load_abi(contract_address)
            
            contract = self.web3.eth.contract(
                address=Web3.to_checksum_address(contract_address),
                abi=abi
            )
            
            result = getattr(contract.functions, function_name)(*args).call()
            
            return result
            
        except Exception as e:
            logger.error(f"Contract call failed: {e}")
            raise
    
    async def send_transaction(
        self,
        contract_address: str,
        function_name: str,
        args: List[Any],
        value: int = 0,
        abi: Optional[List[Dict]] = None
    ) -> str:
        """
        Send contract transaction
        
        Args:
            contract_address: Contract address
            function_name: Function to call
            args: Function arguments
            value: ETH/BNB value to send
            abi: Contract ABI
            
        Returns:
            Transaction hash
        """
        try:
            if abi is None:
                abi = self._load_abi(contract_address)
            
            contract = self.web3.eth.contract(
                address=Web3.to_checksum_address(contract_address),
                abi=abi
            )
            
            # Build transaction
            function = getattr(contract.functions, function_name)(*args)
            
            nonce = self.web3.eth.get_transaction_count(self.wallet_address)
            
            tx = function.build_transaction({
                'from': self.wallet_address,
                'nonce': nonce,
                'value': value,
                'gas': 500000,  # Will be estimated
                'gasPrice': self.web3.eth.gas_price
            })
            
            # Estimate gas
            try:
                estimated_gas = self.web3.eth.estimate_gas(tx)
                tx['gas'] = int(estimated_gas * 1.2)  # 20% buffer
            except Exception as e:
                logger.warning(f"Gas estimation failed: {e}, using default")
            
            # Sign and send
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            logger.info(f"Transaction sent: {tx_hash.hex()}")
            
            # Wait for receipt
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt['status'] == 1:
                logger.info(f"Transaction confirmed: {tx_hash.hex()}")
                return tx_hash.hex()
            else:
                raise Exception(f"Transaction failed: {tx_hash.hex()}")
                
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            raise
    
    def sign_message(self, message: str) -> str:
        """
        Sign a message with wallet (EIP-191)
        
        Args:
            message: Message to sign
            
        Returns:
            Signature as hex string
        """
        message_hash = hashlib.sha256(message.encode()).digest()
        signed = self.account.signHash(message_hash)
        return signed.signature.hex()
    
    def _load_abi(self, contract_address: str) -> List[Dict]:
        """
        Load ABI from file or return minimal ABI
        
        Args:
            contract_address: Contract address
            
        Returns:
            ABI list
        """
        # Simplified: return minimal ABI for testing
        # In production, load from contracts/abi/ directory
        return [
            {
                "inputs": [],
                "name": "getAvailableJobs",
                "outputs": [{"type": "uint256[]"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"type": "uint256"}],
                "name": "acceptJob",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"type": "uint256"},
                    {"type": "bytes32"},
                    {"type": "bytes"}
                ],
                "name": "submitResult",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]


if __name__ == "__main__":
    # Test RPC client
    logging.basicConfig(level=logging.INFO)
    print("Tensora RPC Client")
    print("=" * 60)
    print("Connects to Tensora L2 and BSC contracts")
    print("Supports transactions and view calls")

