import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://activemenubar.app"),
  title: "Menu Bar Spaces — Your Mac Spaces, one click away",
  description:
    "Name, see, and switch between your macOS Desktops directly from the menu bar.",
  keywords: [
    "macOS",
    "Spaces",
    "Mission Control",
    "menu bar",
    "desktop switcher",
  ],
  openGraph: {
    title: "Menu Bar Spaces",
    description: "Your Mac Spaces, one click away.",
    type: "website",
  },
  icons: {
    icon: "/logo.png",
    apple: "/logo.png",
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
