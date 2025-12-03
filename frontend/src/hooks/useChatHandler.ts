/**
 * Custom hook for handling chat operations.
 * Encapsulates chat logic and state management.
 */

import { useCallback } from 'react';
import { useChatStore } from '@/store/chat-store';
import { Conversation } from '@/types/chat';
import chatService from '@/services/chat-service';
import { useConversationRouter } from './useConversationRouter';

export const useChatHandler = () => {
  const {
    currentConversation,
    isStreaming,
    setIsStreaming,
    clearStreamingMessage,
    appendToStreamingMessage,
    addMessage,
    updateMessageContent,
    setError,
    setCurrentConversation,
    addConversation,
  } = useChatStore();

  const { navigateToConversation } = useConversationRouter();

  const createNewConversation = useCallback(() => {
    const newConversation: Conversation = {
      id: crypto.randomUUID(),
      title: 'New Chat',
      messages: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    addConversation(newConversation);
    setCurrentConversation(newConversation);

    // Navigate to new conversation URL
    navigateToConversation(newConversation.id);

    return newConversation;
  }, [addConversation, setCurrentConversation, navigateToConversation]);

  const sendMessage = useCallback(
    async (messageContent: string) => {
      // Create conversation if it doesn't exist
      const conversation = currentConversation || createNewConversation();

      if (isStreaming) return;

      try {
        // Add user message
        const userMessage = {
          id: crypto.randomUUID(),
          role: 'user' as const,
          content: messageContent,
          timestamp: new Date().toISOString(),
        };

        addMessage(conversation.id, userMessage);

        // Prepare streaming
        setIsStreaming(true);
        clearStreamingMessage();

        let assistantMessageId: string | null = null;

        await chatService.sendMessage(
          {
            conversation_id: conversation.id,
            message: messageContent,
          },
          {
            onChunk: (chunk) => {
              if (chunk.message_id && !assistantMessageId) {
                assistantMessageId = chunk.message_id;
              }
              appendToStreamingMessage(chunk.content);
            },
            onError: (error) => {
              setError(error.message);
              setIsStreaming(false);
              clearStreamingMessage();
            },
            onComplete: () => {
              // Get the complete streamed message
              const streamedContent = useChatStore.getState().currentStreamingMessage;

              if (streamedContent) {
                const assistantMessage = {
                  id: assistantMessageId || crypto.randomUUID(),
                  role: 'assistant' as const,
                  content: streamedContent,
                  timestamp: new Date().toISOString(),
                };

                addMessage(conversation.id, assistantMessage);
              }

              setIsStreaming(false);
              clearStreamingMessage();
            },
          }
        );
      } catch (error) {
        setError(error instanceof Error ? error.message : 'Failed to send message');
        setIsStreaming(false);
        clearStreamingMessage();
      }
    },
    [
      currentConversation,
      isStreaming,
      setIsStreaming,
      clearStreamingMessage,
      appendToStreamingMessage,
      addMessage,
      setError,
      createNewConversation,
    ]
  );

  const cancelStream = useCallback(() => {
    chatService.cancelStream();
    setIsStreaming(false);
    clearStreamingMessage();
  }, [setIsStreaming, clearStreamingMessage]);

  const currentStreamingMessage = useChatStore((state) => state.currentStreamingMessage);

  return {
    currentConversation,
    isStreaming,
    currentStreamingMessage,
    sendMessage,
    cancelStream,
    createNewConversation,
  };
};
