import os
from pathlib import Path
from dotenv import load_dotenv
from eth_account import Account
from .network import Network

# Load .env automatically
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)


class Wallet:
    _account = None

    @staticmethod
    def load_from_env():
        """Load wallet from PRIVATE_KEY in .env"""
        private_key = os.getenv("PRIVATE_KEY")
        if not private_key:
            raise Exception("❌ No PRIVATE_KEY found in .env")

        acct = Account.from_key(private_key)
        Wallet._account = acct

        # Register with Web3 (set as default account)
        if Network.w3:
            Network.w3.eth.default_account = acct.address

        print(f"🔑 Wallet loaded: {acct.address}")
        return acct

    @staticmethod
    def get_account():
        """Get currently loaded wallet address"""
        if not Wallet._account:
            raise Exception("❌ No wallet loaded. Call Wallet.load_from_env() first.")
        return Wallet._account.address

    @staticmethod
    def sign_and_send(tx):
        """Sign and send a raw transaction with private key"""
        if not Wallet._account:
            raise Exception("❌ No wallet loaded. Call Wallet.load_from_env() first.")
        w3 = Network.w3
        signed = Wallet._account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt
