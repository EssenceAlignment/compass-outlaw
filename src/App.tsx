import PleadingPaperPreview from './components/PleadingPaperPreview'

function App() {
  return (
    <div className="min-h-screen bg-gray-200 flex flex-col items-center py-10 gap-6">
      <header className="text-center">
        <h1 className="text-3xl font-bold text-gray-800">Compass Outlaw</h1>
        <p className="text-gray-600 mt-1">California Legal Drafting Assistant</p>
      </header>

      <main className="flex flex-col items-center gap-6">
        <PleadingPaperPreview />
      </main>
    </div>
  )
}

export default App
