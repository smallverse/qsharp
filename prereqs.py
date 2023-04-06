#!/usr/bin/env python3

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import urllib.request
import platform
import re
import sys
import subprocess
import tempfile

python_ver    = (3, 11)     # Python support for Windows on ARM64 requires v3.11 or later
rust_ver      = (1, 65)     # Ensure Rust version 1.65 or later is installed (needed for 'backtrace' support)
node_ver      = (16, 17)    # Node.js version 16.17 or later is required to support the Node.js 'test' module
wasmpack_ver  = (0, 11, 0)  # Latest tested wasm-pack version

def check_prereqs(install=False):
    
    if sys.version_info.major != python_ver[0] or sys.version_info.minor < python_ver[1]:
        print(f'Python {python_ver[0]}.{python_ver[1]} or later is required. Please update')
        exit(1)

    try:
        rust_version = subprocess.check_output(['rustc', '--version'])
        print(f"Detected Rust version: {rust_version.decode()}")
    except FileNotFoundError:
        print('Rust compiler not found. Install from https://rustup.rs/')
        exit(1)

    version_match = re.search(r'rustc (\d+)\.(\d+).\d+', rust_version.decode())
    if version_match:
        rust_major = int(version_match.group(1))
        rust_minor = int(version_match.group(2))
        if rust_major < rust_ver[0] or (rust_major == rust_ver[0] and rust_minor < rust_ver[1]):
            print(f'Rust v{rust_ver[0]}.{rust_ver[1]} or later is required. Please update with "rustup update"')
            exit(1)
    else:
        raise Exception('Unable to determine the Rust compiler version.')
    
    try:
        node_version = subprocess.check_output(['node', '-v'])
        print(f"Detected node.js version {node_version.decode()}")
    except FileNotFoundError:
        print('Node.js not found. Please install from https://nodejs.org/')
        exit(1)

    version_match = re.search(r'v(\d+)\.(\d+)\.\d+', node_version.decode())
    if version_match:
        node_major = int(version_match.group(1))
        node_minor = int(version_match.group(2))
        if node_major < node_ver[0] or (node_major == node_ver[0] and node_minor < node_ver[1]):
            print('Node.js v{nodejs_ver[0]}.{nodejs_ver[1]} or later is required. Please update.')
            exit(1)
    else:
        raise Exception('Unable to determine the Node.js version.')

    try:
        wasm_pack_version = subprocess.check_output(['wasm-pack', '--version'])
        print(f"Detected wasm-pack version {wasm_pack_version.decode()}")
    except FileNotFoundError:
        if install == True:
            if platform.system() == 'Windows':
                ver_str = f'v{wasmpack_ver[0]}.{wasmpack_ver[1]}.{wasmpack_ver[2]}'
                with urllib.request.urlopen(f'https://github.com/rustwasm/wasm-pack/releases/download/{ver_str}/wasm-pack-init.exe') as wasm_exe:
                    exe_bytes = wasm_exe.read()
                    tmp_dir = os.getenv('RUNNER_TEMP', default=tempfile.gettempdir())
                    file_name = os.path.join(tmp_dir, 'wasm-pack-init.exe')
                    with open(file_name, "wb") as exe_file:
                        exe_file.write(exe_bytes)
                    print('Attempting to install wasm-pack')
                    subprocess.run([file_name, '/q'], check=True)
            else:
                with urllib.request.urlopen('https://rustwasm.github.io/wasm-pack/installer/init.sh') as wasm_script:
                    sh_text = wasm_script.read().decode('utf-8')
                    tmp_dir = os.getenv('RUNNER_TEMP', default=tempfile.gettempdir())
                    file_name = os.path.join(tmp_dir, 'wasm_install.sh')
                    with open(file_name, "w") as file:
                        file.write(sh_text)
                    print('Attempting to install wasm-pack')
                    subprocess.run(['sh', file_name], check=True)

            wasm_pack_version = subprocess.check_output(['wasm-pack', '--version'])
        else:
            print('wasm-pack not found. Please install from https://rustwasm.github.io/wasm-pack/installer/')
            exit(1)

    version_match = re.search(r'wasm-pack (\d+)\.(\d+).\d+', wasm_pack_version.decode())
    if version_match:
        wasm_major = int(version_match.group(1))
        wasm_minor = int(version_match.group(2))
        if wasm_major != wasmpack_ver[0] or wasm_minor < wasmpack_ver[1]:
            print(f'wasm-pack version must be {wasmpack_ver[0]}.{wasmpack_ver[1]} or later. Please update.')
            exit(1)
    else:
        raise Exception('Unable to determine the wasm-pack version')

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--install':
        check_prereqs(install=True)
    else:
        check_prereqs(install=False)