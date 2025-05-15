import getpass
import os
from langchain_groq import ChatGroq

if "GROQ_API_KEY" not in os.environ:
    os.environ["GROQ_API_KEY"] = "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"

with open(r"C:\Users\patel\Desktop\talkme.i\utiles\llm\rules.txt", "r", encoding="utf-8", errors="replace") as f:
    system_prompt = f.read()

conversation = [("system", system_prompt)]

llm = ChatGroq(
    model="mixtral-8x7b-32768",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

def Gen_response(user_text: str, lang: str = "en") -> str:
    conversation.append(("human", user_text))
    ai_msg = llm.invoke(conversation)
    conversation.append(("assistant", ai_msg.content))
    return ai_msg.content

def main():
    print("ChatBot: Hello! How can I help you today? (Type 'bye' or 'thank you' to exit)")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["bye", "thankyou", "thank you"]:
            print("ChatBot: Thank you for chatting! Goodbye!")
            break
        response = Gen_response(user_input)
        print("ChatBot:", response)

if __name__ == "__main__":
    main()
