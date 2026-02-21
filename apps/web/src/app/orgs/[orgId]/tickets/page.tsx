"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import Link from "next/link";

type Ticket = {
  id: number;
  org_id: number;
  subject: string;
  status: "open" | "closed";
  priority: string;
};

type Message = {
  id: number;
  ticket_id: number;
  author_type: string;
  body: string;
};

export default function TicketsPage() {
  const params = useParams();
  const orgId = Number(params.orgId);

  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const [subject, setSubject] = useState("");
  const [priority, setPriority] = useState("medium");

  const [detail, setDetail] = useState<{ ticket: Ticket; messages: Message[] } | null>(null);

  const [newMsg, setNewMsg] = useState("");
  const [draft, setDraft] = useState<string>("");
  const [loadingDraft, setLoadingDraft] = useState(false);
  const [msg, setMsg] = useState("");

  async function loadTickets() {
    const res = await api<{ items: Ticket[] }>(`/tickets?org_id=${orgId}`);
    setTickets(res.items);
    if (res.items.length && selectedId === null) setSelectedId(res.items[0].id);
  }

  async function loadTicket(ticketId: number) {
    const res = await api<{ ticket: Ticket; messages: Message[] }>(`/tickets/${ticketId}`);
    setDetail(res);
    setDraft("");
    setNewMsg("");
  }

  async function createTicket() {
    setMsg("");
    try {
      const created = await api<Ticket>("/tickets", {
        method: "POST",
        body: JSON.stringify({ org_id: orgId, subject, priority }),
      });
      setSubject("");
      setPriority("medium");
      await loadTickets();
      setSelectedId(created.id);
    } catch (e: any) {
      setMsg(`Error: ${e.message}`);
    }
  }

  async function sendMessage() {
    if (!detail) return;
    setMsg("");
    try {
      await api<Message>(`/tickets/${detail.ticket.id}/messages`, {
        method: "POST",
        body: JSON.stringify({ author_type: "user", body: newMsg }),
      });
      await loadTicket(detail.ticket.id);
    } catch (e: any) {
      setMsg(`Error: ${e.message}`);
    }
  }

  async function getAIDraft() {
    if (!detail) return;
    setLoadingDraft(true);
    setMsg("");
    try {
      const res = await api<{ draft: string }>("/ai/draft-reply", {
        method: "POST",
        body: JSON.stringify({ ticket_id: detail.ticket.id, tone: "friendly" }),
      });
      setDraft(res.draft);
    } catch (e: any) {
      setMsg(`Error: ${e.message}`);
    } finally {
      setLoadingDraft(false);
    }
  }

  // ✅ NEW: status toggle
  async function toggleStatus() {
    if (!detail) return;
    const next = detail.ticket.status === "open" ? "closed" : "open";
    try {
      const updated = await api<Ticket>(`/tickets/${detail.ticket.id}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status: next }),
      });
      setDetail({ ...detail, ticket: updated });
      await loadTickets();
    } catch (e: any) {
      setMsg(`Error: ${e.message}`);
    }
  }

  useEffect(() => {
    if (!Number.isFinite(orgId)) return;
    setSelectedId(null);
    setDetail(null);
    loadTickets();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [orgId]);

  useEffect(() => {
    if (selectedId != null) loadTicket(selectedId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedId]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm text-slate-600">Inbox</div>
          <div className="text-2xl font-semibold">Org #{orgId} tickets</div>
        </div>
        <div className="flex gap-2">
          <Link className="btn" href="/orgs">Back to Workspaces</Link>
          <button className="btn" onClick={loadTickets}>Refresh</button>
        </div>
      </div>

      {msg && (
        <div className="card p-3 text-sm text-slate-700">{msg}</div>
      )}

      <div className="grid grid-cols-12 gap-4">
        {/* Left */}
        <section className="col-span-12 md:col-span-5 card overflow-hidden">
          <div className="p-4 border-b border-slate-200"
               style={{ background: "linear-gradient(135deg, rgb(239 246 255), rgb(238 242 255))" }}>
            <div className="font-semibold">Tickets</div>
            <div className="text-xs text-slate-500">Create, select, and manage conversations.</div>
          </div>

          <div className="p-4 border-b border-slate-200 space-y-2">
            <input
              className="input"
              placeholder="New ticket subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
            />
            <div className="flex gap-2">
              <select className="input w-32" value={priority} onChange={(e) => setPriority(e.target.value)}>
                <option value="low">low</option>
                <option value="medium">medium</option>
                <option value="high">high</option>
              </select>
              <button className="btn btn-success flex-1" onClick={createTicket} disabled={!subject.trim()}>
                Create Ticket
              </button>
            </div>
          </div>

          <div className="divide-y">
            {tickets.map((t) => {
              const active = t.id === selectedId;
              return (
                <button
                  key={t.id}
                  onClick={() => setSelectedId(t.id)}
                  className={`w-full text-left p-4 hover:bg-slate-50 transition ${active ? "bg-slate-50" : ""}`}
                >
                  <div className="font-medium">{t.subject}</div>
                  <div className="text-xs text-slate-500 mt-1 flex gap-2 flex-wrap">
                    <span className="badge">#{t.id}</span>
                    <span className="badge">{t.status}</span>
                    <span className="badge">{t.priority}</span>
                  </div>
                </button>
              );
            })}
            {!tickets.length && <div className="p-4 text-sm text-slate-600">No tickets yet.</div>}
          </div>
        </section>

        {/* Right */}
        <section className="col-span-12 md:col-span-7 card overflow-hidden">
          <div className="p-4 border-b border-slate-200 flex items-center justify-between">
            <div className="font-semibold">{detail ? `Ticket #${detail.ticket.id}` : "Select a ticket"}</div>
            <div className="flex gap-2">
              {detail && (
                <button className="btn" onClick={toggleStatus}>
                  {detail.ticket.status === "open" ? "Close Ticket" : "Reopen"}
                </button>
              )}
              <button className="btn btn-primary" onClick={getAIDraft} disabled={!detail || loadingDraft}>
                {loadingDraft ? "Generating..." : "AI Draft Reply"}
              </button>
            </div>
          </div>

          <div className="p-4 space-y-3">
            {detail ? (
              <>
                <div className="card p-4">
                  <div className="font-semibold">{detail.ticket.subject}</div>
                  <div className="text-xs text-slate-500 mt-1 flex gap-2 flex-wrap">
                    <span className="badge">status: {detail.ticket.status}</span>
                    <span className="badge">priority: {detail.ticket.priority}</span>
                  </div>
                </div>

                <div className="space-y-2">
                  {detail.messages.map((m) => (
                    <div key={m.id} className="card p-4">
                      <div className="text-xs text-slate-500 mb-1">{m.author_type}</div>
                      <div className="whitespace-pre-wrap">{m.body}</div>
                    </div>
                  ))}
                  {!detail.messages.length && <div className="text-sm text-slate-600">No messages yet.</div>}
                </div>

                {draft && (
                  <div className="card p-4">
                    <div className="flex items-center justify-between">
                      <div className="font-semibold">AI Draft</div>
                      <button className="btn" onClick={() => setNewMsg(draft)}>Use as message</button>
                    </div>
                    <textarea className="textarea mt-2" value={draft} onChange={(e) => setDraft(e.target.value)} />
                  </div>
                )}

                <div className="card p-4 space-y-2">
                  <div className="font-semibold">New message</div>
                  <textarea
                    className="textarea"
                    value={newMsg}
                    onChange={(e) => setNewMsg(e.target.value)}
                    placeholder="Write a message..."
                  />
                  <button className="btn btn-success" onClick={sendMessage} disabled={!newMsg.trim()}>
                    Send
                  </button>
                </div>
              </>
            ) : (
              <div className="text-sm text-slate-600">Pick a ticket from the left.</div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
