/**
 * Message bubble component for displaying chat messages.
 * Supports both user and assistant messages with different styling.
 * Renders markdown as semantic HTML.
 */
'use client';

import React, { useMemo } from 'react';
import { Message } from '@/types/chat';
import { parseMarkdownToHTML } from '@/utils/markdown';

interface MessageBubbleProps {
  message: Message;
  isStreaming?: boolean;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  isStreaming = false,
}) => {
  const isUser = message.role === 'user';

  const formattedContent = useMemo(() => {
    if (isUser) {
      return message.content;
    }
    return parseMarkdownToHTML(message.content);
  }, [message.content, isUser]);

  return (
    <div className={'flex ' + (isUser ? 'justify-end' : 'justify-start') + ' mb-4'}>
      <div
        className={'max-w-3xl px-4 py-3 rounded-2xl ' +
          (isUser ? 'bg-primary-600 text-white' : 'bg-dark-700 text-white border border-dark-600')
        }
      >
        <div className="flex items-center gap-2 mb-1.5">
          <span className="text-xs font-semibold opacity-70">
            {isUser ? 'You' : 'Assistant'}
          </span>
          {isStreaming && (
            <div className="flex gap-1">
              <span className="w-1.5 h-1.5 bg-primary-400 rounded-full animate-pulse"></span>
              <span className="w-1.5 h-1.5 bg-primary-400 rounded-full animate-pulse delay-75"></span>
              <span className="w-1.5 h-1.5 bg-primary-400 rounded-full animate-pulse delay-150"></span>
            </div>
          )}
        </div>

        {isUser ? (
          <div className="text-sm leading-relaxed whitespace-pre-wrap break-words">
            {message.content}
          </div>
        ) : (
          <article
            className="formatted-message text-sm leading-relaxed break-words"
            dangerouslySetInnerHTML={{ __html: formattedContent }}
          />
        )}

        <div className="text-xs opacity-50 mt-2">
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>
    </div>
  );
};
