import os, asyncio, httpx, json, xml.etree.ElementTree as ET
from mcp.server.fastmcp import FastMCP
from pydantic import Field

API_KEY = os.getenv("PUBMED_API_KEY", "")
mcp = FastMCP("pubmed-mcp")

@mcp.tool(name="pubmed_search", description="Search PubMed")
async def search(
    query: str = Field(description="PubMed search string"),
    max_results: int = Field(20, ge=1, le=100)
) -> list[dict]:
    if not API_KEY:
        return [{"error": "PUBMED_API_KEY not set"}]
    async with httpx.AsyncClient(timeout=30) as client:
        r1 = await client.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            params={"db": "pubmed", "term": query, "retmax": max_results, "retmode": "json", "api_key": API_KEY}
        )
        ids = r1.json()['esearchresult']['idlist']
        if not ids:
            return []
        r2 = await client.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
            params={"db": "pubmed", "id": ",".join(ids), "retmode": "xml", "api_key": API_KEY}
        )
        root = ET.fromstring(r2.text)
        return [
            {
                "pmid": art.findtext(".//PMID"),
                "title": art.findtext(".//ArticleTitle") or "",
                "authors": [f"{a.findtext('.//LastName')} {a.findtext('.//Initials')}".strip()
                            for a in art.findall(".//Author")],
                "journal": art.findtext(".//Journal/Title") or "",
                "pub_date": f"{art.findtext('.//PubDate/Year')}-{art.findtext('.//PubDate/Month')}",
                "abstract": art.findtext(".//Abstract/AbstractText") or ""
            }
            for art in root.findall(".//PubmedArticle")
        ]

def run():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    run()
