/**
 * Message input component for composing chat messages.
 * Handles text input, submission, and streaming state.
 */
'use client';

import React, { useState, useRef, useEffect } from 'react';

interface MessageInputProps {
  onSend: (message: string) => void;
  isStreaming: boolean;
  onCancel: () => void;
  disabled?: boolean;
}

export const MessageInput: React.FC<MessageInputProps> = ({
  onSend,
  isStreaming,
  onCancel,
  disabled = false,
}) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (message.trim() && !isStreaming && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-dark-700 bg-dark-800 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="relative flex items-end gap-3">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              disabled
                ? 'Select or create a conversation to start chatting'
                : 'Type your message... (Shift+Enter for new line)'
            }
            disabled={isStreaming || disabled}
            className="
              flex-1 resize-none rounded-xl px-4 py-3
              bg-dark-700 text-white placeholder-dark-400
              border border-dark-600 focus:border-primary-500
              focus:outline-none focus:ring-2 focus:ring-primary-500/20
              disabled:opacity-50 disabled:cursor-not-allowed
              max-h-40 min-h-[52px]
            "
            rows={1}
          />

          {isStreaming ? (
            <button
              type="button"
              onClick={onCancel}
              className="
                px-4 py-3 rounded-xl
                bg-red-600 hover:bg-red-700
                text-white font-medium
                transition-colors duration-200
                flex items-center gap-2
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
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
              Stop
            </button>
          ) : (
            <button
              type="submit"
              disabled={!message.trim() || disabled}
              className="
                px-4 py-3 rounded-xl
                bg-primary-600 hover:bg-primary-700
                disabled:bg-dark-600 disabled:cursor-not-allowed
                text-white font-medium
                transition-colors duration-200
                flex items-center gap-2
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
                  d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                />
              </svg>
              Send
            </button>
          )}
        </div>

        <div className="mt-2 text-xs text-dark-400 text-center">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </form>
  );
};
