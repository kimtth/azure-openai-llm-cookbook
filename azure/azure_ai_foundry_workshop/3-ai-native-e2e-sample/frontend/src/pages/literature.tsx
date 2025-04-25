"use client"

import { useState, useRef, useEffect, type FormEvent } from "react"
import { Button } from "../components/ui/button"
import { Input } from "../components/ui/input"
import { SendHorizontal, Mic, MicOff, FileText, MessageSquare } from "lucide-react"
import { literatureApi } from "../lib/api"
import type { ChatMessage, Document } from "../types/api"
import { cn } from "../lib/utils"
import TextareaAutosize from 'react-textarea-autosize'
import { toast, ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "../components/ui/tooltip"
import { motion, AnimatePresence } from "framer-motion"
import ReactMarkdown from "react-markdown"

// If your server occasionally sends weird JSON with single quotes, you can do
// a quick fix here. But ideally, fix on the server side.
function fixSingleQuotes(jsonString: string) {
  return jsonString.replace(/'/g, '"')
}

export function LiteraturePage() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [documents, setDocuments] = useState<Document[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Sample documents to show after response
  const sampleDocuments: Document[] = [
    {
      title: "Deep Learning for Drug Discovery: Opportunities and Challenges",
      relevance: 0.95,
      authors: ["Zhang et al."],
      year: 2023,
      journal: "Nature Reviews Drug Discovery"
    },
    {
      title: "AI-Powered Structure-Based Drug Design: Recent Advances and Future Perspectives",
      relevance: 0.88,
      authors: ["Chen et al."],
      year: 2023,
      journal: "Journal of Medicinal Chemistry"
    },
    {
      title: "Machine Learning Applications in Drug Development Pipeline",
      relevance: 0.82,
      authors: ["Smith et al."],
      year: 2022,
      journal: "Drug Discovery Today"
    },
    {
      title: "Artificial Intelligence in Target Identification and Validation",
      relevance: 0.78,
      authors: ["Johnson et al."],
      year: 2023,
      journal: "Nature Biotechnology"
    }
  ]

  useEffect(() => {
    // Scroll to bottom when messages change
    if (messages.length > 0) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder

      const audioChunks: BlobPart[] = []
      mediaRecorder.addEventListener("dataavailable", (event) => {
        audioChunks.push(event.data)
      })

      mediaRecorder.addEventListener("stop", () => {
        // TODO: Implement voice-to-text conversion with audioChunks
        setInput("Sample transcribed text from voice input")
        stream.getTracks().forEach((track) => track.stop())
      })

      mediaRecorder.start()
      setIsRecording(true)
    } catch (error) {
      console.error("Error accessing microphone:", error)
      setError("Failed to access microphone")
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    setLoading(true)
    setError(null)
    // Clear documents when starting a new query
    setDocuments([])

    try {
      const stream = await literatureApi.chat(input)
      if (!stream) throw new Error("No response stream")

      // Show sample documents after getting a response
      setDocuments(sampleDocuments)

      const reader = stream.getReader()
      const decoder = new TextDecoder()

      let partialContent = ""

      // Add user's message
      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        role: "user",
        content: input,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, userMessage])
      setInput("")

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const text = decoder.decode(value)
        const lines = text.split("\n")

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6).trim()
            if (!data) continue

            try {
              const parsed = JSON.parse(data)
              console.log("Received SSE event:", parsed)

              if (parsed.done) {
                // End of stream
                break
              }

              switch (parsed.type) {
                case "error":
                  throw new Error(parsed.content)

                case "delta": {
                  // Streaming partial text
                  partialContent += parsed.content
                  setMessages((prev) => {
                    const lastMsg = prev[prev.length - 1]
                    if (lastMsg?.role === "assistant") {
                      // Update the existing assistant message
                      return [
                        ...prev.slice(0, -1),
                        { ...lastMsg, content: partialContent },
                      ]
                    } else {
                      // Create a new assistant message
                      return [
                        ...prev,
                        {
                          id: `assistant-${Date.now()}`,
                          role: "assistant",
                          content: partialContent,
                          timestamp: new Date().toISOString(),
                        },
                      ]
                    }
                  })
                  break
                }

                case "message": {
                  // This is the final consolidated message in (often) JSON form
                  let finalText = parsed.content
                  try {
                    // If your server uses single quotes, fix them:
                    const fixed = fixSingleQuotes(finalText)
                    const blocks = JSON.parse(fixed)
                    if (Array.isArray(blocks)) {
                      // Join all text blocks
                      finalText = blocks
                        .map((b) => b.text?.value || "")
                        .join("\n\n")
                    }
                  } catch (err) {
                    console.error("Failed to parse final message JSON:", err)
                  }

                  partialContent = finalText
                  setMessages((prev) => {
                    const lastMsg = prev[prev.length - 1]
                    if (lastMsg?.role === "assistant") {
                      return [
                        ...prev.slice(0, -1),
                        { ...lastMsg, content: finalText },
                      ]
                    }
                    return [
                      ...prev,
                      {
                        id: `assistant-${Date.now()}`,
                        role: "assistant",
                        content: finalText,
                        timestamp: new Date().toISOString(),
                      },
                    ]
                  })
                  break
                }

                case "documents": {
                  // SSE for relevant docs
                  setDocuments(parsed.data)
                  break
                }
              }
            } catch (err) {
              console.error("Error parsing SSE data:", err, "Raw data:", data)
            }
          }
        }
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to chat with literature agent"
      setError(errorMessage)
      toast.error(errorMessage)
      console.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <ToastContainer />
      {/* Sticky header */}
      <header className="sticky top-0 z-50 border-b bg-white/50 backdrop-blur-sm dark:bg-gray-900/50">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <MessageSquare className="w-6 h-6 text-primary" />
            <h1 className="text-xl font-semibold">Literature Answer Engine</h1>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="container mx-auto px-4 py-6 flex gap-6 flex-1">
        {/* Chat section */}
        <div className="flex flex-col w-full max-w-3xl bg-white dark:bg-gray-900 rounded-xl shadow-sm">
          {/* Message list */}
          <div className="p-4 space-y-4 overflow-y-auto" style={{ maxHeight: "60vh" }}>
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center space-y-4 p-8">
                <div className="p-6 backdrop-blur-sm bg-white/30 dark:bg-gray-800/30 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
                  <h2 className="text-xl font-semibold mb-2 text-center">
                    RAG-Powered Literature Assistant
                  </h2>
                  <p className="text-sm text-muted-foreground text-center max-w-md">
                    This is a Retrieval-Augmented Generation (RAG) agent powered by Azure AI
                    Agent Service. It can help you find and understand scientific literature
                    by searching a curated collection of research papers and providing
                    evidence-based responses.
                  </p>
                </div>
              </div>
            )}

            <AnimatePresence initial={false}>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.2 }}
                  className={cn(
                    "flex w-max max-w-[75%] flex-col gap-2 rounded-lg px-3 py-2 text-sm",
                    message.role === "user"
                      ? "ml-auto bg-primary text-primary-foreground"
                      : "bg-muted"
                  )}
                >
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        {/* Use `react-markdown` + Tailwind typography classes */}
                        <div className="cursor-help prose dark:prose-invert max-w-none">
                          <ReactMarkdown>{message.content}</ReactMarkdown>
                        </div>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p className="max-w-xs break-all font-mono text-xs">
                          {message.content}
                        </p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </motion.div>
              ))}
            </AnimatePresence>

            {/* Loading indicator */}
            {loading && (
              <div className="chat-message flex justify-start">
                <div className="bg-muted p-3 rounded-xl rounded-tl-none">
                  <div className="typing-indicator flex space-x-1">
                    <span>•</span>
                    <span>•</span>
                    <span>•</span>
                  </div>
                </div>
              </div>
            )}

            {/* Always scroll to bottom */}
            <div ref={messagesEndRef} />
          </div>

          {/* Input bar */}
          <div className="p-4 border-t dark:border-gray-800">
            <form onSubmit={handleSubmit} className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => (isRecording ? stopRecording() : startRecording())}
                className={cn(
                  "p-2 rounded-full transition-colors",
                  isRecording
                    ? "bg-red-100 text-red-600 dark:bg-red-900/30"
                    : "hover:bg-gray-100 dark:hover:bg-gray-800"
                )}
              >
                {isRecording ? (
                  <MicOff className="w-5 h-5" />
                ) : (
                  <Mic className="w-5 h-5" />
                )}
              </button>
              <TextareaAutosize
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    handleSubmit(e)
                  }
                }}
                placeholder="Ask about research literature..."
                disabled={loading || isRecording}
                className="flex-1 resize-none p-2 border rounded-md"
              />
              <Button
                type="submit"
                disabled={loading || !input.trim() || isRecording}
              >
                {loading ? (
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                ) : (
                  <SendHorizontal className="w-4 h-4" />
                )}
              </Button>
            </form>
          </div>
        </div>

        {/* Referenced Documents panel */}
        <div className="hidden md:block w-64">
          <div className="bg-white dark:bg-gray-900 border dark:border-gray-800 rounded-xl shadow-sm p-3 space-y-2">
            <h2 className="text-sm font-semibold flex items-center gap-2 mb-2">
              <FileText className="w-4 h-4" />
              Referenced Documents
            </h2>
            {documents.map((doc, index) => (
              <div
                key={index}
                className="p-2 bg-white dark:bg-gray-900 rounded-lg shadow-sm border dark:border-gray-800"
              >
                <h3 className="text-sm font-medium leading-tight">{doc.title}</h3>
                <p className="text-xs text-gray-500 mt-0.5">
                  {doc.authors?.join(", ")} • {doc.journal} • {doc.year}
                </p>
                <div className="mt-1.5 h-0.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all duration-500"
                    style={{ width: `${doc.relevance * 100}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-0.5">
                  {Math.round(doc.relevance * 100)}% relevance
                </p>
              </div>
            ))}
            {documents.length === 0 && (
              <p className="text-xs text-muted-foreground">No references yet...</p>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
