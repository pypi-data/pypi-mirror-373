class Status:
    @staticmethod
    def set_status(status: str):
        allowed = ["online", "idle", "dnd", "invisible"]
        if status.lower() in allowed:
            print(f"[DiscordEXT] Status set to: {status}")
        else:
            print(f"[DiscordEXT] Invalid status. Choose one of {allowed}")

# instance
status = Status()
