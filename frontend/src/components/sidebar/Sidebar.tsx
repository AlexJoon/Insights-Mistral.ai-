/**
 * Main sidebar component for conversation list.
 * Handles conversation navigation and management.
 */
'use client';

import React, { useEffect } from 'react';
import { useChatStore } from '@/store/chat-store';
import { ConversationItem } from './ConversationItem';
import conversationService from '@/services/conversation-service';

export const Sidebar: React.FC = () => {
  const {
    conversations,
    currentConversation,
    setConversations,
    setCurrentConversation,
    addConversation,
    deleteConversation,
    setError,
  } = useChatStore();

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    const response = await conversationService.getAllConversations();

    if (response.error) {
      setError(response.error.message);
      return;
    }

    if (response.data) {
      setConversations(response.data.conversations);
    }
  };

  const handleNewConversation = async () => {
    const response = await conversationService.createConversation();

    if (response.error) {
      setError(response.error.message);
      return;
    }

    if (response.data) {
      addConversation(response.data);
      setCurrentConversation(response.data);
    }
  };

  const handleDeleteConversation = async (conversationId: string) => {
    const response = await conversationService.deleteConversation(conversationId);

    if (response.error) {
      setError(response.error.message);
      return;
    }

    deleteConversation(conversationId);
  };

  return (
    <div className="w-80 bg-dark-800 border-r border-dark-700 flex flex-col h-screen">
      {/* Header */}
      <div className="p-4 border-b border-dark-700">
        <button
          onClick={handleNewConversation}
          className="
            w-full px-4 py-2.5 bg-primary-600 hover:bg-primary-700
            text-white font-medium rounded-lg
            transition-colors duration-200
            flex items-center justify-center gap-2
          "
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
              d="M12 4v16m8-8H4"
            />
          </svg>
          New Conversation
        </button>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto p-2">
        {conversations.length === 0 ? (
          <div className="text-center text-dark-400 py-8 px-4">
            <p className="text-sm">No conversations yet</p>
            <p className="text-xs mt-1">Create a new conversation to get started</p>
          </div>
        ) : (
          <div className="space-y-1">
            {conversations.map((conversation) => (
              <ConversationItem
                key={conversation.id}
                conversation={conversation}
                isActive={currentConversation?.id === conversation.id}
                onSelect={() => setCurrentConversation(conversation)}
                onDelete={() => handleDeleteConversation(conversation.id)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-dark-700">
        <div className="text-xs text-dark-400 text-center">
          <p>Powered by Mistral AI</p>
        </div>
      </div>
    </div>
  );
};
