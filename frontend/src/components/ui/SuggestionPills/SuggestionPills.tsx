/**
 * SuggestionPills - Copilot-style suggestion pills
 * Small pill-shaped buttons for quick actions
 */
'use client';

import styles from './SuggestionPills.module.css';

interface Suggestion {
  id: string;
  label: string;
  onClick: () => void;
}

interface SuggestionPillsProps {
  suggestions: Suggestion[];
}

export function SuggestionPills({ suggestions }: SuggestionPillsProps) {
  return (
    <div className={styles.container}>
      {suggestions.map((suggestion) => (
        <button
          key={suggestion.id}
          className={styles.pill}
          onClick={suggestion.onClick}
        >
          {suggestion.label}
        </button>
      ))}
    </div>
  );
}
