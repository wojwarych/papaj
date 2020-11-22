import json
import fbchat


def load_cookies():
    try:
        with open("cookies.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return


def save_cookies(cookies):
    with open("cookies.json", "w") as f:
        json.dump(cookies, f)


def load_session(cookies):
    if not cookies:
        return
    try:
        return fbchat.Session.from_cookies(cookies)
    except fbchat.FacebookError:
        return
