/**
 * NavigationSidebar - Minimalist Copilot-style sidebar
 * Modular navigation component with theme toggle
 */
'use client';

import { useTheme } from '@/design-system/theme';
import styles from './NavigationSidebar.module.css';

interface NavigationItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  onClick: () => void;
  badge?: number;
}

interface NavigationSidebarProps {
  items?: NavigationItem[];
  branding?: React.ReactNode;
  children?: React.ReactNode;
}

export function NavigationSidebar({ items = [], branding, children }: NavigationSidebarProps) {
  const { mode, toggleMode } = useTheme();

  return (
    <div className={styles.sidebar}>
      {/* Branding */}
      {branding && (
        <div className={styles.branding}>
          {branding}
        </div>
      )}

      {/* Navigation Items */}
      <nav className={styles.nav}>
        {items.map((item) => (
          <button
            key={item.id}
            className={styles.navItem}
            onClick={item.onClick}
            title={item.label}
          >
            <div className={styles.navIcon}>{item.icon}</div>
            <span className={styles.navLabel}>{item.label}</span>
            {item.badge !== undefined && item.badge > 0 && (
              <span className={styles.badge}>{item.badge}</span>
            )}
          </button>
        ))}
      </nav>

      {/* Children (e.g., ConversationList) */}
      {children}

      {/* Footer Controls */}
      <div className={styles.footer}>
        {/* Theme Toggle */}
        <button
          className={styles.control}
          onClick={toggleMode}
          title={`Switch to ${mode === 'dark' ? 'light' : 'dark'} mode`}
        >
          <div className={styles.controlIcon}>
            {mode === 'dark' ? (
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path
                  d="M10 2.5V4.5M10 15.5V17.5M4.5 10H2.5M17.5 10H15.5M15.3033 15.3033L13.8891 13.8891M15.3033 4.69670L13.8891 6.11091M4.69670 15.3033L6.11091 13.8891M4.69670 4.69670L6.11091 6.11091M13.5 10C13.5 11.933 11.933 13.5 10 13.5C8.067 13.5 6.5 11.933 6.5 10C6.5 8.067 8.067 6.5 10 6.5C11.933 6.5 13.5 8.067 13.5 10Z"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            ) : (
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path
                  d="M17.5 11.0833C17.3333 12.7083 16.5833 14.1667 15.4167 15.25C13.9167 16.6667 11.9167 17.5 9.66667 17.5C5.25 17.5 1.66667 13.9167 1.66667 9.5C1.66667 6.08333 3.91667 3.16667 7.08333 2.25C7.25 2.16667 7.41667 2.16667 7.58333 2.25C7.75 2.33333 7.83333 2.5 7.83333 2.66667C7.83333 3.08333 7.91667 3.5 8 3.91667C8.16667 4.75 8.5 5.5 9 6.16667C10 7.5 11.5 8.33333 13.1667 8.33333C13.5833 8.33333 14 8.25 14.4167 8.16667C14.5833 8.16667 14.75 8.25 14.8333 8.33333C14.9167 8.5 15 8.66667 14.9167 8.83333C14.75 9.58333 14.75 10.3333 14.9167 11.0833H17.5Z"
                  fill="currentColor"
                />
              </svg>
            )}
          </div>
          <span className={styles.controlLabel}>Theme</span>
        </button>
      </div>
    </div>
  );
}
