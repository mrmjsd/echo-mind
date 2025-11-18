# services/chatbot/bot.py

import re
from services.chatbot.rules import get_rules, default_response
from core.logging_config import get_logger

logger = get_logger(__name__)

class RuleBasedBot:
    def __init__(self):
        self.rules = get_rules()
        logger.info("RuleBasedBot initialized with %d rules", len(self.rules))

    def get_response(self, user_input):
        for pattern, func in self.rules:
            if re.search(pattern, user_input, re.IGNORECASE):
                logger.debug("Rule matched: %s", pattern)
                return func(user_input)
        logger.debug("No rule matched; using default response")
        return default_response(user_input)
