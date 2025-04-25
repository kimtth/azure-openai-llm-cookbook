import { createContext, useContext, useEffect, useState } from "react"

type Theme = "dark" | "light" | "system"

type ThemeProviderProps = {
  children: React.ReactNode
  defaultTheme?: Theme
  storageKey?: string
}

type ThemeContextType = {
  theme: Theme
  setTheme: (theme: Theme) => void
}

type ThemeProviderState = {
  theme: Theme
  setTheme: (theme: Theme) => void
}

const initialState: ThemeProviderState = {
  theme: "system",
  setTheme: () => null
}

const ThemeContext = createContext<ThemeContextType>(initialState)

const applyThemeToDOM = (resolvedTheme: "dark" | "light") => {
  const root = window.document.documentElement
  
  // Remove all theme classes and add new one
  root.classList.remove("light", "dark")
  root.classList.add(resolvedTheme)
  
  // Set data-theme attributes consistently
  const elements = [root, document.body, ...document.querySelectorAll("[data-theme]")]
  elements.forEach(el => {
    el.setAttribute("data-theme", resolvedTheme)
    if (el instanceof HTMLElement) {
      el.style.colorScheme = resolvedTheme
    }
  })
  
  // Update meta theme color
  const themeColor = resolvedTheme === "dark" ? "#020817" : "#ffffff"
  let metaThemeColor = document.querySelector('meta[name="theme-color"]')
  if (!metaThemeColor) {
    metaThemeColor = document.createElement("meta")
    metaThemeColor.setAttribute("name", "theme-color")
    document.head.appendChild(metaThemeColor)
  }
  metaThemeColor.setAttribute("content", themeColor)
  
  // Force re-render and notify components
  window.dispatchEvent(new Event('storage'))
  window.dispatchEvent(new CustomEvent('themechange', { detail: { theme: resolvedTheme } }))

  const colors = {
    "--background": resolvedTheme === "dark" ? "hsl(222.2 84% 4.9%)" : "hsl(0 0% 100%)",
    "--foreground": resolvedTheme === "dark" ? "hsl(210 40% 98%)" : "hsl(222.2 84% 4.9%)",
    "--card": resolvedTheme === "dark" ? "hsl(222.2 84% 4.9%)" : "hsl(0 0% 100%)",
    "--card-foreground": resolvedTheme === "dark" ? "hsl(210 40% 98%)" : "hsl(222.2 84% 4.9%)",
    "--popover": resolvedTheme === "dark" ? "hsl(222.2 84% 4.9%)" : "hsl(0 0% 100%)",
    "--popover-foreground": resolvedTheme === "dark" ? "hsl(210 40% 98%)" : "hsl(222.2 84% 4.9%)",
    "--primary": resolvedTheme === "dark" ? "hsl(217.2 91.2% 59.8%)" : "hsl(221.2 83.2% 53.3%)",
    "--primary-foreground": resolvedTheme === "dark" ? "hsl(222.2 47.4% 11.2%)" : "hsl(210 40% 98%)",
    "--secondary": resolvedTheme === "dark" ? "hsl(217.2 32.6% 17.5%)" : "hsl(210 40% 96.1%)",
    "--secondary-foreground": resolvedTheme === "dark" ? "hsl(210 40% 98%)" : "hsl(222.2 47.4% 11.2%)",
    "--muted": resolvedTheme === "dark" ? "hsl(217.2 32.6% 17.5%)" : "hsl(210 40% 96.1%)",
    "--muted-foreground": resolvedTheme === "dark" ? "hsl(215 20.2% 65.1%)" : "hsl(215.4 16.3% 46.9%)",
    "--accent": resolvedTheme === "dark" ? "hsl(217.2 32.6% 17.5%)" : "hsl(210 40% 96.1%)",
    "--accent-foreground": resolvedTheme === "dark" ? "hsl(210 40% 98%)" : "hsl(222.2 47.4% 11.2%)",
    "--destructive": resolvedTheme === "dark" ? "hsl(0 62.8% 30.6%)" : "hsl(0 84.2% 60.2%)",
    "--destructive-foreground": resolvedTheme === "dark" ? "hsl(210 40% 98%)" : "hsl(210 40% 98%)",
    "--border": resolvedTheme === "dark" ? "hsl(217.2 32.6% 17.5%)" : "hsl(214.3 31.8% 91.4%)",
    "--input": resolvedTheme === "dark" ? "hsl(217.2 32.6% 17.5%)" : "hsl(214.3 31.8% 91.4%)",
    "--ring": resolvedTheme === "dark" ? "hsl(224.3 76.3% 48%)" : "hsl(221.2 83.2% 53.3%)",
  }

  Object.entries(colors).forEach(([property, value]) => {
    document.documentElement.style.setProperty(property, value)
  })

  window.dispatchEvent(
    new CustomEvent("themechange", { detail: { theme: resolvedTheme } })
  )
}

export function ThemeProvider({
  children,
  defaultTheme = "system",
  storageKey = "vite-ui-theme",
}: ThemeProviderProps) {
  const [theme, setTheme] = useState<Theme>(() => {
    if (typeof window === "undefined") return defaultTheme
    return (localStorage.getItem(storageKey) as Theme) || defaultTheme
  })

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)")
    
    const resolveTheme = (theme: Theme): "dark" | "light" => {
      if (theme === "system") {
        return mediaQuery.matches ? "dark" : "light"
      }
      return theme
    }

    const updateTheme = () => {
      const resolvedTheme = resolveTheme(theme)
      applyThemeToDOM(resolvedTheme)
      try {
        localStorage.setItem(storageKey, theme)
      } catch (e) {
        console.warn("Failed to save theme preference:", e)
      }
    }

    updateTheme()

    const handleMediaChange = () => {
      if (theme === "system") {
        updateTheme()
      }
    }

    mediaQuery.addEventListener("change", handleMediaChange)
    return () => mediaQuery.removeEventListener("change", handleMediaChange)
  }, [theme, storageKey])

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider")
  }
  return context
}
