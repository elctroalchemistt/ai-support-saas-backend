"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function Home() {
  const router = useRouter();

  const [email, setEmail] = useState("test1@example.com");
  const [password, setPassword] = useState("12345678");
  const [msg, setMsg] = useState<string>("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    // اگر لاگین هست، مستقیم برو orgs
    (async () => {
      try {
        await api("/auth/me");
        router.push("/orgs");
      } catch {}
    })();
  }, [router]);

  async function run(action: "signup" | "login") {
    setBusy(true);
    setMsg("");
    try {
      await api(`/auth/${action}`, {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      setMsg(action === "signup" ? "Account created ✅" : "Logged in ✅");
      router.push("/orgs");
    } catch (e: any) {
      setMsg(`Error: ${e.message}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-[calc(100vh-120px)] grid place-items-center">
      <div className="w-full max-w-md card overflow-hidden">
        <div className="p-5 border-b border-slate-200"
             style={{ background: "linear-gradient(135deg, rgb(239 246 255), rgb(238 242 255))" }}>
          <div className="text-sm text-slate-600">Welcome back</div>
          <div className="text-xl font-semibold">Secure Login</div>
          <div className="text-xs text-slate-500 mt-1">
            Cookie-based auth • FastAPI • Postgres • Next.js
          </div>
        </div>

        <div className="p-5 space-y-3">
          <label className="block">
            <div className="text-xs text-slate-600 mb-1">Email</div>
            <input className="input" value={email} onChange={(e) => setEmail(e.target.value)} />
          </label>

          <label className="block">
            <div className="text-xs text-slate-600 mb-1">Password</div>
            <input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
            <div className="text-xs text-slate-500 mt-1">Minimum 8 characters</div>
          </label>

          <div className="flex gap-2 pt-2">
            <button className="btn btn-primary flex-1" disabled={busy} onClick={() => run("login")}>
              {busy ? "..." : "Login"}
            </button>
            <button className="btn flex-1" disabled={busy} onClick={() => run("signup")}>
              Signup
            </button>
          </div>

          {msg && (
            <div className="text-sm rounded-xl border border-slate-200 bg-slate-50 px-3 py-2">
              {msg}
            </div>
          )}

          <div className="text-xs text-slate-500 pt-1">
            Tip: بعد از Login، مستقیم می‌ری صفحه Workspaces.
          </div>
        </div>
      </div>
    </div>
  );
}
