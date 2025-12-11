import argparse
import csv
import os
import logging
import random
import re
from difflib import get_close_matches
from datetime import datetime

# ============== Configuration ==============
QUESTIONS_CSV_FILE = "D:\\python\\questions.csv"
# CHATBOT_CSV_FILE = "D:\\OSTFALIA\\chatbot_questions.csv"

# ============== Logging Setup ==============
def setup_logging(enable_logging, level):
    if enable_logging:
        numeric_level = getattr(logging, level.upper(), None)
        if not isinstance(numeric_level, int):
            print(f"Invalid log level: {level}, using WARNING")
            numeric_level = logging.WARNING
        logging.basicConfig(level=numeric_level, format='[%(levelname)s] %(message)s')
        logging.info("Logging enabled at level: %s", level)
    else:
        logging.basicConfig(level=logging.CRITICAL)


# ============== Chatbot Data & Functions ==============
interesting_facts = [
    "Honey never spoils. Archaeologists have found 3,000-year-old honey in Egyptian tombs that's still edible! 🍯",
    "Bananas are berries, but strawberries aren't! 🍌🍓",
    "Octopuses have three hearts and blue blood. ❤️💙",
    "A day on Venus is longer than a year on Venus. It rotates very slowly but orbits the Sun faster. 🪐",
    "Sharks existed before trees. Sharks have been around for over 400 million years! 🦈🌳",
    "There are more stars in the universe than grains of sand on Earth. ✨",
    "Wombat poop is cube-shaped. This helps it mark territory without rolling away. 🐾",
    "Sloths can hold their breath longer than dolphins. Some sloths can slow their heart rate and stay underwater for 40 minutes! 🦥",
    "Butterflies can taste with their feet. 🦋",
    "The Eiffel Tower can be 15 cm taller during summer due to thermal expansion of the metal. 🗼"
]

jokes = [
    "Why did the computer catch a cold? Because it left its Windows open! 🪟😂",
    "Why was the math book sad? It had too many problems. ➗😢",
    "Why did the robot go on a diet? It had too many bytes! 💾🥗",
    "What's a computer's favorite beat? An algo-rhythm! 🎵🤖",
    "Why don't scientists trust atoms? Because they make up everything! ⚛️😂",
    "Why did the developer go broke? Because he used up all his cache! 💸💻",
    "What did one ocean say to the other ocean? Nothing — they just waved! 🌊👋",
    "Why did the scarecrow win an award? Because he was outstanding in his field! 🌾🏆",
    "Why was the computer tired when it got home? It had a hard drive! 🚗💻",
    "What's a robot's favorite snack? Computer chips! 🍟🤖",
]

keyword_questions = {
    "semester": [
        "What subjects are included in this semester?",
        "How many credits are required this semester?",
        "Can you provide notes for this semester?"
    ],
    "python": [
        "Python is a popular programming language.",
        "Python supports object-oriented programming.",
        "You can use Python for web development, data science, and AI."
    ],
    "ai": [
        "AI stands for Artificial Intelligence.",
        "Machine learning is a subset of AI.",
        "AI is used in daily life like voice assistants and recommendations."
    ],
    "cryptography": [
        "Cryptography is the art of secure communication.",
        "RSA is a popular public-key cryptography algorithm.",
        "AES is a widely used symmetric encryption standard."
    ],
    "rsa": [
        "RSA uses two prime numbers to generate keys.",
        "RSA allows secure communication over insecure channels.",
        "The private key in RSA should be kept secret."
    ],
    "germany": [
        "Germany is in Europe and its capital is Berlin.",
        "Braunschweig is a city in Lower Saxony, Germany.",
        "Wolfenbüttel is famous for its historical architecture."
    ],
    "flowers": [
        "You can give yellow flowers to friends.",
        "Red flowers are usually for love or romance.",
        "White flowers often symbolize purity."
    ],
    "insta": [
        "Use aesthetic captions and songs for your Insta story.",
        "Try trending hashtags to increase engagement.",
        "Photos with soft lighting and pastel colors look nice."
    ],
    "uml": [
        "UML stands for Unified Modeling Language.",
        "Sequence diagrams show how objects interact over time.",
        "Use case diagrams show the functionality of a system."
    ],
    "projects": [
        "College projects are important for practical learning.",
        "Choose a project topic that interests you.",
        "Make sure to plan your project before starting."
    ],
    "notes": [
        "Notes help you revise quickly before exams.",
        "Organize your notes by subject and topic.",
        "Use bullet points and diagrams for better understanding."
    ]
}

