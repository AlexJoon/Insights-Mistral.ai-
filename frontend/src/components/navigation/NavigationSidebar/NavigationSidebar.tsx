/**
 * NavigationSidebar - Minimalist Copilot-style sidebar
 * Modular navigation component
 */
'use client';

import { KeyboardShortcuts } from '@/components/navigation/KeyboardShortcuts';
import { ApiStatus } from '@/components/status/ApiStatus';
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
        {/* Keyboard Shortcuts */}
        <KeyboardShortcuts
          className={styles.control}
          iconClassName={styles.controlIcon}
          labelClassName={styles.controlLabel}
        />

        {/* API Status */}
        <ApiStatus
          className={styles.control}
          iconClassName={styles.controlIcon}
          labelClassName={styles.controlLabel}
        />
      </div>
    </div>
  );
}
