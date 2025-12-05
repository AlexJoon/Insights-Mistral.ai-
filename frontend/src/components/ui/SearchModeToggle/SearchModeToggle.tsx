/**
 * SearchModeToggle Component
 * iOS-style sliding toggle between RAG search (left) and Web search (right)
 *
 * Design Pattern: Controlled Component Pattern
 * Purpose: Allow users to switch between search modes with localStorage persistence
 */
'use client';

import styles from './SearchModeToggle.module.css';

export type SearchMode = 'rag' | 'web';

export interface SearchModeToggleProps {
  mode: SearchMode;
  onModeChange: (mode: SearchMode) => void;
  disabled?: boolean;
  className?: string;
}

export function SearchModeToggle({
  mode,
  onModeChange,
  disabled = false,
  className
}: SearchModeToggleProps) {
  const handleRAGClick = () => {
    if (!disabled && mode !== 'rag') {
      onModeChange('rag');
    }
  };

  const handleWebClick = () => {
    if (!disabled && mode !== 'web') {
      onModeChange('web');
    }
  };

  return (
    <div className={`${styles.toggleContainer} ${disabled ? styles.disabled : ''} ${className || ''}`}>
      <button
        onClick={handleRAGClick}
        disabled={disabled}
        className={`${styles.option} ${mode === 'rag' ? styles.active : ''}`}
        aria-label="RAG Search (Internal Database)"
        title="RAG Search (Internal Database)"
      >
        {/* Database icon */}
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <ellipse cx="12" cy="5" rx="9" ry="3" />
          <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
          <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
        </svg>
        <span className={styles.label}>RAG</span>
      </button>

      <button
        onClick={handleWebClick}
        disabled={disabled}
        className={`${styles.option} ${mode === 'web' ? styles.active : ''}`}
        aria-label="Web Search (SSRN & Semantic Scholar)"
        title="Web Search (SSRN & Semantic Scholar)"
      >
        {/* Globe/Web icon */}
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="2" y1="12" x2="22" y2="12" />
          <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
        </svg>
        <span className={styles.label}>Web</span>
      </button>

      <div
        className={`${styles.slider} ${mode === 'web' ? styles.sliderRight : styles.sliderLeft}`}
        aria-hidden="true"
      />
    </div>
  );
}
