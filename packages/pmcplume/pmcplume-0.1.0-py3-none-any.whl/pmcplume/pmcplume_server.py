#!/usr/bin/env python3
import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from pmcplume.pubmed_client import PubMedClient

app = Server("pmcplume-pubfetch")


@app.call_tool()
async def fetch_pubmed(query: str, max_results: int = 5):
    """
    Fetch PubMed articles matching a query.
    """
    client = PubMedClient()
    try:
        articles = await client.search(query, max_results)
        return [
            {
                "type": "text",
                "text": json.dumps(a.model_dump(), ensure_ascii=False, indent=2),
            }
        ]
    finally:
        await client.close()


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
