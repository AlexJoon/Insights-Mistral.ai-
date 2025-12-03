/**
 * Main chat container component.
 * Orchestrates the chat interface with sidebar and chat area.
 */
'use client';

import React from 'react';
import { Sidebar } from './sidebar/Sidebar';
import { ChatArea } from './chat/ChatArea';
import { MessageInput } from './chat/MessageInput';
import { useChatHandler } from '@/hooks/useChatHandler';
import { useChatStore } from '@/store/chat-store';

export const ChatContainer: React.FC = () => {
  const { sendMessage, cancelStream, isStreaming } = useChatHandler();
  const { currentConversation, error, clearError } = useChatStore();

  return (
    <div className="flex h-screen bg-dark-900">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Error Banner */}
        {error && (
          <div className="bg-red-600 text-white px-4 py-3 flex items-center justify-between">
            <span className="text-sm">{error}</span>
            <button
              onClick={clearError}
              className="text-white hover:text-gray-200 ml-4"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        )}

        {/* Chat Area */}
        <ChatArea />

        {/* Message Input */}
        <MessageInput
          onSend={sendMessage}
          isStreaming={isStreaming}
          onCancel={cancelStream}
          disabled={!currentConversation}
        />
      </div>
    </div>
  );
};
