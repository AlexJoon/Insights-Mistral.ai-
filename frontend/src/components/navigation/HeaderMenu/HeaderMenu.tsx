/**
 * HeaderMenu Component
 * Hamburger menu button with dropdown for Profile, Settings, and Contact
 */
'use client';

import { useState, useRef, useEffect } from 'react';
import styles from './HeaderMenu.module.css';

export interface MenuItem {
  label: string;
  href: string;
  icon?: React.ReactNode;
}

export interface HeaderMenuProps {
  className?: string;
}

const defaultMenuItems: MenuItem[] = [
  {
    label: 'Profile',
    href: '#',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
        <circle cx="12" cy="7" r="4" />
      </svg>
    )
  },
  {
    label: 'Settings',
    href: '#',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="12" r="3" />
        <path d="M12 1v6m0 6v6m5.196-15.804L13.804 6.804m-3.608 6.392-3.392 3.392m9.192-9.192-3.392 3.392m-3.608 6.392-3.392 3.392M1 12h6m6 0h6" />
      </svg>
    )
  },
  {
    label: 'Contact',
    href: '#',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
      </svg>
    )
  }
];

export function HeaderMenu({ className }: HeaderMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleToggle = () => {
    setIsOpen(!isOpen);
  };

  const handleItemClick = () => {
    setIsOpen(false);
  };

  return (
    <div className={`${styles.menuContainer} ${className || ''}`} ref={menuRef}>
      <button
        onClick={handleToggle}
        className={styles.menuButton}
        title="Menu"
        aria-label="Open menu"
        aria-expanded={isOpen}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>

      {isOpen && (
        <div className={styles.dropdown}>
          <ul className={styles.menuList}>
            {defaultMenuItems.map((item, index) => (
              <li key={index}>
                <a
                  href={item.href}
                  className={styles.menuItem}
                  onClick={handleItemClick}
                >
                  {item.icon && <span className={styles.menuIcon}>{item.icon}</span>}
                  <span className={styles.menuLabel}>{item.label}</span>
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
