# -*- coding: utf-8 -*-
# Copyright (c) 2025 yaqiang.sun.
# This source code is licensed under the license found in the LICENSE file
# in the root directory of this source tree.
#########################################################################
# Author: yaqiangsun
# Created Time: 2025/09/03 19:43:55
########################################################################
import sys
from typing import Any, Dict, List, Optional, Union

import argparse

from swiftmcp.core.proxy.mcp_proxy import local_proxy
def get_config(args: Optional[Union[List[str]]] = None):

    #Create ArgumentParser object
    parser = argparse.ArgumentParser()

    parser.add_argument('--port', type=int, required=False, default=8000)
    parser.add_argument('--path', type=str, required=False, default="/mcp")
    # parser arguments
    args = parser.parse_args(sys.argv[1:])

    port = args.port
    return args

if __name__ == "__main__":
    args = get_config(sys.argv[1:])
    # print(args)
    print("Port:", args.port,",Paht:", args.path)
    local_proxy.run(transport="http", host="0.0.0.0", port=args.port, path=args.path)
    # local_proxy.run(transport="http", host="0.0.0.0", port=8080, path="/mcp")