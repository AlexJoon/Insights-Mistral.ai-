/**
 * CenteredWelcome - Copilot-style centered welcome message
 * Displays greeting and input in center of screen
 */
'use client';

import { ReactNode } from 'react';
import styles from './CenteredWelcome.module.css';

interface CenteredWelcomeProps {
  greeting: string;
  input: ReactNode;
  suggestions?: ReactNode;
}

export function CenteredWelcome({ greeting, input, suggestions }: CenteredWelcomeProps) {
  return (
    <div className={styles.container}>
      <div className={styles.content}>
        <h1 className={styles.greeting}>{greeting}</h1>
        <div className={styles.inputSection}>
          {input}
        </div>
        {suggestions && (
          <div className={styles.suggestionsSection}>
            {suggestions}
          </div>
        )}
      </div>
    </div>
  );
}
