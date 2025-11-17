import type { Metadata } from 'next';
import ClientThemeProvider from '@/components/ClientThemeProvider';
import { AuthProvider } from '@/contexts/AuthContext';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: 'MyAIStorybook - AI-Powered Story Generator',
  description: 'Generate illustrated children\'s stories using AI',
  viewport: 'width=device-width, initial-scale=1, maximum-scale=5',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning>
        <ClientThemeProvider>
          <AuthProvider>
            {children}
          </AuthProvider>
        </ClientThemeProvider>
      </body>
    </html>
  );
}
