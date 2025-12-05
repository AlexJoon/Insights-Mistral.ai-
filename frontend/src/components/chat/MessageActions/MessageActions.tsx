/**
 * MessageActions Component
 * Modular action buttons for AI messages (copy, export PDF, retry)
 */
import { useState } from 'react';
import styles from './MessageActions.module.css';

export interface MessageActionsProps {
  content: string;
  onRetry?: () => void;
  className?: string;
}

export function MessageActions({ content, onRetry, className }: MessageActionsProps) {
  const [copied, setCopied] = useState(false);
  const [exporting, setExporting] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const handleExportPDF = async () => {
    setExporting(true);
    try {
      // Dynamic import to avoid loading jsPDF unless needed
      const { jsPDF } = await import('jspdf');
      const doc = new jsPDF();

      // Split content into lines that fit the page width
      const pageWidth = doc.internal.pageSize.getWidth();
      const margin = 15;
      const maxWidth = pageWidth - (margin * 2);

      const lines = doc.splitTextToSize(content, maxWidth);

      // Add text to PDF
      doc.setFontSize(11);
      doc.text(lines, margin, margin);

      // Download PDF
      const timestamp = new Date().toISOString().split('T')[0];
      doc.save(`ai-response-${timestamp}.pdf`);
    } catch (error) {
      console.error('Failed to export PDF:', error);
    } finally {
      setExporting(false);
    }
  };

  const handleRetry = () => {
    if (onRetry) {
      onRetry();
    }
  };

  return (
    <div className={`${styles.actions} ${className || ''}`}>
      {/* Copy Button */}
      <button
        onClick={handleCopy}
        className={styles.actionButton}
        title={copied ? 'Copied!' : 'Copy to clipboard'}
        aria-label="Copy to clipboard"
      >
        {copied ? (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="20 6 9 17 4 12" />
          </svg>
        ) : (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
          </svg>
        )}
      </button>

      {/* Export PDF Button */}
      <button
        onClick={handleExportPDF}
        className={styles.actionButton}
        disabled={exporting}
        title="Export to PDF"
        aria-label="Export to PDF"
      >
        {exporting ? (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" opacity="0.25" />
            <path d="M12 2a10 10 0 0 1 10 10" strokeLinecap="round">
              <animateTransform
                attributeName="transform"
                type="rotate"
                from="0 12 12"
                to="360 12 12"
                dur="1s"
                repeatCount="indefinite"
              />
            </path>
          </svg>
        ) : (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="12" y1="18" x2="12" y2="12" />
            <line x1="9" y1="15" x2="12" y2="18" />
            <line x1="15" y1="15" x2="12" y2="18" />
          </svg>
        )}
      </button>

      {/* Retry Button */}
      {onRetry && (
        <button
          onClick={handleRetry}
          className={styles.actionButton}
          title="Regenerate response"
          aria-label="Regenerate response"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
      )}
    </div>
  );
}
