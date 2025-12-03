/**
 * Custom hook for handling chat operations.
 * Encapsulates chat logic and state management.
 */

import { useCallback } from 'react';
import { useChatStore } from '@/store/chat-store';
import chatService from '@/services/chat-service';

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
  } = useChatStore();

  const sendMessage = useCallback(
    async (messageContent: string) => {
      if (!currentConversation || isStreaming) return;

      try {
        // Add user message
        const userMessage = {
          id: crypto.randomUUID(),
          role: 'user' as const,
          content: messageContent,
          timestamp: new Date().toISOString(),
        };

        addMessage(currentConversation.id, userMessage);

        // Prepare streaming
        setIsStreaming(true);
        clearStreamingMessage();

        let assistantMessageId: string | null = null;

        await chatService.sendMessage(
          {
            conversation_id: currentConversation.id,
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

                addMessage(currentConversation.id, assistantMessage);
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
    ]
  );

  const cancelStream = useCallback(() => {
    chatService.cancelStream();
    setIsStreaming(false);
    clearStreamingMessage();
  }, [setIsStreaming, clearStreamingMessage]);

  return {
    sendMessage,
    cancelStream,
    isStreaming,
  };
};
