#!/usr/bin/env python3
"""
Trendyol MCP Server

An MCP server that provides Trendyol product search functionality.
"""

import asyncio
import json
import sys
from typing import Any, Sequence

import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# Import the search function from our existing module
from search_trendyol import search_trendyol
from get_product_details import get_product_details
from get_product_image import get_product_image
from get_product_reviews import get_product_reviews

# Create the server instance
server = Server("trendyol-search")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="search_trendyol",
            description="Search for products on Trendyol with detailed information including names, descriptions, and prices",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query/product name to search for on Trendyol",
                    },
                    "target_count": {
                        "type": "integer",
                        "description": "Number of products to retrieve (default: 100, max: 100)",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 100,
                    },
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="get_product_details",
            description="Get detailed information about a specific product including title, price, description, features, rating, and brand",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The product name to search for and get details",
                    }
                },
                "required": ["product_name"],
            },
        ),
        types.Tool(
            name="get_product_image",
            description="Extract and display product images from the product gallery carousel",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The product name to search for and get images",
                    }
                },
                "required": ["product_name"],
            },
        ),
        types.Tool(
            name="get_product_reviews",
            description="Extract customer reviews and comments for a specific product",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The product name to search for and get reviews",
                    }
                },
                "required": ["product_name"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent]:
    """
    Handle tool calls from the client.
    """
    if not arguments:
        raise ValueError("Missing arguments")

    try:
        # Capture the output by redirecting stdout
        import io
        import contextlib

        # Create a string buffer to capture output
        captured_output = io.StringIO()

        # Redirect stdout to capture the function's print statements
        with contextlib.redirect_stdout(captured_output):
            if name == "search_trendyol":
                query = arguments.get("query")
                if not query:
                    raise ValueError("Missing required argument: query")

                target_count = arguments.get("target_count", 100)
                max_scroll_attempts = arguments.get("max_scroll_attempts", 15)

                # Validate arguments
                if target_count < 1 or target_count > 100:
                    raise ValueError("target_count must be between 1 and 100")

                if max_scroll_attempts < 1 or max_scroll_attempts > 30:
                    raise ValueError("max_scroll_attempts must be between 1 and 30")

                # Call the search function
                search_trendyol(query, target_count, max_scroll_attempts)

            elif name == "get_product_details":
                product_name = arguments.get("product_name")
                if not product_name:
                    raise ValueError("Missing required argument: product_name")

                # Call the product details function
                get_product_details(product_name)

            elif name == "get_product_image":
                product_name = arguments.get("product_name")
                if not product_name:
                    raise ValueError("Missing required argument: product_name")

                # Call the product image function
                get_product_image(product_name)

            elif name == "get_product_reviews":
                product_name = arguments.get("product_name")
                if not product_name:
                    raise ValueError("Missing required argument: product_name")

                # Call the product reviews function
                get_product_reviews(product_name)

            else:
                raise ValueError(f"Unknown tool: {name}")

        # Get the captured output
        captured_results = captured_output.getvalue()

        return [
            types.TextContent(
                type="text",
                text=f"Trendyol {name} Results:\n\n{captured_results}",
            )
        ]

    except Exception as e:
        error_message = f"Error executing {name}: {str(e)}"
        return [
            types.TextContent(
                type="text",
                text=error_message,
            )
        ]


async def main():
    """Main entry point for the server."""
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="trendyol-search",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
