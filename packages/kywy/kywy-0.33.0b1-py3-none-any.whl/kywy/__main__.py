import os
import sys
from . import __version__

from kywy.client.kawa_client import KawaClient


def main():
    url = os.getenv("KAWA_URL")
    username = os.getenv("KAWA_USER")
    password = os.getenv("KAWA_PASSWORD")

    print(f"Kywy version: {__version__}")

    if not url or not username or not password:
        print("Variables are missing, silently exiting")
        sys.exit(0)

    kawa_root = KawaClient(url)
    kawa_root.login_with_credential(username, password)

    root_user = kawa_root.get_current_user()
    root_user_email = root_user.get("email")
    print(f'Successfully logged in as {root_user_email}')


if __name__ == "__main__":
    main()