HALL_DATA = {
    "cryptography": {
        "where is lecturing hall cryptography": "Am Exer 7",
        "what is the location of lecturing hall cryptography": "Café Limes, Am Exer 7, 38302 Wolfenbüttel",
        "where is lecturing hall cryptography located": "It is located in Wolfenbüttel near Exer Süd",
        "how do i reach lecturing hall cryptography": "Just enter from the gate and turn left, then walk for 2 minutes."
    },
    "sicherheit": {
        "where is lecturing hall sicherheit": "Hall E in Fachhochschule",
        "what is the location of lecturing hall sicherheit": "Salzdahlumer Str. 46/48, 38302 Wolfenbüttel",
        "where is lecturing hall sicherheit located": "It is located near Mittelweg Wolfenbüttel",
        "how do i reach lecturing hall sicherheit": "Just enter from the main gate and go right from downstairs."
    },
    "software for autonomous safety critical systems": {
        "where is lecturing hall software for autonomous safety critical systems": "Hall E in Fachhochschule",
        "what is the location of lecturing hall software for autonomous safety critical systems": "Salzdahlumer Str. 46/48, 38302 Wolfenbüttel",
        "where is lecturing hall software for autonomous safety critical systems located": "It is located near Mittelweg Wolfenbüttel",
        "how do i reach lecturing hall software for autonomous safety critical systems": "Just enter from the main gate and go right from downstairs."
    },
    "german a2.2": {
        "where is lecturing hall german a2.2": "Am Exer 2 Raum 187",
        "what is the location of lecturing hall german a2.2": "Am Exer 2, 38302 Wolfenbüttel",
        "where is lecturing hall german a2.2 located": "It is located in Wolfenbüttel near Exer Süd",
        "how do i reach lecturing hall german a2.2": "It is the 2nd room on the first floor"
    },
}

# Global chatbot QA dictionary
chatbot_qa = {}


