/**
 * ApiStatus Component
 * Displays API connection status with green/red indicator
 */
'use client';

import { useEffect, useState } from 'react';
import styles from './ApiStatus.module.css';

export interface ApiStatusProps {
  className?: string;
  iconClassName?: string;
  labelClassName?: string;
}

export function ApiStatus({
  className,
  iconClassName,
  labelClassName
}: ApiStatusProps) {
  const [isOnline, setIsOnline] = useState(true);
  const [isChecking, setIsChecking] = useState(false);

  const checkApiStatus = async () => {
    try {
      setIsChecking(true);
      const response = await fetch('http://localhost:8000/health', {
        method: 'GET',
        signal: AbortSignal.timeout(5000), // 5 second timeout
      });
      setIsOnline(response.ok);
    } catch (error) {
      setIsOnline(false);
    } finally {
      setIsChecking(false);
    }
  };

  useEffect(() => {
    // Check immediately on mount
    checkApiStatus();

    // Check every 30 seconds
    const interval = setInterval(checkApiStatus, 30000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div
      className={`${styles.statusContainer} ${className || ''}`}
      title={isOnline ? 'API Online' : 'API Offline'}
    >
      <div className={iconClassName}>
        <div className={`${styles.statusDot} ${isOnline ? styles.online : styles.offline} ${isChecking ? styles.checking : ''}`} />
      </div>
      <span className={labelClassName}>Zeta 1.0</span>
    </div>
  );
}
