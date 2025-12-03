/**
 * Theme Context - Color mode management
 * Separate context for theme state management
 */
'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { ColorMode } from '../tokens';

interface ThemeContextValue {
  mode: ColorMode;
  setMode: (mode: ColorMode) => void;
  toggleMode: () => void;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
  defaultMode?: ColorMode;
  storageKey?: string;
}

export function ThemeProvider({
  children,
  defaultMode = 'dark',
  storageKey = 'insights-theme-mode',
}: ThemeProviderProps) {
  const [mode, setModeState] = useState<ColorMode>(defaultMode);
  const [mounted, setMounted] = useState(false);

  // Hydrate from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(storageKey) as ColorMode | null;
    if (stored && (stored === 'light' || stored === 'dark')) {
      setModeState(stored);
    }
    setMounted(true);
  }, [storageKey]);

  // Update localStorage and document when mode changes
  useEffect(() => {
    if (!mounted) return;

    localStorage.setItem(storageKey, mode);
    document.documentElement.classList.remove('light', 'dark');
    document.documentElement.classList.add(mode);
    document.documentElement.setAttribute('data-theme', mode);
  }, [mode, mounted, storageKey]);

  const setMode = (newMode: ColorMode) => {
    setModeState(newMode);
  };

  const toggleMode = () => {
    setModeState(prev => prev === 'light' ? 'dark' : 'light');
  };

  // Prevent flash of unstyled content
  if (!mounted) {
    return null;
  }

  return (
    <ThemeContext.Provider value={{ mode, setMode, toggleMode }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
