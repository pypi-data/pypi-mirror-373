# -*- coding: utf-8 -*-
# Copyright (c) 2025 yaqiang.sun.
# This source code is licensed under the license found in the LICENSE file
# in the root directory of this source tree.
#########################################################################
# Author: yaqiangsun
# Created Time: 2025/09/03 19:53:58
########################################################################


import importlib.util
import os
import subprocess

import sys
from typing import Dict, List, Optional

ROUTE_MAPPING: Dict[str, str] = {
    'serve': 'swiftmcp.cli.proxy_serve',
}
def cli_main(route_mapping: Optional[Dict[str, str]] = None) -> None:
    print("Welcome to SwiftMCP!")
    

    if len(sys.argv)<=1:
        print("Usage: swiftmcp <command> [<args>]")
        sys.exit(1)
    
    route_mapping = route_mapping or ROUTE_MAPPING
    argv = sys.argv[1:]
    method_name = argv[0].replace('_', '-')
    argv = argv[1:]
    file_path = importlib.util.find_spec(route_mapping[method_name]).origin
    python_cmd = sys.executable
    args = [python_cmd, file_path, *argv]
    # print(f"run sh: `{' '.join(args)}`", flush=True)
    result = subprocess.run(args)
    if result.returncode != 0:
        sys.exit(result.returncode)