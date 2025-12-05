/**
 * KeyboardShortcuts Component
 * Displays keyboard shortcuts button in sidebar footer
 */
'use client';

import { useState } from 'react';

export interface KeyboardShortcutsProps {
  className?: string;
  iconClassName?: string;
  labelClassName?: string;
}

export function KeyboardShortcuts({
  className,
  iconClassName,
  labelClassName
}: KeyboardShortcutsProps) {
  const [showModal, setShowModal] = useState(false);

  const handleClick = () => {
    setShowModal(true);
    // TODO: Implement keyboard shortcuts modal
    console.log('Keyboard shortcuts modal would open here');
  };

  return (
    <button
      className={className}
      onClick={handleClick}
      title="Keyboard Shortcuts"
    >
      <div className={iconClassName}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <rect x="2" y="4" width="20" height="16" rx="2" />
          <path d="M6 8h.01M10 8h.01M14 8h.01M18 8h.01M8 12h.01M12 12h.01M16 12h.01M7 16h10" />
        </svg>
      </div>
      <span className={labelClassName}>Keyboard Shortcuts</span>
    </button>
  );
}
