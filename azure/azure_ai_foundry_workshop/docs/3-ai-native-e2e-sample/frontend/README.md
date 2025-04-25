# Drug Development Platform Frontend 🧬

## Overview 🎯
Frontend for the Drug Development Platform, built with Next.js and React. Features a modern UI for molecular analysis, literature search, and clinical trial monitoring.

## Key Features 🌟

- 🔬 **Molecular Analysis**: Interactive 3D molecule viewer using 3Dmol.js
- 📚 **Literature Search**: AI-powered scientific literature analysis
- 📊 **Clinical Trial Analysis**: Data visualization and analysis tools
- 🎨 **Theme Support**: Light/dark mode with next-themes
- 🎯 **Responsive Design**: Mobile-first approach using Tailwind CSS

## Tech Stack 💻

- 🚀 **Next.js**: React framework for production
- 🎨 **Tailwind CSS**: Utility-first CSS framework
- 📊 **Recharts**: Composable charting library
- 🎯 **Radix UI**: Accessible component primitives
- 🔄 **Zustand**: State management
- 🎭 **Lucide**: Beautiful icons
- 🧪 **3Dmol.js**: Molecular visualization

## Getting Started 🚀

1. **Clone and Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Environment Setup**:
   Create a `.env.local` file:
   ```env
   # Backend API URL
   NEXT_PUBLIC_API_URL=http://localhost:8000
   
   # Default theme (light/dark)
   NEXT_PUBLIC_DEFAULT_THEME=dark
   ```

3. **Development Server**:
   ```bash
   npm run dev
   ```
   Visit [http://localhost:3000](http://localhost:3000)

4. **Build for Production**:
   ```bash
   npm run build
   npm run start
   ```

## Project Structure 📁

```
frontend/
├── src/
│   ├── app/                 # Next.js app router
│   ├── components/         
│   │   ├── ui/             # Reusable UI components
│   │   └── molecule-viewer  # 3D molecule visualization
│   ├── lib/
│   │   ├── store/          # Zustand state management
│   │   └── utils/          # Utility functions
│   └── styles/             # Global styles
├── public/                 # Static assets
└── package.json           # Dependencies and scripts
```

## Key Components 🔧

### Molecule Viewer
```typescript
<MoleculeViewer
  smiles="CC1=CC=C(C=C1)NC(=O)C2=CC=C(Cl)C=C2"
  width="100%"
  height="400px"
/>
```

### Literature Search
```typescript
<LiteratureSearch
  onSearch={async (query) => {
    const results = await searchLiterature(query);
    // Handle results...
  }}
/>
```

### Clinical Trial Analysis
```typescript
<TrialAnalysis
  data={trialData}
  onAnalyze={async (data) => {
    const analysis = await analyzeTrialData(data);
    // Handle analysis...
  }}
/>
```

## API Integration 🔌

The frontend communicates with the backend through RESTful endpoints:

```typescript
// Example API call
const searchLiterature = async (query: string) => {
  const response = await fetch(`${API_URL}/agents/literature-search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  });
  return response.json();
};
```

## State Management 🔄

Using Zustand for global state management:

```typescript
const useDrugDiscoveryStore = create((set) => ({
  literatureResults: null,
  moleculeAnalysis: null,
  trialAnalysis: null,
  // ... actions and state updates
}));
```

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Submit a Pull Request

## Learn More 📚

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Radix UI Documentation](https://www.radix-ui.com/docs/primitives)
- [3Dmol.js Documentation](https://3dmol.csb.pitt.edu/)
- [Zustand Documentation](https://github.com/pmndrs/zustand)

## Security 🔒

- All API calls use HTTPS
- Environment variables for sensitive data
- CSP headers for security
- Input sanitization and validation

## Deployment with Azure Developer CLI (azd) 🚀

1. **Install Azure Developer CLI**:
   ```bash
   curl -fsSL https://aka.ms/install-azd.sh | bash
   ```

2. **Login to Azure**:
   ```bash
   azd auth login
   ```

3. **Deploy from Root Directory**:
   From the root of "3-e2e-drug-discovery-sample/", run:
   ```bash
   azd init
   azd up
   ```

This will:
- Create Azure Static Web App for the frontend
- Configure environment variables
- Deploy the frontend application
- Output the public URL for your site

After deployment:
- Access your site at the provided Static Web App URL
- The backend API URL will be automatically configured

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.
