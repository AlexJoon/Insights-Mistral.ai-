/**
 * useSearchMode Hook
 * Manages search mode state with localStorage persistence
 *
 * Design Pattern: Custom Hook Pattern
 * Purpose: Encapsulate search mode logic and persistence
 */
'use client';

import { useState, useEffect } from 'react';
import type { SearchMode } from '@/components/ui/SearchModeToggle';

const STORAGE_KEY = 'insights_search_mode';
const DEFAULT_MODE: SearchMode = 'rag';

export function useSearchMode() {
  const [searchMode, setSearchMode] = useState<SearchMode>(DEFAULT_MODE);
  const [isInitialized, setIsInitialized] = useState(false);

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored === 'rag' || stored === 'web') {
        setSearchMode(stored);
      }
    } catch (error) {
      console.error('Failed to load search mode from localStorage:', error);
    } finally {
      setIsInitialized(true);
    }
  }, []);

  // Save to localStorage whenever mode changes
  useEffect(() => {
    if (isInitialized) {
      try {
        localStorage.setItem(STORAGE_KEY, searchMode);
      } catch (error) {
        console.error('Failed to save search mode to localStorage:', error);
      }
    }
  }, [searchMode, isInitialized]);

  const setMode = (mode: SearchMode) => {
    setSearchMode(mode);
  };

  return {
    searchMode,
    setSearchMode: setMode,
    isRAGMode: searchMode === 'rag',
    isWebMode: searchMode === 'web',
  };
}
