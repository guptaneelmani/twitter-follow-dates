import anthropic

_SYSTEM = (
    "You are a travel specialist. Use web search to find current flight options, "
    "hotel availability, visa requirements, local tips, and costs. "
    "Structure your response clearly: overview, key logistics, estimated budget, "
    "and practical tips. Always mention the best time to visit and any advisories."
)

_TOOLS = [{"type": "web_search_20260209", "name": "web_search"}]


class TravelAgent:
    def __init__(self):
        self.client = anthropic.Anthropic()

    def run(self, query: str) -> str:
        messages = [{"role": "user", "content": query}]

        for _ in range(5):
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

            messages = [
                {"role": "user", "content": query},
                {"role": "assistant", "content": response.content},
            ]

        print()
        return next((b.text for b in response.content if b.type == "text"), "")
