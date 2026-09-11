import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SmartEval AI – Intelligent Examination Paper Evaluation",
  description: "AI-powered automated descriptive exam evaluation and learning analytics system",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased dark">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
