import os
import httpx
from urllib.parse import quote_plus
from mcp.server.fastmcp import FastMCP

# 创建MCP服务器
mcp = FastMCP("NCBI Search Server")

NCBI_API_KEY = os.getenv("NCBI_API_KEY")
NCBI_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

async def make_ncbi_request(url: str) -> str | None:
    """向 NCBI 发送请求，返回文本内容"""
    headers = {"Accept": "text/plain"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"NCBI 请求失败: {e}")
            return None

@mcp.tool()
async def get_ncbi_data(locus: str) -> dict:
    """
    根据用户输入的 locus 获取 NCBI 对应的 GenBank 数据。
    """
    url = (
        f"{NCBI_BASE_URL}?db=nuccore&id={quote_plus(locus.strip())}"
        f"&rettype=gb&retmode=text"
    )
    raw_data = await make_ncbi_request(url)
    if not raw_data:
        return {"error": "未能获取到数据"}

    return {"data":raw_data}


if __name__ == "__main__":
    mcp.run(transport="stdio")
