import type { Metadata } from "next";
import { Geist_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "@/lib/providers";
import { AuthGuard } from "@/components/AuthGuard";

const geistMono = Geist_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "mem8 | Terminal Memory Interface",
  description: "Terminal-style memory management for the orchestr8 ecosystem",
  icons: {
    icon: '/favicon.ico',
    apple: '/apple-touch-icon.png',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistMono.variable} bg-grid bg-scanlines`}
      >
        <Providers>
          <AuthGuard>
            <div className="min-h-screen flex flex-col">
              {children}
            </div>
          </AuthGuard>
        </Providers>
      </body>
    </html>
  );
}
