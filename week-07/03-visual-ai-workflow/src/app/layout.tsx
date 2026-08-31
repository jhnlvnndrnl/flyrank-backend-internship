import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Visual AI Workflow Studio | FlyRank",
  description: "Interactive visual AI decision tree workflow orchestrator powered by React Flow and Inngest.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-slate-950 text-slate-100 antialiased">
        {children}
      </body>
    </html>
  );
}
