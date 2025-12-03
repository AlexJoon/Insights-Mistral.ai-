/**
 * Providers - Client-side provider wrapper
 * Separates client providers from server layout
 */
'use client';

import { ReactNode } from 'react';
import { ThemeProvider } from '@/design-system/theme';

interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return (
    <ThemeProvider defaultMode="dark">
      {children}
    </ThemeProvider>
  );
}
