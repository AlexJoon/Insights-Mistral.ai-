/**
 * Root layout component.
 * Defines the HTML structure and global styles.
 */

import type { Metadata } from 'next';
import { Be_Vietnam_Pro } from 'next/font/google';
import { Providers } from '@/components/providers/Providers';
import '../styles/globals.css';

const beVietnamPro = Be_Vietnam_Pro({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700'],
  variable: '--font-be-vietnam-pro',
});

export const metadata: Metadata = {
  title: 'Insights - AI Research Assistant',
  description: 'A modular chat application powered by Mistral AI with enterprise design',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={beVietnamPro.className}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
