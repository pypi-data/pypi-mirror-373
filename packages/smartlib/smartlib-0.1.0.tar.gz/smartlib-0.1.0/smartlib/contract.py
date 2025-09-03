import json
import re
import requests
import os
from pathlib import Path
from web3.exceptions import ContractLogicError
from .network import Network
from .compiler import Compiler


class SmartContract:
    def __init__(self, filepath, contract_name=None):
        self.filepath = Path(filepath)
        self.contract_name = contract_name
        self.compiled = None          # ABI + bytecode for this contract
        self.compiled_full = None     # Full compiler output (for libs)
        self.contract = None
        self.address = None
        self.compiler_version = None

    def compile(self, optimizer=True, runs=200):
        """Compile Solidity contract"""
        compiled, version = Compiler.compile_contract(
            self.filepath, optimizer=optimizer, runs=runs
        )
        self.compiler_version = version
        self.compiled_full = compiled  # ✅ store full compiler output
        self.compiled = compiled["contracts"][self.filepath.name][self.contract_name]

        contracts = compiled["contracts"][self.filepath.name]
        if not self.contract_name:
            if len(contracts) > 1:
                raise Exception(
                    f"❌ Multiple contracts found: {list(contracts.keys())}. "
                    "Please specify contract_name."
                )
            self.contract_name = list(contracts.keys())[0]

        self.compiled = contracts[self.contract_name]

        # Save ABI + bytecode to artifacts
        build_path = Path(__file__).resolve().parent / "artifacts"
        build_path.mkdir(exist_ok=True)
        with open(build_path / f"{self.contract_name}.json", "w") as f:
            json.dump(self.compiled, f, indent=2)

        print(
            f"✅ Compiled {self.contract_name} with solc {version} "
            f"| Bytecode length: {len(self.compiled['evm']['bytecode']['object'])}"
        )
        return self

    def _link_libraries(self, bytecode, compiled_contracts):
        """
        Deploys required libraries and replaces placeholders in bytecode.
        Uses compiler's linkReferences to map libraries to placeholders.
        """
        w3 = Network.w3
        linked_bytecode = bytecode

        # Check for linkReferences in compiled output
        link_refs = self.compiled.get("evm", {}).get("bytecode", {}).get("linkReferences", {})
        if not link_refs:
            return linked_bytecode  # No libraries to link

        print(f"🔗 Found {sum(len(v) for v in link_refs.values())} library reference(s). Deploying...")

        for file_name, libs in link_refs.items():
            for lib_name in libs:
                # Grab library data
                lib_data = compiled_contracts["contracts"][file_name][lib_name]
                lib_bytecode = lib_data["evm"]["bytecode"]["object"]
                if not lib_bytecode or lib_bytecode == "0x":
                    continue

                # Deploy the library
                lib_contract = w3.eth.contract(abi=lib_data["abi"], bytecode=lib_bytecode)
                account = Network.get_account(0)
                tx_hash = lib_contract.constructor().transact({"from": account, "gas": 3_000_000})
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                lib_address = receipt.contractAddress
                print(f"   ✅ Linked {lib_name} at {lib_address}")

                # Replace all occurrences of the library placeholder with address
                linked_bytecode = re.sub(
                    r"__\$[0-9a-fA-F]{34}\$__",
                    lib_address[2:].rjust(40, "0"),
                    linked_bytecode,
                )

        return linked_bytecode

    def deploy(self, *constructor_args, account=None, **tx_params):
        """Deploy contract with optional constructor args and tx params"""
        if not self.compiled:
            raise Exception("Contract not compiled. Call compile() first.")

        w3 = Network.w3
        abi = self.compiled["abi"]

        # ✅ link libraries before deployment
        raw_bytecode = self.compiled["evm"]["bytecode"]["object"]
        bytecode = self._link_libraries(raw_bytecode, self.compiled_full)

        if not bytecode or bytecode == "0x":
            raise Exception(f"❌ No bytecode found for {self.contract_name}")

        contract = w3.eth.contract(abi=abi, bytecode=bytecode)
        account = account or Network.get_account(0)

        transaction = {"from": account, "nonce": w3.eth.get_transaction_count(account)}
        transaction.update(tx_params)

        try:
            constructor = contract.constructor(*constructor_args)
        except TypeError as e:
            ctor = next((x for x in abi if x.get("type") == "constructor"), {"inputs": []})
            expected = ", ".join(f"{inp['type']} {inp['name']}" for inp in ctor["inputs"])
            provided = ", ".join(type(arg).__name__ for arg in constructor_args)
            raise Exception(
                f"❌ Constructor args mismatch for {self.contract_name}\n"
                f"   Expected: ({expected})\n"
                f"   Provided: ({provided})"
            ) from e

        try:
            gas_estimate = w3.eth.estimate_gas(constructor.build_transaction(transaction))
            transaction.setdefault("gas", int(gas_estimate * 1.2))
        except Exception as e:
            print(f"⚠️ Gas estimation failed ({e}), retrying with fallback")
            transaction.setdefault("gas", 3_000_000)

        built_tx = constructor.build_transaction(transaction)

        # ✅ If wallet loaded → sign & send manually
        if Network._wallet:
            receipt = Network.sign_and_send(built_tx)
        else:
            tx_hash = constructor.transact(transaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        self.contract = w3.eth.contract(address=receipt.contractAddress, abi=abi)
        self.address = receipt.contractAddress

        print(f"🚀 Deployed {self.contract_name} at {self.address} | Gas used: {receipt.gasUsed}")
        return self

    def _check_function_args(self, fn_name, args):
        """Helper to validate function args against ABI"""
        fn_abi = next(
            (f for f in self.compiled["abi"] if f.get("type") == "function" and f["name"] == fn_name),
            None,
        )
        if fn_abi:
            expected_count = len(fn_abi["inputs"])
            if len(args) != expected_count:
                expected = ", ".join(f"{inp['type']} {inp['name']}" for inp in fn_abi["inputs"])
                provided = ", ".join(type(arg).__name__ for arg in args)
                raise Exception(
                    f"❌ Arg mismatch for {fn_name}()\n"
                    f"   Expected: ({expected})\n"
                    f"   Provided: ({provided})"
                )

    def call(self, function_name, *args):
        if not self.contract:
            raise Exception("Contract not deployed yet.")
        self._check_function_args(function_name, args)
        return getattr(self.contract.functions, function_name)(*args).call()

    def transact(self, function_name, *args, account=None, **tx_params):
        if not self.contract:
            raise Exception("Contract not deployed yet.")

        w3 = Network.w3
        account = account or Network.get_account(0)

        self._check_function_args(function_name, args)

        transaction = {"from": account, "nonce": w3.eth.get_transaction_count(account)}
        transaction.update(tx_params)

        fn = getattr(self.contract.functions, function_name)(*args)

        try:
            gas_estimate = w3.eth.estimate_gas(fn.build_transaction(transaction))
            transaction.setdefault("gas", int(gas_estimate * 1.2))
        except Exception as e:
            print(f"⚠️ Gas estimation failed for {function_name} ({e}), using fallback")
            transaction.setdefault("gas", 3_000_000)

        built_tx = fn.build_transaction(transaction)

        if Network._wallet:
            receipt = Network.sign_and_send(built_tx)
        else:
            tx_hash = fn.transact(transaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        print(f"✅ Tx {function_name} confirmed | Gas used: {receipt.gasUsed}")
        return receipt

    # ==========================================================
    #  NEW: Step 4.4 → Etherscan Verification
    # ==========================================================
    def verify_on_etherscan(self, constructor_args=None):
        """
        Verify contract on Etherscan.
        Requires ETHERSCAN_API_KEY in .env.
        """
        api_key = os.getenv("ETHERSCAN_API_KEY")
        if not api_key:
            raise Exception("❌ ETHERSCAN_API_KEY not found in .env")

        if not self.address:
            raise Exception("❌ Contract must be deployed before verification.")

        source_code = self.filepath.read_text()
        compiler_version = f"v{self.compiler_version}+commit"
        optimizer_enabled = 1
        runs = 200

        url = "https://api.etherscan.io/api"
        data = {
            "apikey": api_key,
            "module": "contract",
            "action": "verifysourcecode",
            "contractaddress": self.address,
            "sourceCode": source_code,
            "codeformat": "solidity-single-file",
            "contractname": self.contract_name,
            "compilerversion": compiler_version,
            "optimizationUsed": optimizer_enabled,
            "runs": runs,
            "constructorArguements": "" if not constructor_args else constructor_args,
        }

        response = requests.post(url, data=data)
        result = response.json()

        if result.get("status") == "1":
            print(f"📤 Verification submitted! GUID: {result['result']}")
        else:
            print(f"❌ Verification failed: {result}")
