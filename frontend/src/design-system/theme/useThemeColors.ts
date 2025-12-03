/**
 * Theme colors hook - Access semantic colors based on current theme
 * Separate hook for color logic
 */
'use client';

import { useMemo } from 'react';
import { useTheme } from './ThemeContext';
import { semanticColors } from '../tokens';

export function useThemeColors() {
  const { mode } = useTheme();

  const colors = useMemo(() => {
    return semanticColors[mode];
  }, [mode]);

  return colors;
}
