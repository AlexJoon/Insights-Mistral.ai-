/**
 * Main chat area component.
 * Displays messages and handles scrolling behavior.
 */
'use client';

import React, { useEffect, useRef } from 'react';
import { useChatStore } from '@/store/chat-store';
import { MessageBubble } from './MessageBubble';
import { Message } from '@/types/chat';

export const ChatArea: React.FC = () => {
  const { currentConversation, isStreaming, currentStreamingMessage } = useChatStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [currentConversation?.messages, currentStreamingMessage]);

  if (!currentConversation) {
    return (
      <div className="flex-1 flex items-center justify-center bg-dark-900">
        <div className="text-center max-w-md px-4">
          <div className="mb-4">
            <svg
              className="w-16 h-16 mx-auto text-dark-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-white mb-2">
            Welcome to Mistral Chat
          </h2>
          <p className="text-dark-400">
            Select a conversation from the sidebar or create a new one to get started
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto bg-dark-900 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Conversation Header */}
        <div className="mb-6 pb-4 border-b border-dark-700">
          <h1 className="text-2xl font-bold text-white">
            {currentConversation.title}
          </h1>
          <p className="text-sm text-dark-400 mt-1">
            {currentConversation.messages.length} messages
          </p>
        </div>

        {/* Messages */}
        {currentConversation.messages.length === 0 ? (
          <div className="text-center text-dark-400 py-12">
            <p>No messages yet. Start the conversation below!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {currentConversation.messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}

            {/* Streaming Message */}
            {isStreaming && currentStreamingMessage && (
              <MessageBubble
                message={{
                  id: 'streaming',
                  role: 'assistant',
                  content: currentStreamingMessage,
                  timestamp: new Date().toISOString(),
                }}
                isStreaming={true}
              />
            )}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};
