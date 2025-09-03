import re
import json
import hashlib
from pathlib import Path
from solcx import compile_standard, install_solc, set_solc_version


ARTIFACTS_DIR = Path(__file__).parent / "artifacts"
ARTIFACTS_DIR.mkdir(exist_ok=True)


class Compiler:
    @staticmethod
    def detect_version(source: str) -> str:
        match = re.search(r"pragma solidity\s+\^?([0-9.]+);", source)
        return match.group(1) if match else "0.8.19"

    @staticmethod
    def _hash_source(source: str) -> str:
        """Hash source for cache invalidation"""
        return hashlib.sha1(source.encode()).hexdigest()

    @staticmethod
    def compile_contract(filepath: str, optimizer: bool = True, runs: int = 200):
        filepath = Path(filepath).resolve()
        source = filepath.read_text()
        version = Compiler.detect_version(source)

        # ✅ cache file path
        contract_name = filepath.stem
        cache_file = ARTIFACTS_DIR / f"{contract_name}.json"
        source_hash = Compiler._hash_source(source)

        # ✅ check cache
        if cache_file.exists():
            data = json.loads(cache_file.read_text())
            if data.get("sourceHash") == source_hash:
                print(f"📦 Loaded cached artifact for {contract_name}")
                return data["compiled"], data["version"]

        # ✅ load all .sol files in the same folder (so imports work)
        sources = {}
        for file in filepath.parent.glob("*.sol"):
            sources[file.name] = {"content": file.read_text()}

        # compile
        try:
            install_solc(version)
            set_solc_version(version)
        except Exception:
            install_solc("0.8.19")
            set_solc_version("0.8.19")
            version = "0.8.19"

        compiled = compile_standard(
            {
                "language": "Solidity",
                "sources": sources,
                "settings": {
                    "optimizer": {"enabled": optimizer, "runs": runs},
                    "outputSelection": {
                        "*": {"*": ["abi", "evm.bytecode", "evm.deployedBytecode"]}
                    },
                },
            },
            solc_version=version,
        )

        # ✅ save to cache
        cache_file.write_text(json.dumps({
            "version": version,
            "sourceHash": source_hash,
            "compiled": compiled
        }, indent=2))

        print(
            f"✅ Compiled {contract_name} with solc {version} "
            f"| Bytecode length: {len(compiled['contracts'][filepath.name][contract_name]['evm']['bytecode']['object'])}"
        )

        return compiled, version
