/**
 * AppLayout - Copilot-style centered layout
 * Full-width centered content with overlay sidebar
 */
'use client';

import { ReactNode, useState } from 'react';
import { HeaderMenu } from '@/components/navigation/HeaderMenu';
import { ThemeToggle } from '@/components/navigation/ThemeToggle';
import { HelpButton } from '@/components/ui/HelpButton';
import styles from './AppLayout.module.css';

interface AppLayoutProps {
  sidebar: ReactNode;
  children: ReactNode;
}

export function AppLayout({ sidebar, children }: AppLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className={styles.layout}>
      {/* Hamburger Menu Button */}
      <button
        className={styles.menuButton}
        onClick={() => setSidebarOpen(!sidebarOpen)}
        aria-label="Toggle menu"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path
            d="M3 12H21M3 6H21M3 18H21"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {/* Header Controls - Top Right */}
      <div className={styles.headerControls}>
        <ThemeToggle />
        <HeaderMenu />
      </div>

      {/* Overlay Sidebar */}
      <div
        className={`${styles.sidebarOverlay} ${sidebarOpen ? styles.open : ''}`}
        onClick={() => setSidebarOpen(false)}
      />

      <aside className={`${styles.sidebar} ${sidebarOpen ? styles.open : ''}`}>
        {sidebar}
      </aside>

      {/* Main Content - Centered */}
      <main className={styles.main}>
        {children}
      </main>

      {/* Help Button - Fixed Bottom Right */}
      <HelpButton />
    </div>
  );
}