# ============== CSV Management Functions ==============
def load_questions():
    """Load questions from internal CSV file."""
    logging.info(f"Loading internal CSV from: {QUESTIONS_CSV_FILE}")
    if not os.path.exists(QUESTIONS_CSV_FILE):
        logging.warning("Internal CSV does not exist. Returning empty store.")
        return {}
    chatbot_qa = {}
    try:
        with open(QUESTIONS_CSV_FILE, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    chatbot_qa[row[0]] = row[1:]
                else:
                    logging.warning("Encountered malformed row in CSV: %s", row)
    except Exception as e:
        logging.warning("Error reading CSV: %s", e)
    logging.info(f"Loaded {len(chatbot_qa)} questions")
    return chatbot_qa


def save_questions(questions):
    """Save questions to internal CSV file."""
    try:
        with open(QUESTIONS_CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for q, answers in questions.items():
                writer.writerow([q] + answers)
        logging.info(f"Saved {len(questions)} questions to CSV")
    except Exception as e:
        logging.warning(f"Error saving CSV: {e}")


def add_answer(question, answer):
    """Add an answer to a question."""
    logging.info(f"Adding answer '{answer}' to question '{question}'")
    chatbot_qa = load_questions()
    chatbot_qa.setdefault(question, [])
    if answer in chatbot_qa[question]:
        logging.warning(f"Answer already exists for question '{question}'")
        return
    chatbot_qa[question].append(answer)
    save_questions(chatbot_qa)
    logging.info(f"Added answer '{answer}' to question '{question}'")


def remove_answer(question, answer):
    """Remove an answer from a question."""
    logging.info(f"Removing answer '{answer}' from question '{question}'")
    chatbot_qa = load_questions()
    if question not in chatbot_qa:
        logging.warning(f"Question not found: {question}")
        return
    if answer in chatbot_qa[question]:
        chatbot_qa[question].remove(answer)
        logging.info(f"Removed answer '{answer}' from question '{question}'")
        if not chatbot_qa[question]:
            del chatbot_qa[question]
            logging.info(f"No answers remain. Question '{question}' removed completely.")
    else:
        logging.warning(f"Answer '{answer}' not found for question '{question}'")
    save_questions(chatbot_qa)


def import_csv(import_path):
    """Import questions from an external CSV file."""
    logging.info(f"Importing CSV file: {import_path}")
    if not os.path.exists(import_path):
        logging.warning(f"File does not exist: {import_path}")
        return
    if not import_path.lower().endswith(".csv"):
        logging.warning("Unsupported file type, only CSV allowed")
        return
    imported = {}
    try:
        with open(import_path, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader, start=1):
                if len(row) < 2:
                    logging.warning(f"Skipping malformed row {i}: {row}")
                    continue
                question = row[0].strip()
                answers = [a.strip() for a in row[1:]]
                imported[question] = answers
    except PermissionError:
        logging.warning("Access denied to file: %s", import_path)
        return
    except csv.Error:
        logging.warning("Corrupted CSV file: %s", import_path)
        return
    existing = load_questions()
    existing.update(imported)
    save_questions(existing)
    logging.info(f"Imported {len(imported)} questions from {import_path}")


def list_questions():
    """List all stored questions."""
    chatbot_qa = load_questions()
    print("\nStored Questions:")
    for q in chatbot_qa:
        print(f"- {q}")


def list_full():
    """List all questions with their answers."""
    chatbot_qa = load_questions()
    print("\nQuestions with Answers:")
    for q, answers in chatbot_qa.items():
        print(f"{q}")
        for a in answers:
            print(f"   - {a}")


# ============== Chatbot Functions ==============
def load_chatbot_csv(filepath):
    """Load chatbot questions and answers from a CSV file."""
    global chatbot_qa
    chatbot_qa = {}
    print(f"Loading chatbot CSV from: {filepath}")
    try:
        with open(filepath, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) >= 2:
                    question = row[0].strip()
                    answers = [ans.strip() for ans in row[1:] if ans.strip()]
                    if question and answers:
                        chatbot_qa[question.lower()] = answers
    except FileNotFoundError:
        logging.warning(f"Chatbot CSV not found: {filepath}")
    except Exception as e:
        logging.warning(f"Error loading chatbot CSV: {e}")
    return chatbot_qa


def normalize(text: str) -> str:
    """Normalize text for matching."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def find_hall(user_question: str):
    """Find lecturing hall from question."""
    for hall in HALL_DATA.keys():
        if hall in user_question.lower():
            return hall
    return None


def answer_question1(user_question: str) -> str:
    """Answer hall-related questions."""
    norm_user_q = normalize(user_question)
    hall = find_hall(user_question)

    if not hall:
        return "Please mention the subject name."

    hall_questions = HALL_DATA[hall]
    known_questions = list(hall_questions.keys())

    matches = get_close_matches(norm_user_q, known_questions, n=1, cutoff=0.5)

    if matches:
        return hall_questions[matches[0]]
    else:
        return "Sorry, I don't have details for that question yet."


def is_single_word(text: str) -> bool:
    """Check if input is a single word."""
    if text.lower() in ["hi", "hello"]:
        return False
    cleaned = text.strip()
    words = cleaned.split()
    return len(words) == 1


def get_related_question(keyword):
    """Get related questions for a keyword."""
    if keyword.lower() in keyword_questions:
        print("\n", datetime.now().strftime('%H:%M:%S'), " 📌 Related Questions:")
        chatbot_qa = keyword_questions[keyword.lower()]

        for i, q in enumerate(chatbot_qa, start=1):
            print(f"{i}. {q}")

        try:
            choice = int(input("\nEnter the number of your question: "))
            if 1 <= choice <= len(chatbot_qa):
                selected = chatbot_qa[choice - 1]
                print(datetime.now().strftime('%H:%M:%S'), f"\n👉 You selected: {selected}")
                return selected
            else:
                print(datetime.now().strftime('%H:%M:%S'), "❌ Invalid selection.")
                return None
        except ValueError:
            print("\n", datetime.now().strftime('%H:%M:%S'), " ❌ Invalid input. Please type a number.")
            return None
    else:
        print(datetime.now().strftime('%H:%M:%S'), "❓ No related questions found for this keyword.")
        return None


def get_response(user_input):
    """Get chatbot response based on user input."""
    user_input = user_input.lower().strip()
    
    # Check chatbot QA
    for key in chatbot_qa:
        if key in user_input:
            answers = chatbot_qa[key]
            stopwords = ["what", "is", "your", "the", "a", "do", "are", "can", "help", "i", "you", "me", "with", "to", "of", "in", "on", "my", "for", "and", "how", "tell", "about"]
            words = [w for w in user_input.split() if w.isalpha() and w not in stopwords]
            keywords = [w.capitalize() for w in words if len(w) > 2]

            response = random.choice(answers)

            if len(user_input.split()) <= 5 and keywords:
                related_topics = []
                for kw in keywords[:3]:
                    for topic_key in chatbot_qa.keys():
                        if kw.lower() in topic_key and topic_key != key:
                            related_topics.append(topic_key.replace("_", " ").title())
                            break

                if related_topics:
                    suggestion_text = f"\n\n💡 You might also ask about: {', '.join(related_topics[:3])}"
                    return response + suggestion_text
                elif keywords:
                    suggestion_text = f"\n\n💡 Related keywords: {', '.join(keywords[:3])}"
                    return response + suggestion_text

            return response
    
    return "The question isn't recognized. Please ask another one. 🤔"


def count_questions(sentence):
    """Count number of questions in a sentence."""
    question_mark_count = sentence.count('?')
    if question_mark_count > 0:
        return question_mark_count
    else:
        return len(sentence.split(' and '))


def split_into_questions(sentence):
    """Split sentence into multiple questions."""
    questions = sentence.split(" and ")
    questions = [q.strip().rstrip('?') + '?' for q in questions]
    return questions


def chat():
    """Interactive chatbot chat mode."""
    print(datetime.now().strftime('%H:%M:%S'), "Chatbot: Hi! Type 'bye' to exit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print(datetime.now().strftime('%H:%M:%S'), "Chatbot: Goodbye! Have a wonderful day! 👋")
            break
        if is_single_word(user_input):
            get_related_question(user_input)
        else:
            if count_questions(user_input) == 1:
                print(datetime.now().strftime('%H:%M:%S'), "Chatbot:", get_response(user_input))
            else:
                questions = split_into_questions(user_input)
                for i, q in enumerate(questions, 1):
                    print(datetime.now().strftime('%H:%M:%S'), "Chatbot:", get_response(q))


# ============== Main Function ==============
def main():
    parser = argparse.ArgumentParser(description="Integrated Chatbot & Question Manager CLI")
    
    # Logging arguments
    parser.add_argument("--log", action="store_true", help="Enable logging mode")
    parser.add_argument("--log-level", type=str, default="WARNING", help="Logging level: INFO or WARNING")
    
    # Question Manager arguments
    parser.add_argument("--add", action="store_true", help="Add a question/answer")
    parser.add_argument("--remove", action="store_true", help="Remove an answer")
    parser.add_argument("--list", action="store_true", help="List all questions")
    parser.add_argument("--list-full", action="store_true", help="List questions with answers")
    parser.add_argument("--import-csv", type=str, help="Import CSV file")
    parser.add_argument("--question", type=str, help="Question text")
    parser.add_argument("--answer", type=str, help="Answer text")
    
    args = parser.parse_args()
    
    setup_logging(args.log, args.log_level)
    
    # Load chatbot CSV if it exists
    load_chatbot_csv(QUESTIONS_CSV_FILE)
    
    # Handle Question Manager operations
    if args.import_csv:
        import_csv(args.import_csv)
        return
    if args.add:
        if not args.question or not args.answer:
            logging.warning("--add requires --question and --answer")
            return
        add_answer(args.question, args.answer)
        return
    if args.remove:
        if not args.question:
            logging.warning("--remove requires --question")
            return
        remove_answer(args.question, args.answer)
        return
    if args.list:
        list_questions()
        return
    if args.list_full:
        list_full()
        return
    
    # Handle Chatbot operations
    if args.question:
        if is_single_word(args.question):
            get_related_question(args.question)
        else:
            if count_questions(args.question) == 1:
                print(datetime.now().strftime('%H:%M:%S'), "Chatbot:", get_response(args.question))
            else:
                questions = split_into_questions(args.question)
                for i, q in enumerate(questions, 1):
                    print(datetime.now().strftime('%H:%M:%S'), "Chatbot:", get_response(q))
    else:
        # Start interactive chatbot
        chat()


if __name__ == "__main__":
    main()
