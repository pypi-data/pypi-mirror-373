# -*- coding: utf-8 -*-
# Copyright (c) 2025 yaqiang.sun.
# This source code is licensed under the license found in the LICENSE file
# in the root directory of this source tree.
#########################################################################
# Author: yaqiangsun
# Created Time: 2025/09/01 14:09:42
########################################################################


from fastmcp import FastMCP

from fastmcp.server.proxy import ProxyClient

main_mcp = FastMCP(name="MainAppLive")


def get_mcp_server_proxy(url:str="http://example.com/mcp/sse",name:str="Remote-to-Local Bridge"):
    # Bridge remote SSE server to local stdio
    remote_proxy = FastMCP.as_proxy(
        ProxyClient(url),
        name=name
    )
    return remote_proxy

@main_mcp.tool
def add_mcp_server(url:str,name:str):
    """Add a remote MCP server to the main MCP server"""
    main_mcp.mount(get_mcp_server_proxy(url,name))
    return main_mcp._mounted_servers
@main_mcp.tool
def delete_mcp_server(url:str,name:str):
    """Detect a remote MCP server and add it to the main MCP server"""
    # server = get_mcp_server_proxy(url,name)
    remove_index = []
    for i in range(len(main_mcp._mounted_servers)):
        server_name = main_mcp._mounted_servers[i].server.name
        if server_name == name:
            remove_index.append(i)
    for i in remove_index[::-1]:
            main_mcp._mounted_servers.pop(i)
            main_mcp._tool_manager._mounted_servers.pop(i)
            main_mcp._resource_manager._mounted_servers.pop(i)
            main_mcp._prompt_manager._mounted_servers.pop(i)
    return None
@main_mcp.tool
def list_mcp_servers():
    """List all mounted MCP servers"""
    return main_mcp._mounted_servers


# Run locally via stdio for Claude Desktop
if __name__ == "__main__":
    main_mcp.run()  # Defaults to stdio transport