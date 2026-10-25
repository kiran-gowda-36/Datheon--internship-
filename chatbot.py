"""Rule-Based Interactive Terminal Chatbot.

A customer-support style assistant that understands several intents in one
message (greeting, business hours, FAQs, thanks, exit) using keywords and
regular expressions. FAQ answers are loaded from sample_faq.json.

Run with:  python chatbot.py
"""

import json
import os
import re

FAQ_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_faq.json")

# Used only if sample_faq.json is missing.
DEFAULT_DATA = {
    "greetings": ["hello", "hi", "hey", "good morning", "good afternoon"],
    "faqs": [
        {"question": "What are your hours of operation?",
         "answer": "We operate Monday through Friday from 9:00 AM to 6:00 PM IST."},
    ],
}

# ---------- rules (regular expressions) ----------

EXIT_RE = re.compile(r"\b(bye|goodbye|exit|quit)\b")
THANKS_RE = re.compile(r"\b(thanks|thank you|thx)\b")
HELP_RE = re.compile(r"\b(help|what can you do|options)\b")
HOURS_RE = re.compile(
    r"\b(hours?|timings?|open|opening|close|closing|working time|business time|"
    r"operation|operate|available|availability)\b"
)
NAME_RE = re.compile(r"\b(?:my name is|i am|i'm|call me)\s+([a-z]+)")
YES_RE = re.compile(r"^(yes|yeah|yep|sure|ok|okay)\b")
NO_RE = re.compile(r"^(no|nope|nothing|that's all|thats all)\b")

# Words ignored when comparing a message with a FAQ question.
STOPWORDS = {
    "a", "an", "the", "is", "are", "do", "does", "did", "i", "my", "me", "you",
    "your", "we", "our", "can", "will", "to", "of", "for", "in", "on", "and",
    "or", "how", "what", "when", "where", "which", "who", "it", "if", "be",
    "please", "tell", "about", "need", "want", "would", "could", "should",
}

# Different words that mean the same thing.
SYNONYMS = {
    "get": "receive", "got": "receive", "send": "submit", "upload": "submit",
    "turn": "submit", "cert": "certificate", "certification": "certificate",
    "repo": "project", "repository": "project", "work": "project",
}

FAQ_MATCH_THRESHOLD = 0.5   # share of a FAQ question's key words that must match


# ---------- helpers ----------

def load_data():
    """Load greetings and FAQs from the JSON dataset."""
    try:
        with open(FAQ_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        print("(sample_faq.json not found or invalid - using built-in answers.)\n")
        return DEFAULT_DATA


def normalize(text):
    """Lowercase, trim and remove punctuation (keeps apostrophes)."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9'\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def keywords(text):
    """Important words of a sentence: no stopwords, simple plural removal."""
    words = []
    for w in normalize(text).split():
        if w in STOPWORDS:
            continue
        if len(w) > 3 and w.endswith("s"):
            w = w[:-1]
        words.append(SYNONYMS.get(w, w))
    return set(words)


def is_greeting(message, greetings):
    return any(re.search(rf"\b{re.escape(g)}\b", message) for g in greetings)


def best_faq_matches(message, faqs):
    """Return (score, faq) pairs above the threshold, best first."""
    user_words = keywords(message)
    matches = []
    for faq in faqs:
        q_words = keywords(faq["question"])
        if not q_words:
            continue
        score = len(user_words & q_words) / len(q_words)
        # Match if enough key words overlap, or if everything the user said
        # is part of the question (e.g. a short message like "certificate").
        short_match = bool(user_words) and user_words <= q_words
        if score >= FAQ_MATCH_THRESHOLD or short_match:
            matches.append((score, faq))
    return sorted(matches, key=lambda m: m[0], reverse=True)


def find_hours_answer(faqs):
    for faq in faqs:
        if "hour" in faq["question"].lower():
            return faq["answer"]
    return "We operate Monday through Friday from 9:00 AM to 6:00 PM IST."


# ---------- the chatbot ----------

class Chatbot:
    def __init__(self):
        data = load_data()
        self.greetings = data.get("greetings", DEFAULT_DATA["greetings"])
        self.faqs = data.get("faqs", [])
        self.name = None
        # Conversation state: GREETING -> LISTENING -> RESOLVED -> EXIT
        self.state = "GREETING"
        self.topics_covered = []   # remembers what was already answered

    def reply(self, raw):
        """Return (response text, keep_going)."""
        message = normalize(raw)
        if not message:
            return "I didn't catch that. Could you type your question again?", True

        parts = []          # one piece of response per detected intent
        answered = set()    # avoid giving the same answer twice

        # Context: short replies to "Anything else?"
        if self.state == "RESOLVED":
            if NO_RE.match(message):
                self.state = "EXIT"
                return self.goodbye(), False
            if YES_RE.match(message) and len(message.split()) <= 2:
                return "Great, go ahead and ask me your next question.", True

        # Intent: user tells us their name
        name_match = NAME_RE.search(message)
        if name_match:
            self.name = name_match.group(1).capitalize()
            parts.append(f"Nice to meet you, {self.name}!")

        # Intent: greeting
        if is_greeting(message, self.greetings):
            hello = f"Hello{', ' + self.name if self.name else ''}!"
            if self.state == "GREETING":
                hello += " I'm the Datheon support assistant. How can I help you today?"
            parts.append(hello)

        # Intent: business hours
        if HOURS_RE.search(message):
            answer = find_hours_answer(self.faqs)
            parts.append(answer)
            answered.add(answer)
            self.topics_covered.append("business hours")

        # Intent: FAQs (can match more than one in a single message)
        for score, faq in best_faq_matches(message, self.faqs):
            if faq["answer"] not in answered:
                parts.append(faq["answer"])
                answered.add(faq["answer"])
                self.topics_covered.append(faq["question"])

        # Intent: help and thanks
        if HELP_RE.search(message):
            parts.append("I can tell you our business hours and answer questions such as:\n"
                         + "\n".join(f"  - {f['question']}" for f in self.faqs))
        if THANKS_RE.search(message):
            parts.append("You're welcome!")

        # Intent: exit (handled last so other answers still appear)
        wants_exit = bool(EXIT_RE.search(message))

        if wants_exit:
            self.state = "EXIT"
            parts.append(self.goodbye())
            return "\n".join(parts), False

        # Fallback: nothing was recognised
        if not parts:
            return ("Sorry, I'm not sure I understand. Try asking about our business "
                    "hours, project submission or certificates - or type 'help'."), True

        # Resolution: after answering, offer more help
        if answered or THANKS_RE.search(message):
            self.state = "RESOLVED"
            parts.append("Is there anything else I can help you with?")
        else:
            self.state = "LISTENING"
        return "\n".join(parts), True

    def goodbye(self):
        who = f", {self.name}" if self.name else ""
        return f"Goodbye{who}! Thanks for chatting with us. Have a great day!"


def main():
    print("=" * 50)
    print(" Datheon Support Assistant  (type 'bye' to exit)")
    print("=" * 50)
    bot = Chatbot()
    while True:
        try:
            user = input("\nYou: ")
        except (EOFError, KeyboardInterrupt):
            print("\nBot: Goodbye!")
            break
        response, keep_going = bot.reply(user)
        print("Bot:", response)
        if not keep_going:
            break


if __name__ == "__main__":
    main()
