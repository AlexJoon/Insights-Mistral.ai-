/**
 * Conversation Page - URL-based conversation routing
 * Loads specific conversation by ID from URL
 */
'use client';

import { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useChatStore } from '@/store/chat-store';
import { conversationPersistence } from '@/services/conversation-persistence';
import HomePage from '@/app/page';

export default function ConversationPage() {
  const params = useParams();
  const router = useRouter();
  const { setCurrentConversation } = useChatStore();
  const conversationId = params.conversationId as string;

  useEffect(() => {
    const loadConversation = async () => {
      if (conversationId) {
        const conversation = await conversationPersistence.load(conversationId);

        if (conversation) {
          setCurrentConversation(conversation);
        } else {
          // Conversation not found, redirect to home
          router.push('/');
        }
      }
    };

    loadConversation();
  }, [conversationId, setCurrentConversation, router]);

  return <HomePage />;
}
