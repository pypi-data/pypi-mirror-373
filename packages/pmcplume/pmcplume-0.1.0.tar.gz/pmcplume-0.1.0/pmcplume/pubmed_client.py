import os
import httpx
from typing import List, Dict, Any
from pydantic import BaseModel, Field

API_KEY = os.getenv("NCBI_API_KEY", "f0f10edfc9595dd9f383f31b010c636d2a08")
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


class PubMedArticle(BaseModel):
    pmid: str
    title: str
    authors: List[str] = Field(default_factory=list)
    journal: str = ""
    pub_date: str = ""
    doi: str = ""
    abstract: str = ""


class PubMedClient:
    def __init__(self, api_key: str = API_KEY):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)

    async def search(self, query: str, max_results: int = 10) -> List[PubMedArticle]:
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "api_key": self.api_key,
        }
        r = await self.client.get(f"{BASE_URL}/esearch.fcgi", params=params)
        r.raise_for_status()
        data = r.json()
        id_list = data["esearchresult"]["idlist"]
        if not id_list:
            return []

        # 批量获取详情
        params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "xml",
            "api_key": self.api_key,
        }
        r = await self.client.get(f"{BASE_URL}/efetch.fcgi", params=params)
        r.raise_for_status()
        return self._parse_xml(r.text)

    def _parse_xml(self, xml_text: str) -> List[PubMedArticle]:
        import xml.etree.ElementTree as ET

        root = ET.fromstring(xml_text)
        articles = []
        for article in root.findall(".//PubmedArticle"):
            medline = article.find("MedlineCitation")
            art = medline.find("Article")
            pmid = medline.find("PMID").text or ""
            title = " ".join(
                n.text or "" for n in art.findall(".//ArticleTitle")
            ).strip()
            authors = [
                (f"{a.find('LastName').text or ''} {a.find('ForeName').text or ''}").strip()
                for a in art.findall(".//Author[LastName]")
            ]
            journal = art.find(".//Journal/Title").text or ""
            pub_date_node = art.find(".//PubDate")
            pub_date = f"{pub_date_node.find('Year').text or ''}-{pub_date_node.find('Month').text or ''}"
            doi_node = art.find(".//ArticleId[@IdType='doi']")
            doi = doi_node.text if doi_node is not None else ""
            abstract = " ".join(
                n.text or "" for n in art.findall(".//AbstractText")
            ).strip()

            articles.append(
                PubMedArticle(
                    pmid=pmid,
                    title=title,
                    authors=authors,
                    journal=journal,
                    pub_date=pub_date,
                    doi=doi,
                    abstract=abstract,
                )
            )
        return articles

    async def close(self):
        await self.client.aclose()
