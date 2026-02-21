import "./globals.css";
import Link from "next/link";

export const metadata = {
  title: "AI Support Mini SaaS",
  description: "Secure, fast, resume-ready AI helpdesk",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen flex flex-col">
          <header className="border-b border-slate-200 bg-white">
            <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
              <div>
                <h1 className="text-lg font-semibold text-slate-900">
                  AI Support Mini SaaS
                </h1>
                <p className="text-xs text-slate-500">
                  Secure • Fast • Resume-Ready
                </p>
              </div>

              <nav className="flex gap-4 text-sm">
                <Link href="/orgs" className="text-slate-600 hover:text-blue-600">
                  Workspaces
                </Link>
                <Link href="/" className="text-slate-600 hover:text-blue-600">
                  Login
                </Link>
              </nav>
            </div>
          </header>

          <main className="flex-1 max-w-6xl mx-auto w-full px-6 py-8">
            {children}
          </main>

          <footer className="border-t border-slate-200 text-xs text-slate-500 text-center py-4">
            Built with FastAPI + Next.js • AI Powered
          </footer>
        </div>
      </body>
    </html>
  );
}
