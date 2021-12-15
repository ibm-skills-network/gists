"""
This script is useful to replace the sops encryption backend in the repo

Decrypt all secrets

```bash
python3 rotate.py decrypt
```

Update config in `.sops.yaml` to use the new encryption backend. Re-encrypt all secrets

```bash
python3 rotate.py encrypt
```
"""

import sys
import os
import subprocess
import argparse
import glob

PATTERNS = [
    "./config/*/secrets.*.yaml",
    "./config/*/secrets.yaml",
    "./environments/secrets.*.yaml",
    "./environments/secrets.yaml"
]

def decrypt_file(path):
    if not os.path.isfile(path):
        raise Exception(f"{path} is not a file")
    subprocess.run(["helm", "secrets", "dec", path])


def encrypt_file(path, gpg_key_id=None):
    if not os.path.isfile(path):
        raise Exception(f"{path} is not a file")
    commands = ["helm", "secrets", "enc", path]
    env = os.environ.copy()
    if gpg_key_id:
        env["SOPS_PGP_FP"] = gpg_key_id
    subprocess.run(commands, env=env)

def get_secret_files():
    secret_files = []
    for each in PATTERNS:
        secret_files.extend(glob.glob(each))
    return list(set(secret_files))

def encrypt(args):
    secret_files = get_secret_files()
    
    for each in secret_files:
        encrypt_file(each)

def decrypt(args):
    secret_files = get_secret_files()
    
    for each in secret_files:
        decrypt_file(each)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="action")
    base_subparser = argparse.ArgumentParser(add_help=False)

    parser_encrypt = subparsers.add_parser("encrypt", parents=[base_subparser])
    parser_encrypt.set_defaults(func=encrypt)

    parser_decrypt = subparsers.add_parser("decrypt", parents=[base_subparser])
    parser_decrypt.set_defaults(func=decrypt)

    args = parser.parse_args()
    if args.action:
        args.func(args)
    else:
        parser.parse_args(["--help"])
        sys.exit(0)
