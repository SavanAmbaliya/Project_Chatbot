import random
from datetime import datetime
now = datetime.now().strftime("%H:%M:%S")

interesting_facts = [
    "Honey never spoils. Archaeologists have found 3,000-year-old honey in Egyptian tombs that’s still edible! 🍯",
    "Bananas are berries, but strawberries aren’t! 🍌🍓",
    "Octopuses have three hearts and blue blood. ❤️💙",
    "A day on Venus is longer than a year on Venus. It rotates very slowly but orbits the Sun faster. 🪐",
    "Sharks existed before trees. Sharks have been around for over 400 million years! 🦈🌳",
    "There are more stars in the universe than grains of sand on Earth. ✨",
    "Wombat poop is cube-shaped. This helps it mark territory without rolling away. 🐾",
    "Sloths can hold their breath longer than dolphins. Some sloths can slow their heart rate and stay underwater for 40 minutes! 🦥",
    "Butterflies can taste with their feet. 🦋"
    "The Eiffel Tower can be 15 cm taller during summer due to thermal expansion of the metal. 🗼"
]
jokes = [
    "Why did the computer catch a cold? Because it left its Windows open! 🪟😂",
    "Why was the math book sad? It had too many problems. ➗😢",
    "Why did the robot go on a diet? It had too many bytes! 💾🥗",
    "What’s a computer’s favorite beat? An algo-rhythm! 🎵🤖",
    "Why don’t scientists trust atoms? Because they make up everything! ⚛️😂",
    "Why did the developer go broke? Because he used up all his cache! 💸💻",
    "What did one ocean say to the other ocean? Nothing — they just waved! 🌊👋",
    "Why did the scarecrow win an award? Because he was outstanding in his field! 🌾🏆", 
    "Why was the computer tired when it got home? It had a hard drive! 🚗💻",
    "What’s a robot’s favorite snack? Computer chips! 🍟🤖"
    ]
chatbot_qa = {
    "hello": "How can I help you?",
    "how are you": "I'm doing great! How about you?",
    "what is your name":"I'm your friendly chatbot! You can call me Chatty 🤖",
    "what do you do":"I chat with users, tell jokes and give facts",
    "what's the current time": ""+datetime.now().strftime("%H:%M:%S"),
    "what's today's date": ""+datetime.now().strftime("%Y-%m-%d"),
    "tell me a joke": random.choice(jokes),
    "tell me an interesting fact": random.choice(interesting_facts),
    "what's your favorite color": "I like blue — it reminds me of clear skies and calm code editors. 💙",
    "can you help me with a math problem": "Of course! Give me your math question and I’ll solve it step by step. ➗",
    "are you real":"I'm a virtual chatbot, so not exactly real, but I can chat with you! 🤖",
    "goodbye": "Goodbye! Have a wonderful day! 👋"
}

def get_response(user_input):
    user_input = user_input.lower().strip()
    if "tell me a joke" in user_input:
        return random.choice(jokes)
    if "tell me an interesting fact" in user_input:
        return random.choice(interesting_facts)
    for key in chatbot_qa:
        if key in user_input:
            return chatbot_qa[key]
    return "the user question isn't recognized and the user should ask another one. 🤔"

def chat():
    print(now ,"Chatbot: Hi! Type 'bye' to exit.")
    while True:
        user_input = input("You: ")
        if "bye" in user_input.lower():
            print(now ,"Chatbot:", chatbot_qa["goodbye"])
            break
        print(now ,"Chatbot:", get_response(user_input))

if __name__ == "__main__":
    chat()