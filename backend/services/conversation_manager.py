"""
Conversation management service.
Handles storage and retrieval of conversations.
"""
from typing import Dict, Optional, List
from backend.models.chat import Conversation, Message
from backend.utils.logger import setup_logger


logger = setup_logger(__name__)


class ConversationManager:
    """
    Manages conversation state and persistence.
    In a production environment, this would interface with a database.
    """

    def __init__(self):
        """Initialize the conversation manager with in-memory storage."""
        self._conversations: Dict[str, Conversation] = {}

    def create_conversation(self, title: str = "New Conversation") -> Conversation:
        """
        Create a new conversation.

        Args:
            title: The conversation title

        Returns:
            The created conversation
        """
        conversation = Conversation(title=title)
        self._conversations[conversation.id] = conversation
        logger.info(f"Created new conversation: {conversation.id}")
        return conversation

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Retrieve a conversation by ID.

        Args:
            conversation_id: The conversation ID

        Returns:
            The conversation if found, None otherwise
        """
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            logger.warning(f"Conversation not found: {conversation_id}")
        return conversation

    def get_or_create_conversation(self, conversation_id: Optional[str] = None) -> Conversation:
        """
        Get an existing conversation or create a new one.

        Args:
            conversation_id: Optional conversation ID

        Returns:
            The conversation
        """
        if conversation_id:
            conversation = self.get_conversation(conversation_id)
            if conversation:
                return conversation
            logger.info(f"Conversation {conversation_id} not found, creating new one")

        return self.create_conversation()

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str
    ) -> Optional[Message]:
        """
        Add a message to a conversation.

        Args:
            conversation_id: The conversation ID
            role: The message role (user, assistant, system)
            content: The message content

        Returns:
            The created message, or None if conversation not found
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None

        message = conversation.add_message(role, content)
        logger.info(f"Added message to conversation {conversation_id}: {message.id}")
        return message

    def get_all_conversations(self) -> List[Conversation]:
        """
        Get all conversations.

        Returns:
            List of all conversations
        """
        return list(self._conversations.values())

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.

        Args:
            conversation_id: The conversation ID

        Returns:
            True if deleted, False if not found
        """
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            logger.info(f"Deleted conversation: {conversation_id}")
            return True
        return False

    def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        """
        Update a conversation's title.

        Args:
            conversation_id: The conversation ID
            title: The new title

        Returns:
            True if updated, False if not found
        """
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.title = title
            logger.info(f"Updated conversation title: {conversation_id}")
            return True
        return False
