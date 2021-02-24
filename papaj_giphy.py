import io
import random
import sys

import bs4
import fbchat
import requests


tags = [
    "jp2",
    "papaj",
    "2137",
    "jp2gmd",
    "vatican",
    "cenzopapa",
    "papiez",
    "papiezak",
    "okrutnik",
]


if __name__ == "__main__":
    session = fbchat.Session.login("woj.warych@gmail.com", "7ZabwZakiecie!")
    client = fbchat.Client(session=session)
    thread = fbchat.Group(session=session, id='1420813071503747')
    listener = fbchat.Listener(session=session, chat_on=False, foreground=False)
    for event in listener.listen():
        if type(event) == fbchat.MessageEvent:
            if event.message.text == "daj papaja":
                url = f"https://tenor.com/search/{random.choice(tags)}-gifs"
                r = requests.get(url)
                soup = bs4.BeautifulSoup(r.text, "html.parser")
                papajs = [
                    i.attrs["src"]
                    for i in soup.find_all("img")
                    if "Gif" in i.parent["class"]
                ]
                gif_r = requests.get(random.choice(papajs))
                files = client.upload([("papaj.gif", gif_r.content, "image/gif")])
                thread.send_files(files)
            if event.message.text == "zamknij się!":
                thread.send_text("Jan Paweł II Zajebał Mi Szlugi. Żegnam!")
                session.logout()
                break
    sys.exit(0)
