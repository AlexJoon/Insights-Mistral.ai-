"""
Email service for sending notifications and digests.
Uses SendGrid for reliable email delivery.
"""
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, Personalization
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EmailConfig:
    """Email configuration."""
    api_key: str
    from_email: str
    from_name: str


class EmailServiceError(Exception):
    """Email service errors."""
    pass


class EmailService:
    """
    Service for sending emails via SendGrid.

    Handles research digests, notifications, and alerts.
    """

    def __init__(self, config: EmailConfig):
        """
        Initialize email service.

        Args:
            config: Email configuration with API key and sender info
        """
        self.config = config
        self.client = sendgrid.SendGridAPIClient(api_key=config.api_key)
        self.from_email = Email(config.from_email, config.from_name)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send a single email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text fallback (optional)

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=To(to_email),
                subject=subject,
                plain_text_content=Content("text/plain", text_content or ""),
                html_content=Content("text/html", html_content)
            )

            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Email sending failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    async def send_weekly_digest(
        self,
        to_email: str,
        user_name: str,
        papers: List[Dict],
        topic: str
    ) -> bool:
        """
        Send weekly research digest email.

        Args:
            to_email: Recipient email
            user_name: Recipient name
            papers: List of paper summaries
            topic: Research topic

        Returns:
            True if sent successfully
        """
        try:
            # Generate email content
            subject = f"Weekly Research Digest: {topic}"
            html_content = self._generate_digest_html(user_name, papers, topic)
            text_content = self._generate_digest_text(user_name, papers, topic)

            return await self.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )

        except Exception as e:
            logger.error(f"Failed to send digest to {to_email}: {e}")
            return False

    async def send_batch_digest(
        self,
        recipients: List[Dict]
    ) -> Dict[str, int]:
        """
        Send digest to multiple recipients.

        Args:
            recipients: List of dicts with to_email, user_name, papers, topic

        Returns:
            Dict with sent/failed counts
        """
        sent = 0
        failed = 0

        for recipient in recipients:
            success = await self.send_weekly_digest(
                to_email=recipient["to_email"],
                user_name=recipient["user_name"],
                papers=recipient["papers"],
                topic=recipient["topic"]
            )

            if success:
                sent += 1
            else:
                failed += 1

        logger.info(f"Batch digest: {sent} sent, {failed} failed")

        return {
            "sent": sent,
            "failed": failed,
            "total": len(recipients)
        }

    def _generate_digest_html(
        self,
        user_name: str,
        papers: List[Dict],
        topic: str
    ) -> str:
        """Generate HTML email content for digest."""

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weekly Research Digest</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            border-bottom: 3px solid #0ea5e9;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #0ea5e9;
            margin: 0;
            font-size: 28px;
        }}
        .subtitle {{
            color: #64748b;
            margin-top: 8px;
            font-size: 14px;
        }}
        .paper {{
            border-left: 4px solid #0ea5e9;
            padding-left: 16px;
            margin-bottom: 24px;
            background-color: #f8fafc;
            padding: 16px;
            border-radius: 4px;
        }}
        .paper-title {{
            font-size: 18px;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 8px;
        }}
        .paper-authors {{
            color: #64748b;
            font-size: 14px;
            margin-bottom: 8px;
        }}
        .paper-summary {{
            color: #475569;
            font-size: 15px;
            line-height: 1.6;
        }}
        .paper-link {{
            display: inline-block;
            margin-top: 8px;
            color: #0ea5e9;
            text-decoration: none;
            font-size: 14px;
        }}
        .paper-link:hover {{
            text-decoration: underline;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
            text-align: center;
            color: #94a3b8;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 Weekly Research Digest</h1>
            <div class="subtitle">Your personalized update on {topic}</div>
        </div>

        <p>Hi {user_name},</p>
        <p>Here are this week's top {len(papers)} papers in <strong>{topic}</strong>:</p>
"""

        # Add each paper
        for i, paper in enumerate(papers, 1):
            authors_str = ", ".join(paper.get("authors", [])[:3])
            if len(paper.get("authors", [])) > 3:
                authors_str += " et al."

            html += f"""
        <div class="paper">
            <div class="paper-title">{i}. {paper.get("title", "Untitled")}</div>
            <div class="paper-authors">{authors_str}</div>
            <div class="paper-summary">{paper.get("summary", "No summary available.")}</div>
            <a href="{paper.get("url", "#")}" class="paper-link">Read paper →</a>
        </div>
"""

        html += """
        <div class="footer">
            <p>This digest was generated by Insights AI</p>
            <p><a href="#" style="color: #64748b;">Unsubscribe</a> | <a href="#" style="color: #64748b;">Update preferences</a></p>
        </div>
    </div>
</body>
</html>
"""

        return html

    def _generate_digest_text(
        self,
        user_name: str,
        papers: List[Dict],
        topic: str
    ) -> str:
        """Generate plain text email content for digest."""

        text = f"""
Weekly Research Digest: {topic}

Hi {user_name},

Here are this week's top {len(papers)} papers in {topic}:

"""

        for i, paper in enumerate(papers, 1):
            authors_str = ", ".join(paper.get("authors", [])[:3])
            if len(paper.get("authors", [])) > 3:
                authors_str += " et al."

            text += f"""
{i}. {paper.get("title", "Untitled")}
   Authors: {authors_str}
   {paper.get("summary", "No summary available.")}
   Read more: {paper.get("url", "N/A")}

"""

        text += """
---
This digest was generated by Insights AI
Unsubscribe | Update preferences
"""

        return text
