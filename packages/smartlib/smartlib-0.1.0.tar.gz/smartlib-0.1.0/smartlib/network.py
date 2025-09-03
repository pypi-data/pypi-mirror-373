import os
from web3 import Web3
from dotenv import load_dotenv
from eth_account import Account

# Load .env if present
load_dotenv()

class Network:
    w3 = None
    provider_url = None
    chain_id = None
    _wallet = None  # loaded wallet (from private key)

    @classmethod
    def connect(cls, provider_url=None):
        """Connect to an Ethereum network (Ganache, Infura, Alchemy, etc.)."""
        if provider_url is None:
            provider_url = os.getenv("RPC_URL", "http://127.0.0.1:7545")

        cls.w3 = Web3(Web3.HTTPProvider(provider_url))
        cls.provider_url = provider_url

        if cls.w3.is_connected():
            try:
                cls.chain_id = cls.w3.eth.chain_id
                print(f"✅ Connected to {provider_url} | Chain ID: {cls.chain_id}")
            except Exception:
                cls.chain_id = None
                print(f"✅ Connected to {provider_url} | ⚠️ Could not fetch chain ID")
        else:
            raise ConnectionError(f"❌ Failed to connect to {provider_url}")

    @classmethod
    def connect_from_env(cls):
        """
        Connect to a network using .env:
        - DEFAULT_NETWORK → RPC key name (e.g., SEPOLIA_URL, GANACHE_URL).
        - Fallback: GANACHE_URL if set.
        - Fallback: http://127.0.0.1:7545
        """
        network_name = os.getenv("DEFAULT_NETWORK")

        if network_name:
            provider_url = os.getenv(network_name)
            if not provider_url:
                raise Exception(f"❌ DEFAULT_NETWORK={network_name}, but {network_name} not found in .env")
        else:
            provider_url = os.getenv("GANACHE_URL", "http://127.0.0.1:7545")

        cls.connect(provider_url)

    @classmethod
    def load_wallet(cls):
        """Load wallet from PRIVATE_KEY in .env and set as default account."""
        private_key = os.getenv("PRIVATE_KEY")
        if not private_key:
            raise Exception("❌ No PRIVATE_KEY found in .env")

        acct = Account.from_key(private_key)
        cls._wallet = acct
        if cls.w3:
            cls.w3.eth.default_account = acct.address

        print(f"🔑 Wallet loaded: {acct.address}")
        return acct.address

    @classmethod
    def get_account(cls, index=0):
        """
        Get an account:
        - If wallet loaded → return that.
        - Else → fallback to Ganache/unlocked accounts.
        """
        if not cls.w3:
            raise Exception("❌ Not connected to a network. Call Network.connect() first.")

        if cls._wallet:
            return cls._wallet.address

        if cls.w3.eth.accounts:
            return cls.w3.eth.accounts[index]

        raise Exception("❌ No accounts available. Provide PRIVATE_KEY in .env")

    @classmethod
    def sign_and_send(cls, tx):
        """Sign and send a raw transaction with loaded wallet."""
        if not cls._wallet:
            raise Exception("❌ No wallet loaded. Call Network.load_wallet() first.")

        # Auto-inject chainId if missing
        tx.setdefault("chainId", cls.chain_id or 1337)

        signed = cls._wallet.sign_transaction(tx)
        tx_hash = cls.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = cls.w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt


