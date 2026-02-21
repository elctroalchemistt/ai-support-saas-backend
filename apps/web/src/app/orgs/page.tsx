"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import Link from "next/link";
import { useRouter } from "next/navigation";

type Org = {
  id: number;
  name: string;
};

export default function OrgsPage() {
  const router = useRouter();
  const [orgs, setOrgs] = useState<Org[]>([]);
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(true);

  async function checkAuth() {
    try {
      await api("/auth/me");
      await load();
    } catch {
      router.push("/");
    } finally {
      setLoading(false);
    }
  }

  async function load() {
    const data = await api<{ items: Org[] }>("/orgs");
    setOrgs(data.items);
  }

  async function create() {
    if (!name.trim()) return;
    await api("/orgs", {
      method: "POST",
      body: JSON.stringify({ name }),
    });
    setName("");
    load();
  }

  useEffect(() => {
    checkAuth();
  }, []);

  if (loading) {
    return <p className="text-center text-slate-500">Loading...</p>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between">
        <h2 className="text-2xl font-semibold">Your Workspaces</h2>

        <button
          className="btn"
          onClick={async () => {
            await api("/auth/logout", { method: "POST" });
            router.push("/");
          }}
        >
          Logout
        </button>
      </div>

      <div className="card p-4 flex gap-3">
        <input
          className="input flex-1"
          placeholder="Workspace name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <button className="btn btn-success" onClick={create}>
          Create
        </button>
      </div>

      <div className="space-y-3">
        {orgs.map((org) => (
          <div
            key={org.id}
            className="card p-4 flex justify-between items-center"
          >
            <div>
              <p className="font-medium">{org.name}</p>
              <p className="text-xs text-slate-500">
                Workspace #{org.id}
              </p>
            </div>

            <Link
              href={`/orgs/${org.id}/tickets`}
              className="btn btn-primary"
            >
              Open Inbox →
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
