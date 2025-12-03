/**
 * Individual conversation item in the sidebar.
 * Displays conversation metadata and handles selection.
 */
'use client';

import React from 'react';
import { Conversation } from '@/types/chat';

interface ConversationItemProps {
  conversation: Conversation;
  isActive: boolean;
  onSelect: () => void;
  onDelete: () => void;
}

export const ConversationItem: React.FC<ConversationItemProps> = ({
  conversation,
  isActive,
  onSelect,
  onDelete,
}) => {
  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm(`Delete conversation "${conversation.title}"?`)) {
      onDelete();
    }
  };

  return (
    <div
      onClick={onSelect}
      className={`
        group relative flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer
        transition-all duration-200 hover:bg-dark-700
        ${isActive ? 'bg-dark-700 border-l-2 border-primary-500' : 'border-l-2 border-transparent'}
      `}
    >
      <div className="flex-1 min-w-0">
        <h3 className="text-sm font-medium text-white truncate">
          {conversation.title}
        </h3>
        <p className="text-xs text-dark-400 truncate">
          {conversation.messages.length} messages
        </p>
      </div>

      <button
        onClick={handleDelete}
        className="
          opacity-0 group-hover:opacity-100 transition-opacity
          p-1 rounded hover:bg-dark-600 text-dark-400 hover:text-red-400
        "
        aria-label="Delete conversation"
      >
        <svg
          className="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
          />
        </svg>
      </button>
    </div>
  );
};
