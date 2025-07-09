import type { Metadata } from 'next'
import { Inter, Poppins, JetBrains_Mono } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '../components/AuthContext'

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const poppins = Poppins({ 
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700', '800'],
  variable: '--font-poppins',
  display: 'swap',
})

const jetbrainsMono = JetBrains_Mono({ 
  subsets: ['latin'],
  variable: '--font-jetbrains-mono',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'DocSearch AI - Assistant IA pour Documents',
  description: 'Plateforme moderne d\'analyse et de recherche dans vos documents avec IA',
  keywords: ['IA', 'documents', 'recherche', 'analyse', 'GPT', 'RAG'],
  authors: [{ name: 'DocSearch AI Team' }],
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#667eea',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr" className={`${inter.variable} ${poppins.variable} ${jetbrainsMono.variable}`}>
      <body className="font-sans antialiased">
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
