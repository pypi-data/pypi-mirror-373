import random

class Activity:
    activities = ["Playing Chess", "Listening to Spotify", "Watching YouTube", "Coding Python"]

    @staticmethod
    def set_activity(activity=None):
        if activity:
            print(f"[DiscordEXT] Activity set to: {activity}")
        else:
            print(f"[DiscordEXT] Activity set to: {random.choice(Activity.activities)}")

activity = Activity()
