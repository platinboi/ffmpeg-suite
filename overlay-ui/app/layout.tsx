import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Text Overlay Editor',
  description: 'Add text overlays to images and videos',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  );
}
