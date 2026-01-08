/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_DEFAULT_THEME: string
  readonly VITE_API_VERSION: string
  readonly VITE_AZURE_ENDPOINT: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
