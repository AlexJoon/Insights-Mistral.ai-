/**
 * Transition tokens - Animation timing and easing
 * Smooth, purposeful motion
 */

export const transitions = {
  duration: {
    instant: '0ms',
    fast: '150ms',
    base: '200ms',
    slow: '300ms',
    slower: '500ms',
  },
  easing: {
    linear: 'linear',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
  },
} as const;

export const transitionPresets = {
  fade: `opacity ${transitions.duration.base} ${transitions.easing.easeInOut}`,
  slide: `transform ${transitions.duration.base} ${transitions.easing.easeOut}`,
  scale: `transform ${transitions.duration.fast} ${transitions.easing.easeOut}`,
  color: `background-color ${transitions.duration.base} ${transitions.easing.easeInOut}, color ${transitions.duration.base} ${transitions.easing.easeInOut}`,
  all: `all ${transitions.duration.base} ${transitions.easing.easeInOut}`,
} as const;

export type TransitionPreset = keyof typeof transitionPresets;
