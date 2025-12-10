export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <header className="bg-blue-700 text-white py-4 text-center">
        <h1 className="text-2xl font-bold">Rekomendasi Prodi Polindra</h1>
      </header>
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  );
}