import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'Groww Lens — Your Market Memory',
  description:
    'A smart market watchlist that remembers what you last saw, identifies meaningful market changes while you were away, ranks those changes by impact, and explains why they matter.',
  keywords: ['stock market', 'watchlist', 'market intelligence', 'India stocks', 'NSE', 'BSE'],
  openGraph: {
    title: 'Groww Lens — Your Market Memory',
    description: 'Transform your passive watchlist into a personalized market intelligence feed.',
    type: 'website',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans antialiased bg-[#0a0a0f] text-white`}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
