import getpass
import os
from langchain_groq import ChatGroq


if "GROQ_API_KEY" not in os.environ:
    os.environ["GROQ_API_KEY"] = "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"

with open("rules.txt", "r") as f:
    system_prompt = f.read()
    
def Gen_response(text :str, lang: str):
    llm = ChatGroq(
        model="mixtral-8x7b-32768",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    messages = [
        (
            "system", system_prompt),
        ("human", "I love programming."),
    ]
    ai_msg = llm.invoke(messages)
    return ai_msg.content


if __name__ == "__main__":
    user_text = input("Enter your text: ")
    print("Response:", Gen_response(user_text, "en"))