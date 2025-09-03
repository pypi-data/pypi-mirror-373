# -*- coding: utf-8 -*-
# Copyright (c) 2025 yaqiang.sun.
# This source code is licensed under the license found in the LICENSE file
# in the root directory of this source tree.
#########################################################################
# Author: yaqiangsun
# Created Time: 2025/08/29 17:37:59
########################################################################


from pydantic import BaseModel
from typing import Any, Literal, cast


from mcp.server.fastmcp import FastMCP as FastMCP1x
import pydantic_core
import fastmcp
from fastmcp import Client
from fastmcp.server.server import FastMCP
from fastmcp.utilities.inspect import (
    FastMCPInfo,
    ToolInfo,
    inspect_fastmcp
)
import json


class MCPTool(object):
    def __init__(self,mcp: FastMCP[Any]
                 ):
        self.mcp = mcp
        pass
    async def inspect_tools(self) -> list[ToolInfo]:
        mcp_info =  await inspect_fastmcp(self.mcp)
        return mcp_info.tools
    async def get_tools_names(self) -> list[str]:
        tools = await self.inspect_tools()
        return [tool.name for tool in tools]
    async def get_tool(self, tool_name: str) -> ToolInfo:
        tools = await self.inspect_tools()
        for tool_info in tools:
            if tool_info.name == tool_name:
                return tool_info
        return None
    async def get_tool_json(self,tool:ToolInfo) -> dict:
        return tool.__dict__
    async def restore_tool(self, tool_json:ToolInfo) -> ToolInfo:
        tool = ToolInfo(**tool_json)
        return tool


    