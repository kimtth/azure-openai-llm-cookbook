import * as React from "react"
import { Navbar } from "./navbar"

interface MainLayoutProps {
  children: React.ReactNode
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-background text-foreground antialiased transition-colors duration-200">
      <Navbar />
      <main className="container mx-auto px-4 py-8 transition-colors duration-200">
        {children}
      </main>
    </div>
  )
}
