"""
Semantic Scholar API integration service.
Fetches academic papers with metadata, abstracts, and citations.
"""
import httpx
from typing import List, Dict, Optional, AsyncGenerator
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PaperMetadata:
    """Academic paper metadata from Semantic Scholar."""
    paper_id: str
    title: str
    abstract: Optional[str]
    authors: List[str]
    year: Optional[int]
    venue: Optional[str]
    citation_count: int
    url: str
    published_date: Optional[str]
    fields_of_study: List[str]

    def to_dict(self) -> Dict:
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "abstract": self.abstract,
            "authors": self.authors,
            "year": self.year,
            "venue": self.venue,
            "citation_count": self.citation_count,
            "url": self.url,
            "published_date": self.published_date,
            "fields_of_study": self.fields_of_study,
        }


class SemanticScholarServiceError(Exception):
    """Semantic Scholar service errors."""
    pass


class SemanticScholarService:
    """
    Service for interacting with Semantic Scholar API.

    API Docs: https://api.semanticscholar.org/api-docs/
    Rate Limits: 100 requests/5 minutes (unauthenticated)
                1,000 requests/5 minutes (with API key)
    """

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Semantic Scholar service.

        Args:
            api_key: Optional API key for higher rate limits
        """
        headers = {}
        if api_key:
            headers["x-api-key"] = api_key

        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=headers,
            timeout=30.0,
            follow_redirects=True
        )

    async def search_papers(
        self,
        query: str,
        year: Optional[str] = None,
        fields_of_study: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[PaperMetadata]:
        """
        Search for papers by query string.

        Args:
            query: Search query (keywords, author names, etc.)
            year: Filter by year or year range (e.g., "2023" or "2020-2023")
            fields_of_study: Filter by fields (e.g., ["Computer Science", "Medicine"])
            limit: Maximum number of results (max 100)
            offset: Pagination offset

        Returns:
            List of paper metadata

        Example:
            papers = await service.search_papers(
                query="large language models",
                year="2023-2024",
                fields_of_study=["Computer Science"],
                limit=50
            )
        """
        try:
            params = {
                "query": query,
                "limit": min(limit, 100),  # API max is 100
                "offset": offset,
                "fields": "paperId,title,abstract,authors,year,venue,citationCount,url,publicationDate,fieldsOfStudy"
            }

            if year:
                params["year"] = year
            if fields_of_study:
                params["fieldsOfStudy"] = ",".join(fields_of_study)

            response = await self.client.get("/paper/search", params=params)
            response.raise_for_status()

            data = response.json()
            papers = []

            for item in data.get("data", []):
                paper = self._parse_paper(item)
                if paper:
                    papers.append(paper)

            logger.info(f"Found {len(papers)} papers for query: {query}")
            return papers

        except httpx.HTTPStatusError as e:
            logger.error(f"Semantic Scholar API error: {e.response.status_code}")
            raise SemanticScholarServiceError(f"API request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error searching papers: {e}")
            raise SemanticScholarServiceError(f"Search failed: {e}")

    async def get_paper_details(self, paper_id: str) -> Optional[PaperMetadata]:
        """
        Get detailed information about a specific paper.

        Args:
            paper_id: Semantic Scholar paper ID

        Returns:
            Paper metadata or None if not found
        """
        try:
            params = {
                "fields": "paperId,title,abstract,authors,year,venue,citationCount,url,publicationDate,fieldsOfStudy,citations,references"
            }

            response = await self.client.get(f"/paper/{paper_id}", params=params)
            response.raise_for_status()

            data = response.json()
            return self._parse_paper(data)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Paper not found: {paper_id}")
                return None
            logger.error(f"Error fetching paper {paper_id}: {e}")
            raise SemanticScholarServiceError(f"Failed to fetch paper: {e}")

    async def get_recent_papers(
        self,
        fields_of_study: List[str],
        days_back: int = 7,
        min_citations: int = 0,
        limit: int = 100
    ) -> List[PaperMetadata]:
        """
        Get recently published papers in specific fields.

        Args:
            fields_of_study: Academic fields to search
            days_back: How many days back to search
            min_citations: Minimum citation count filter
            limit: Maximum results

        Returns:
            List of recent papers
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        year_range = f"{start_date.year}-{end_date.year}"

        all_papers = []
        for field in fields_of_study:
            papers = await self.search_papers(
                query=field,
                year=year_range,
                fields_of_study=[field],
                limit=limit
            )

            # Filter by date and citations
            filtered = [
                p for p in papers
                if p.citation_count >= min_citations
                and self._is_recent(p.published_date, days_back)
            ]

            all_papers.extend(filtered)

        # Remove duplicates and sort by citation count
        unique_papers = {p.paper_id: p for p in all_papers}.values()
        sorted_papers = sorted(
            unique_papers,
            key=lambda x: x.citation_count,
            reverse=True
        )

        return sorted_papers[:limit]

    def _parse_paper(self, data: Dict) -> Optional[PaperMetadata]:
        """Parse API response into PaperMetadata."""
        try:
            return PaperMetadata(
                paper_id=data.get("paperId", ""),
                title=data.get("title", ""),
                abstract=data.get("abstract"),
                authors=[
                    author.get("name", "Unknown")
                    for author in data.get("authors", [])
                ],
                year=data.get("year"),
                venue=data.get("venue"),
                citation_count=data.get("citationCount", 0),
                url=data.get("url", ""),
                published_date=data.get("publicationDate"),
                fields_of_study=data.get("fieldsOfStudy", [])
            )
        except Exception as e:
            logger.warning(f"Failed to parse paper: {e}")
            return None

    def _is_recent(self, published_date: Optional[str], days_back: int) -> bool:
        """Check if paper was published within the last N days."""
        if not published_date:
            return False

        try:
            pub_date = datetime.strptime(published_date, "%Y-%m-%d")
            cutoff = datetime.now() - timedelta(days=days_back)
            return pub_date >= cutoff
        except ValueError:
            return False

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
