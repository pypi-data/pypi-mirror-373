class Message:
    @staticmethod
    def send_message(channel: str, message: str):
        print(f"[DiscordEXT] Message sent to #{channel}: {message}")

message = Message()
