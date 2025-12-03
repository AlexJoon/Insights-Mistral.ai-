/**
 * Typography tokens - Type scale and font settings
 * Clean, readable typography for enterprise feel
 */

export const fontFamilies = {
  sans: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  mono: '"SF Mono", "Monaco", "Inconsolata", "Fira Code", "Droid Sans Mono", monospace',
} as const;

export const fontSizes = {
  xs: '0.75rem',      // 12px
  sm: '0.875rem',     // 14px
  base: '1rem',       // 16px
  lg: '1.125rem',     // 18px
  xl: '1.25rem',      // 20px
  '2xl': '1.5rem',    // 24px
  '3xl': '1.875rem',  // 30px
  '4xl': '2.25rem',   // 36px
  '5xl': '3rem',      // 48px
  '6xl': '3.75rem',   // 60px
} as const;

export const fontWeights = {
  normal: 400,
  medium: 500,
  semibold: 600,
  bold: 700,
} as const;

export const lineHeights = {
  none: 1,
  tight: 1.25,
  snug: 1.375,
  normal: 1.5,
  relaxed: 1.625,
  loose: 2,
} as const;

export const textStyles = {
  display: {
    fontSize: fontSizes['5xl'],
    fontWeight: fontWeights.bold,
    lineHeight: lineHeights.tight,
  },
  h1: {
    fontSize: fontSizes['4xl'],
    fontWeight: fontWeights.bold,
    lineHeight: lineHeights.tight,
  },
  h2: {
    fontSize: fontSizes['3xl'],
    fontWeight: fontWeights.semibold,
    lineHeight: lineHeights.snug,
  },
  h3: {
    fontSize: fontSizes['2xl'],
    fontWeight: fontWeights.semibold,
    lineHeight: lineHeights.snug,
  },
  h4: {
    fontSize: fontSizes.xl,
    fontWeight: fontWeights.semibold,
    lineHeight: lineHeights.normal,
  },
  body: {
    fontSize: fontSizes.base,
    fontWeight: fontWeights.normal,
    lineHeight: lineHeights.relaxed,
  },
  bodySmall: {
    fontSize: fontSizes.sm,
    fontWeight: fontWeights.normal,
    lineHeight: lineHeights.normal,
  },
  caption: {
    fontSize: fontSizes.xs,
    fontWeight: fontWeights.normal,
    lineHeight: lineHeights.normal,
  },
  button: {
    fontSize: fontSizes.sm,
    fontWeight: fontWeights.medium,
    lineHeight: lineHeights.none,
  },
} as const;

export type FontSize = keyof typeof fontSizes;
export type TextStyle = keyof typeof textStyles;
