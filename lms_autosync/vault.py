import keyring
import getpass

SERVICE_NAME = "lms-autosync"

def save_credentials():
    username = input("LMS username: ").strip()
    password = getpass.getpass("LMS password: ")
    keyring.set_password(SERVICE_NAME, "username", username)
    keyring.set_password(SERVICE_NAME, username, password)
    print("Credentials saved securely in your OS keychain.")

def get_credentials():
    username = keyring.get_password(SERVICE_NAME, "username")
    if not username:
        raise RuntimeError("No credentials found. Run: python -m lms_autosync.vault")
    password = keyring.get_password(SERVICE_NAME, username)
    return username, password

def clear_credentials():
    username = keyring.get_password(SERVICE_NAME, "username")
    if username:
        keyring.delete_password(SERVICE_NAME, username)
        keyring.delete_password(SERVICE_NAME, "username")
        print("Credentials cleared.")

if __name__ == "__main__":
    save_credentials()