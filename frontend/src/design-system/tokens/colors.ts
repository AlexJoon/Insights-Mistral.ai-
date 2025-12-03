/**
 * Color tokens - Brand and semantic colors
 * Modular color system following Open Climate Curriculum brand
 */

export const brandColors = {
  // Primary brand colors
  primary: {
    50: '#e0f9f4',
    100: '#b3f0e6',
    200: '#80e6d7',
    300: '#4ddcc8',
    400: '#26d4bd',
    500: '#00d4aa',  // Main brand color
    600: '#00c09a',
    700: '#00a687',
    800: '#008d74',
    900: '#006354',
  },

  // Secondary - Sky blue accents
  secondary: {
    50: '#f0f9ff',
    100: '#e0f2fe',
    200: '#bae6fd',
    300: '#7dd3fc',
    400: '#38bdf8',
    500: '#0ea5e9',
    600: '#0284c7',
    700: '#0369a1',
    800: '#075985',
    900: '#0c4a6e',
  },

  // Neutral - Dark slate for backgrounds
  neutral: {
    50: '#f8fafc',
    100: '#f1f5f9',
    200: '#e2e8f0',
    300: '#cbd5e1',
    400: '#94a3b8',
    500: '#64748b',
    600: '#475569',
    700: '#334155',
    800: '#1e293b',
    900: '#0f172a',
    950: '#020617',
  },
} as const;

export const semanticColors = {
  light: {
    background: {
      primary: brandColors.neutral[50],
      secondary: brandColors.neutral[100],
      tertiary: '#ffffff',
      elevated: '#ffffff',
    },
    surface: {
      default: '#ffffff',
      hover: brandColors.neutral[100],
      active: brandColors.neutral[200],
      disabled: brandColors.neutral[200],
    },
    text: {
      primary: brandColors.neutral[900],
      secondary: brandColors.neutral[600],
      tertiary: brandColors.neutral[500],
      disabled: brandColors.neutral[400],
      inverse: '#ffffff',
    },
    border: {
      default: brandColors.neutral[200],
      hover: brandColors.neutral[300],
      focus: brandColors.primary[500],
      disabled: brandColors.neutral[200],
    },
    interactive: {
      primary: brandColors.primary[500],
      primaryHover: brandColors.primary[600],
      primaryActive: brandColors.primary[700],
      secondary: brandColors.secondary[500],
      secondaryHover: brandColors.secondary[600],
    },
  },

  dark: {
    background: {
      primary: brandColors.neutral[950],
      secondary: brandColors.neutral[900],
      tertiary: brandColors.neutral[800],
      elevated: brandColors.neutral[800],
    },
    surface: {
      default: brandColors.neutral[800],
      hover: brandColors.neutral[700],
      active: brandColors.neutral[600],
      disabled: brandColors.neutral[800],
    },
    text: {
      primary: brandColors.neutral[50],
      secondary: brandColors.neutral[300],
      tertiary: brandColors.neutral[400],
      disabled: brandColors.neutral[500],
      inverse: brandColors.neutral[900],
    },
    border: {
      default: brandColors.neutral[700],
      hover: brandColors.neutral[600],
      focus: brandColors.primary[500],
      disabled: brandColors.neutral[800],
    },
    interactive: {
      primary: brandColors.primary[500],
      primaryHover: brandColors.primary[400],
      primaryActive: brandColors.primary[300],
      secondary: brandColors.secondary[500],
      secondaryHover: brandColors.secondary[400],
    },
  },
} as const;

export const statusColors = {
  success: {
    light: '#10b981',
    dark: '#34d399',
  },
  warning: {
    light: '#f59e0b',
    dark: '#fbbf24',
  },
  error: {
    light: '#ef4444',
    dark: '#f87171',
  },
  info: {
    light: brandColors.secondary[500],
    dark: brandColors.secondary[400],
  },
} as const;

export type ColorMode = 'light' | 'dark';
export type BrandColor = keyof typeof brandColors;
export type SemanticColorCategory = keyof typeof semanticColors.light;
