/**
 * Message Component
 * Modular component for rendering chat messages with markdown support
 */
import { parseMarkdownToHTML } from '@/utils/markdown';
import { MessageActions } from '../MessageActions';
import { MessageRole } from '@/types/chat';
import styles from './Message.module.css';

export interface MessageProps {
  content: string;
  role: MessageRole;
  isStreaming?: boolean;
  onRetry?: () => void;
  className?: string;
}

export function Message({ content, role, isStreaming, onRetry, className }: MessageProps) {
  const messageClass = `${styles.message} ${
    role === 'user' ? styles.userMessage : styles.assistantMessage
  } ${className || ''}`;

  const showActions = role === 'assistant' && !isStreaming && content.length > 0;

  return (
    <div className={messageClass}>
      <div
        className={styles.messageContent}
        dangerouslySetInnerHTML={{ __html: parseMarkdownToHTML(content) }}
      />
      {showActions && (
        <MessageActions content={content} onRetry={onRetry} />
      )}
    </div>
  );
}
