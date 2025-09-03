# -*- coding: utf-8 -*-
# Copyright (c) 2025 yaqiang.sun.
# This source code is licensed under the license found in the LICENSE file
# in the root directory of this source tree.
#########################################################################
# Author: yaqiangsun
# Created Time: 2025/09/03 19:27:51
########################################################################


from fastmcp import FastMCP

import httpx
import asyncio

async def fetch_openapi_json(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()  # raise error when request state code is not 2xx
            return response.json()       # return json data, which is a Python dict
        except httpx.RequestError as e:
            print(f"Request error: {e}")
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"Other error: {e}")


async def get_mcp(base_url):
    url = f"{base_url}/openapi.json"  # openapi.json address
    openapi_spec = await fetch_openapi_json(url)
    if openapi_spec:
        client = httpx.AsyncClient(base_url="base_url")

        # Create the MCP server from the OpenAPI spec
        mcp = FastMCP.from_openapi(
            openapi_spec=openapi_spec,
            client=client,
            name="JSONPlaceholder MCP Server"
        )
        return mcp





