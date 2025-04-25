import { motion } from "framer-motion"
import { Card, CardContent } from "../ui/card"

export interface AgentCardProps {
  name: string
  role: string
  status: "idle" | "processing" | "complete"
  result?: string
}

export function AgentCard({ name, role, status, result }: AgentCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
    >
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <h4 className="font-medium">{name}</h4>
            <span className={`px-2 py-1 text-xs rounded-full ${
              status === "processing" ? "bg-primary/10 text-primary" :
              status === "complete" ? "bg-success/10 text-success" :
              "bg-muted text-muted-foreground"
            }`}>
              {status}
            </span>
          </div>
          <p className="text-sm text-muted-foreground mt-2">{role}</p>
          {result && (
            <p className="mt-2 text-sm border-t pt-2">{result}</p>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
