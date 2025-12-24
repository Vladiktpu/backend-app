class BotService:
    def get_response(self, message: str) -> str:
        message = message.lower()
        if "hello" in message or "hi" in message:
            return "Hello! How can I help you today?"
        elif "help" in message:
            return "I am a support bot. You can ask me about our services, pricing, or contact support."
        elif "price" in message or "pricing" in message:
            return "Our basic plan starts at $10/month. Professional plan is $30/month."
        elif "contact" in message:
            return "You can reach us at support@example.com."
        elif "bye" in message:
            return "Goodbye! Have a nice day."
        else:
            return "I'm sorry, I didn't understand that. Could you please rephrase?"

bot_service = BotService()
