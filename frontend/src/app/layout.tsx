import type { Metadata } from 'next';
import ClientThemeProvider from '@/components/ClientThemeProvider';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: 'MyAIStorybook - AI-Powered Story Generator',
  description: 'Generate illustrated children\'s stories using AI',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <ClientThemeProvider>
          {children}
        </ClientThemeProvider>
      </body>
    </html>
  );
}
