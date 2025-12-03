/**
 * useConversationRouter Hook
 * Handles URL navigation for conversations
 */

import { useCallback } from 'react';
import { useRouter } from 'next/navigation';

export function useConversationRouter() {
  const router = useRouter();

  const navigateToConversation = useCallback((conversationId: string) => {
    router.push(`/chat/${conversationId}`);
  }, [router]);

  const navigateToHome = useCallback(() => {
    router.push('/');
  }, [router]);

  return {
    navigateToConversation,
    navigateToHome,
  };
}
