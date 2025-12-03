"""
Paper summarization service using Mistral LLM.
Generates concise summaries of academic papers for digests.
"""
import httpx
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PaperSummary:
    """Summarized paper information."""
    paper_id: str
    title: str
    summary: str
    key_findings: List[str]
    relevance_score: float

    def to_dict(self) -> Dict:
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "summary": self.summary,
            "key_findings": self.key_findings,
            "relevance_score": self.relevance_score
        }


class PaperSummarizationService:
    """
    Service for summarizing academic papers using Mistral LLM.

    Generates concise summaries suitable for weekly digests.
    """

    def __init__(self, api_key: str, model: str = "mistral-large-latest"):
        """
        Initialize summarization service.

        Args:
            api_key: Mistral API key
            model: Mistral model to use
        """
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient(
            timeout=120.0,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )

    async def summarize_paper(
        self,
        title: str,
        abstract: str,
        authors: List[str],
        user_interests: Optional[List[str]] = None
    ) -> PaperSummary:
        """
        Generate a concise summary of a paper.

        Args:
            title: Paper title
            abstract: Paper abstract
            authors: List of authors
            user_interests: Optional user interests for relevance scoring

        Returns:
            Paper summary with key findings
        """
        try:
            # Build prompt
            prompt = self._build_summary_prompt(
                title, abstract, authors, user_interests
            )

            # Call Mistral API
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert academic research assistant. Your job is to summarize research papers concisely for busy researchers."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,  # Low temperature for factual summaries
                "max_tokens": 500
            }

            response = await self.client.post(
                "https://api.mistral.ai/v1/chat/completions",
                json=payload
            )
            response.raise_for_status()

            data = response.json()
            summary_text = data["choices"][0]["message"]["content"]

            # Parse the summary (extract key findings and relevance)
            key_findings, relevance = self._parse_summary(summary_text)

            return PaperSummary(
                paper_id="",  # Set by caller
                title=title,
                summary=summary_text,
                key_findings=key_findings,
                relevance_score=relevance
            )

        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            # Return basic summary if AI fails
            return PaperSummary(
                paper_id="",
                title=title,
                summary=abstract[:300] + "...",
                key_findings=[],
                relevance_score=0.5
            )

    async def summarize_papers_batch(
        self,
        papers: List[Dict],
        user_interests: Optional[List[str]] = None
    ) -> List[PaperSummary]:
        """
        Summarize multiple papers.

        Args:
            papers: List of paper dicts with title, abstract, authors
            user_interests: User research interests

        Returns:
            List of paper summaries
        """
        summaries = []

        for paper in papers:
            try:
                summary = await self.summarize_paper(
                    title=paper.get("title", ""),
                    abstract=paper.get("abstract", ""),
                    authors=paper.get("authors", []),
                    user_interests=user_interests
                )
                summary.paper_id = paper.get("paper_id", "")
                summaries.append(summary)

            except Exception as e:
                logger.error(f"Failed to summarize paper: {e}")
                continue

        return summaries

    async def generate_digest_summary(
        self,
        papers: List[PaperSummary],
        topic: str
    ) -> str:
        """
        Generate a weekly digest summary from multiple papers.

        Args:
            papers: List of paper summaries
            topic: Research topic/field

        Returns:
            Digest text suitable for email
        """
        try:
            prompt = f"""
I have {len(papers)} new research papers in {topic} from this week.
Please write a brief (2-3 paragraphs) overview highlighting the main themes and trends.

Papers:
"""
            for i, paper in enumerate(papers[:10], 1):  # Limit to top 10
                prompt += f"\n{i}. {paper.title}\n   Summary: {paper.summary[:200]}...\n"

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a research newsletter writer. Create engaging overviews of recent research."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.5,
                "max_tokens": 400
            }

            response = await self.client.post(
                "https://api.mistral.ai/v1/chat/completions",
                json=payload
            )
            response.raise_for_status()

            data = response.json()
            return data["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Digest generation failed: {e}")
            return f"This week's top {len(papers)} papers in {topic}."

    def _build_summary_prompt(
        self,
        title: str,
        abstract: str,
        authors: List[str],
        user_interests: Optional[List[str]]
    ) -> str:
        """Build prompt for paper summarization."""
        prompt = f"""
Summarize this research paper in 2-3 sentences. Focus on:
1. Main contribution
2. Key findings
3. Significance

Title: {title}

Authors: {', '.join(authors[:5])}

Abstract:
{abstract}
"""

        if user_interests:
            prompt += f"\n\nUser Research Interests: {', '.join(user_interests)}"
            prompt += "\nNote: Emphasize relevance to these interests if applicable."

        prompt += "\n\nProvide a concise summary suitable for a research digest."

        return prompt

    def _parse_summary(self, summary_text: str) -> tuple[List[str], float]:
        """
        Parse summary to extract key findings and relevance.

        Args:
            summary_text: Generated summary

        Returns:
            Tuple of (key_findings, relevance_score)
        """
        # Simple parsing - can be enhanced with structured output
        key_findings = []
        relevance_score = 0.7  # Default relevance

        # Extract bullet points if present
        lines = summary_text.split("\n")
        for line in lines:
            if line.strip().startswith(("-", "•", "*", "1.", "2.", "3.")):
                finding = line.strip().lstrip("-•*123456789. ")
                if finding:
                    key_findings.append(finding)

        # If no structured findings, use sentences
        if not key_findings:
            sentences = summary_text.split(". ")
            key_findings = [s.strip() + "." for s in sentences[:3] if s.strip()]

        return key_findings, relevance_score

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
