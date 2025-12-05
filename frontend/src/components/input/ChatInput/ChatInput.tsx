/**
 * ChatInput - Copilot-style message input
 * Modular input component with send button and file upload
 */
'use client';

import { useState, useRef, KeyboardEvent } from 'react';
import { FileUpload } from '../FileUpload';
import { VoiceRecorder } from '../VoiceRecorder';
import { SearchModeToggle, SearchMode } from '@/components/ui/SearchModeToggle';
import styles from './ChatInput.module.css';

interface ChatInputProps {
  onSend: (message: string) => void;
  onFileUpload?: (file: File) => void;
  searchMode?: SearchMode;
  onSearchModeChange?: (mode: SearchMode) => void;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
}

export function ChatInput({
  onSend,
  onFileUpload,
  searchMode,
  onSearchModeChange,
  disabled = false,
  placeholder = "Message Insights...",
  maxLength = 4000,
}: ChatInputProps) {
  const [value, setValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    const trimmed = value.trim();
    if (trimmed && !disabled) {
      onSend(trimmed);
      setValue('');

      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    if (newValue.length <= maxLength) {
      setValue(newValue);

      // Auto-resize textarea
      const textarea = e.target;
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  };

  const canSend = value.trim().length > 0 && !disabled;

  const handleFileSelect = (file: File) => {
    if (onFileUpload) {
      onFileUpload(file);
    }
  };

  const handleVoiceTranscription = (text: string) => {
    // Set the transcribed text in the textarea
    setValue(text);

    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }

    // Focus the textarea
    textareaRef.current?.focus();
  };

  return (
    <div className={styles.container}>
      <div className={styles.inputWrapper}>
        {/* Textarea area */}
        <div className={styles.textareaContainer}>
          <textarea
            ref={textareaRef}
            className={styles.textarea}
            value={value}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            aria-label="Chat message input"
          />

          <button
            className={`${styles.sendButton} ${canSend ? styles.active : ''}`}
            onClick={handleSend}
            disabled={!canSend}
            aria-label="Send message"
            title="Send message (Enter)"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path
                d="M17.5 10L2.5 2.5L5.83333 10L2.5 17.5L17.5 10Z"
                fill="currentColor"
              />
            </svg>
          </button>
        </div>

        {/* Bottom action bar with icons */}
        {onFileUpload && (
          <div className={styles.actionBar}>
            <div className={styles.leftActions}>
              <FileUpload onFileSelect={handleFileSelect} disabled={disabled} />
              {searchMode !== undefined && onSearchModeChange && (
                <SearchModeToggle
                  mode={searchMode}
                  onModeChange={onSearchModeChange}
                  disabled={disabled}
                />
              )}
            </div>
            <div className={styles.rightActions}>
              <VoiceRecorder
                onTranscription={handleVoiceTranscription}
                disabled={disabled}
              />
            </div>
          </div>
        )}
      </div>

      {value.length > maxLength * 0.9 && (
        <div className={styles.counter}>
          {value.length} / {maxLength}
        </div>
      )}
    </div>
  );
}
