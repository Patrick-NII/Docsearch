import type { Metadata, Viewport } from 'next'
import { Geist, Geist_Mono } from "next/font/google";
import './globals.css'
import { AuthProvider } from "../components/AuthContext";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: 'DocSearch AI - Assistant IA pour Documents',
  description: 'Analysez et interrogez vos documents avec l\'intelligence artificielle',
  keywords: ['IA', 'documents', 'analyse', 'recherche', 'GPT'],
  authors: [{ name: 'DocSearch AI Team' }],
  creator: 'DocSearch AI',
  publisher: 'DocSearch AI',
  robots: 'index, follow',
  openGraph: {
    title: 'DocSearch AI - Assistant IA pour Documents',
    description: 'Analysez et interrogez vos documents avec l\'intelligence artificielle',
    type: 'website',
    locale: 'fr_FR',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'DocSearch AI - Assistant IA pour Documents',
    description: 'Analysez et interrogez vos documents avec l\'intelligence artificielle',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#6366f1' },
    { media: '(prefers-color-scheme: dark)', color: '#0a0a0a' }
  ],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
