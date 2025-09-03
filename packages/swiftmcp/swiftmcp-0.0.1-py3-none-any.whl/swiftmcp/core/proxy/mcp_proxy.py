# -*- coding: utf-8 -*-
# Copyright (c) 2025 yaqiang.sun.
# This source code is licensed under the license found in the LICENSE file
# in the root directory of this source tree.
#########################################################################
# Author: yaqiangsun
# Created Time: 2025/09/02 13:07:09
########################################################################


from fastmcp import FastMCP

from fastmcp.server.proxy import ProxyClient



# Bridge local server to HTTP
local_proxy = FastMCP.as_proxy(
    ProxyClient("swiftmcp/core/composition/mcp_composition.py"),
    name="Local-to-HTTP Bridge"
)

# Run via HTTP for remote clients
if __name__ == "__main__":
    local_proxy.run(transport="http", host="0.0.0.0", port=8080, path="/mcp")