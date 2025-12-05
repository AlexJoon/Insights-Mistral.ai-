/**
 * FileUpload Component
 * Modular file upload button with icon matching MessageActions styling
 */
'use client';

import { useRef, ChangeEvent } from 'react';
import styles from './FileUpload.module.css';

export interface FileUploadProps {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
  acceptedTypes?: string[];
  maxSizeMB?: number;
  className?: string;
}

export function FileUpload({
  onFileSelect,
  disabled = false,
  acceptedTypes = ['.pdf', '.docx', '.txt', '.md'],
  maxSizeMB = 10,
  className
}: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleClick = () => {
    if (!disabled && inputRef.current) {
      inputRef.current.click();
    }
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file size
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      alert(`File size must be less than ${maxSizeMB}MB`);
      return;
    }

    // Validate file type
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!acceptedTypes.includes(fileExtension)) {
      alert(`File type not supported. Accepted types: ${acceptedTypes.join(', ')}`);
      return;
    }

    onFileSelect(file);

    // Reset input to allow selecting the same file again
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  return (
    <>
      <input
        ref={inputRef}
        type="file"
        accept={acceptedTypes.join(',')}
        onChange={handleFileChange}
        className={styles.hiddenInput}
        aria-label="Upload file"
      />

      <button
        onClick={handleClick}
        disabled={disabled}
        className={`${styles.uploadButton} ${className || ''}`}
        title="Upload file (PDF, DOCX, TXT, MD)"
        aria-label="Upload file"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="17 8 12 3 7 8" />
          <line x1="12" y1="3" x2="12" y2="15" />
        </svg>
      </button>
    </>
  );
}
