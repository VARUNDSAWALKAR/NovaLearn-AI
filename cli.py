"""Optional command-line interface to the same chatbot."""
from chatbot import (
    ChatbotConfigurationError, ChatbotResponseError, TOPICS,
    answer_question, build_chain, load_settings,
)


def main():
    print("AI Question-Answering Chatbot (type 'exit' to quit)")
    try:
        settings = load_settings()
        topic = "Study Assistant"
        chain = build_chain(settings, topic)
    except (ChatbotConfigurationError, Exception) as exc:
        # Avoid leaking raw credentials or provider error payloads.
        if isinstance(exc, ChatbotConfigurationError):
            print(f"Setup error: {exc}")
        else:
            print("Setup error: Could not initialize model. Check requirements and config.")
        return
    history = []
    while True:
        try:
            question = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if question.lower() in ("exit", "quit"):
            break
        try:
            answer = answer_question(chain, question, topic, history)
        except (ValueError, ChatbotResponseError) as exc:
            print(f"Error: {exc}")
            continue
        print(f"\nAssistant: {answer}")
        history.extend([
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ])
    print("Goodbye!")


if __name__ == "__main__":
    main()
