import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "VoxForm AI",
  description: "AI based form filling app.",
};

// Importing a common app layout
import LayoutWrapper from "@/components/LayoutWrapper";


export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <div id="root">
          <LayoutWrapper> {children} </LayoutWrapper>
        </div>
      </body>
    </html>
  );
}
