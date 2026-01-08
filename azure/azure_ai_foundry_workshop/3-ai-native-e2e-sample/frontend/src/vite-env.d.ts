/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_DEFAULT_THEME: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
