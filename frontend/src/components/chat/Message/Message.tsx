/**
 * Message Component
 * Modular component for rendering chat messages with markdown support
 */
import { parseMarkdownToHTML } from '@/utils/markdown';
import styles from './Message.module.css';

export interface MessageProps {
  content: string;
  role: 'user' | 'assistant';
  className?: string;
}

export function Message({ content, role, className }: MessageProps) {
  const messageClass = `${styles.message} ${
    role === 'user' ? styles.userMessage : styles.assistantMessage
  } ${className || ''}`;

  return (
    <div className={messageClass}>
      <div
        className={styles.messageContent}
        dangerouslySetInnerHTML={{ __html: parseMarkdownToHTML(content) }}
      />
    </div>
  );
}
