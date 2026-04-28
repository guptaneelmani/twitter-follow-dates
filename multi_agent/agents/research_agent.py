import anthropic

_SYSTEM = (
    "You are a research assistant. Use web search to find accurate, up-to-date "
    "information. Synthesise findings into a clear, well-structured answer. "
    "Cite sources inline where relevant. If a topic is contested, present multiple "
    "perspectives fairly."
)

_TOOLS = [{"type": "web_search_20260209", "name": "web_search"}]


class ResearchAgent:
    def __init__(self):
        self.client = anthropic.Anthropic()

    def run(self, query: str) -> str:
        messages = [{"role": "user", "content": query}]

        for _ in range(5):  # guard against infinite pause_turn loops
            with self.client.messages.stream(
                model="claude-opus-4-7",
                max_tokens=4096,
                thinking={"type": "adaptive"},
                system=_SYSTEM,
                tools=_TOOLS,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    print(text, end="", flush=True)
                response = stream.get_final_message()

            if response.stop_reason != "pause_turn":
                break

            # Server hit its tool-loop limit; re-send to continue
            messages = [
                {"role": "user", "content": query},
                {"role": "assistant", "content": response.content},
            ]

        print()
        return next((b.text for b in response.content if b.type == "text"), "")
