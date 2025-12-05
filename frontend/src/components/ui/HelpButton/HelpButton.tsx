/**
 * HelpButton - Fixed position help button with mailto link
 * Modular component for support contact
 */
'use client';

import styles from './HelpButton.module.css';

export function HelpButton() {
  const handleClick = () => {
    window.location.href = 'mailto:openclimatecurriculum@gsb.columbia.edu';
  };

  return (
    <button
      className={styles.helpButton}
      onClick={handleClick}
      aria-label="Contact support"
      title="Contact support"
    >
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <circle
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="2"
        />
        <path
          d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3M12 17h.01"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </button>
  );
}
