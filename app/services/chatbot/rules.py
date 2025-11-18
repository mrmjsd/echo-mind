# services/chatbot/rules.py

import re


def get_rules():
    return [
        (r"\b(hi|hello|hey|good morning|good evening)\b", respond_greeting),
        (r"\b(bye|goodbye|see you)\b", respond_farewell),
    ]


def respond_greeting(_): return "Hello! How can I assist you today?"


def respond_farewell(_): return "Goodbye! Have a great day."


def default_response(_): return ""
