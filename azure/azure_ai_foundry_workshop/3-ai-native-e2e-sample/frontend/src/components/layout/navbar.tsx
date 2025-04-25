// Remove unused import
import { Link, useLocation } from "react-router-dom"
import { Button } from "../ui/button"
import { useTheme } from "../theme-provider"
import {
  Sun,
  Moon,
  Pill,
  LineChart,
  MessageSquare,
  Users,
  Brain,
} from "lucide-react"

const navigation = [
  { id: 'medication', name: 'Medications', href: '/medication', icon: Pill },
  { id: 'trials', name: 'Trials', href: '/trials', icon: LineChart },
  { id: 'literature', name: 'Literature', href: '/literature', icon: MessageSquare },
  { id: 'patient', name: 'Patient', href: '/patient', icon: Users },
]

export function Navbar() {
  const { theme, setTheme } = useTheme()
  const { pathname } = useLocation()

  return (
    <nav className="border-b bg-background">
      <div className="container mx-auto px-2 sm:px-4">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2 text-foreground hover:text-foreground/80">
              <Brain className="h-6 w-6" />
              <span className="text-lg font-semibold truncate max-w-[120px] md:max-w-none">AI Native Sample App</span>
            </Link>
          </div>

          <div className="flex items-center gap-1 md:gap-3 overflow-x-auto">
            {navigation.map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  data-appid={item.id}
                  className={`flex items-center justify-center p-2 md:px-3 md:py-2 rounded-md text-sm font-medium transition-colors ${
                    pathname === item.href
                      ? 'bg-secondary text-secondary-foreground'
                      : 'hover:bg-accent hover:text-accent-foreground'
                  }`}
                >
                  <Icon className="h-5 w-5 md:h-4 md:w-4" />
                  <span className="hidden md:inline md:ml-1">{item.name}</span>
                </Link>
              )
            })}

            <Button
              variant="ghost"
              size="icon"
              data-appid="0"
              className="theme-toggle"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            >
              {theme === 'dark' ? (
                <Sun className="h-5 w-5 text-yellow-500" />
              ) : (
                <Moon className="h-5 w-5 text-slate-700" />
              )}
            </Button>
          </div>
        </div>
      </div>
    </nav>
  )
}
