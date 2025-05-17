class ChatHistory:
    def __init__(self):
        self.history = []

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})

    def get_formatted_history(self):
        return "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in self.history])

    def get_all(self):
        return self.history
