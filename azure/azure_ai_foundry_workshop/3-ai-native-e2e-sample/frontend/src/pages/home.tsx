import { Link } from "react-router-dom"
import { Button } from "../components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card"
import { Pill, LineChart, MessageSquare, ClipboardCheck } from "lucide-react"

// Framer Motion
import { motion, AnimatePresence } from "framer-motion"

export function HomePage() {
  // We can animate each tile individually
  const tiles = [
    {
      to: "/medication",
      icon: <Pill className="h-5 w-5" />,
      title: "Smart Medication Insights",
      desc: `This is about showcasing how you can build deep research using your company’s proprietary tools and data sources using AI Agent Service. 🧪 
        It uses AI Agent Service, Azure Functions, Grounding with Bing, Logic Apps, and Azure AI Search to generate a deeply researched report.`,
      buttonText: "Deep Research on your data",
      buttonIcon: <Pill className="h-4 w-4" />,
    },
    {
      to: "/trials",
      icon: <LineChart className="h-5 w-5" />,
      title: "Clinical Trials",
      desc: `This is about event-driven ambient agents. It showcases a multi-agent pattern where an orchestrator divides a task (triggered by an event) to other agents and then aggregates their analyses. 🤖 
        All built with AI Agent Service multi-agent patterns and tools.`,
      buttonText: "Event-driven Multi-Agent orchestration",
      buttonIcon: <LineChart className="h-4 w-4" />,
    },
    {
      to: "/literature",
      icon: <MessageSquare className="h-5 w-5" />,
      title: "Literature Chat",
      desc: `An Agent RAG demonstration showcasing AI Agent Service integration with AI Search to respond in a coherent way. 📚`,
      buttonText: "Agent RaG with AI Agent Service",
      buttonIcon: <MessageSquare className="h-4 w-4" />,
    },
    {
      to: "/patient",
      icon: <ClipboardCheck className="h-5 w-5" />,
      title: "Clinical Trial Eligibility",
      desc: `An example with Code Interpreter and Logic Apps used to determine if a clinical trial matches a patient's info. 🩺`,
      buttonText: "Deterministic workflows and accurate responses",
      buttonIcon: <ClipboardCheck className="h-4 w-4" />,
    },
  ]

  return (
    <div className="space-y-8">
      {/* Centered main copy */}
      <div className="text-center space-y-4 max-w-4xl mx-auto">
        <h2 className="text-4xl font-bold">AI Agent Showcase: Intelligent Workflows in Action</h2>
        <p className="text-muted-foreground text-base sm:text-lg">
          This is an art-of-the-possible sample app demonstrating Azure AI Foundry
          and Azure AI Agent Service capabilities. It showcases different design
          patterns and integrations that can be built using AI Agent Service to drive automation, personalization, decision-making, and intelligent research.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-2 max-w-5xl mx-auto">
        <AnimatePresence>
          {tiles.map((tile, index) => (
            <motion.div
              key={tile.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
            >
              <Link to={tile.to}>
                <Card className="hover:bg-muted/50 transition-colors h-full flex flex-col">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      {tile.icon}
                      {tile.title}
                    </CardTitle>
                    <CardDescription>
                      {tile.desc}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="mt-auto">
                    <Button
                      variant="outline"
                      className="w-full py-3 flex items-center justify-center gap-2 border-2"
                    >
                      {tile.buttonIcon}
                      {tile.buttonText}
                    </Button>
                  </CardContent>
                </Card>
              </Link>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  )
}
