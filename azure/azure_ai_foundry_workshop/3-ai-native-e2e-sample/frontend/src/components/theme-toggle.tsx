
// Remove unused import
import { Button } from "./ui/button"
import { MoonIcon, SunIcon } from "lucide-react"
import { useTheme } from "./theme-provider"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  
  const toggleTheme = () => {
    const newTheme = theme === "dark" ? "light" : "dark"
    setTheme(newTheme)
  }
  
  return (
    <Button
      variant="outline"
      size="icon"
      onClick={toggleTheme}
      className="transition-colors duration-200 hover:bg-accent hover:text-accent-foreground"
      title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
      data-appid="theme-toggle"
    >
      <span className="sr-only">Toggle theme</span>
      {theme === "dark" ? (
        <SunIcon className="h-5 w-5 text-yellow-500 hover:text-yellow-400 transition-all duration-200" />
      ) : (
        <MoonIcon className="h-5 w-5 text-slate-700 hover:text-slate-900 transition-all duration-200" />
      )}
    </Button>
  )
}
