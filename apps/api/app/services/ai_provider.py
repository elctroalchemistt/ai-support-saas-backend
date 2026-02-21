from dataclasses import dataclass

@dataclass
class DraftContext:
    subject: str
    last_messages: list[str]
    kb_snippets: list[str]
    tone: str

class MockAIProvider:
    def draft_reply(self, ctx: DraftContext) -> str:
        tone = ctx.tone.lower().strip()
        opening = "Hey! Thanks for reaching out." if tone == "friendly" else "Hello, thank you for contacting support."

        bullets = []
        if ctx.kb_snippets:
            bullets.append("Based on our knowledge base, here are the relevant points:")
            for s in ctx.kb_snippets[:3]:
                bullets.append(f"- {s[:140]}")

        summary = " ".join(ctx.last_messages[-2:])[:220] if ctx.last_messages else ""
        body = f"{opening}\n\nI reviewed your ticket about: {ctx.subject}.\n"
        if summary:
            body += f"\nSummary of your latest message(s): {summary}\n"

        if bullets:
            body += "\n" + "\n".join(bullets) + "\n"

        closing = "\nIf you confirm a couple details, I can help you faster.\n\nBest regards,"
        return body + closing
