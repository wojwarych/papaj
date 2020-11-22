import getpass
import logging
import os
import sys
import time

from random import randrange, uniform
from datetime import datetime as dt
from multiprocessing import Process

import fbchat

from dotenv import load_dotenv

import cookies


FORMAT = "%(asctime)s %(levelname)s: %(message)s"
logging.basicConfig(
    format=FORMAT,
    filename="/var/log/papiezowa/papiezowa.log",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main_papa(thread, fake=False):
    process = Process(target=bring_papaj, args=(thread, fake,))
    return process


def count_down_the_papaj(thread, fake=False, counter=3):
    if counter == 0:
        return
    if not fake:
        try:
            thread.send_text(f"{counter}...")
        except fbchat.HTTPError:
            time.sleep(uniform(0.5, 2.5))
            return count_down_the_papaj(thread, fake, counter)
    else:
        print(f"{counter}...")
    time.sleep(1)
    return count_down_the_papaj(thread, fake, counter-1)


def bring_papaj(thread, fake=False):
    count_down_the_papaj(thread, fake)
    with open("barka.txt", "r") as f:
        for line in f:
            if not fake:
                try:
                    thread.send_text(line.strip("\n"))
                except fbchat.HTTPError:
                    time.sleep(uniform(8.0, 11.0))
                    thread.send_text(line.strip("\n"))
            else:
                print("{}, {}".format(thread, line.strip("\n")))
            time.sleep(uniform(2.0, 6.0))


def create_fb_threads(sess, sess_types, threads, thread_types):
    chats = []
    for thread, thread_type in zip(threads, thread_types):
        if thread_type == "fake":
            chat = thread
        else:
            chat = sess_types[False] if thread_type != "user" else sess_types[True]
            chat = chat(session=sess, id=thread)
        chats.append(chat)
    return chats


if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] != "env":
            print("Invalid argument. Session aborted")
            sys.exit(1)
        load_dotenv()
        username = os.getenv("CLIENT", None)
        password = os.getenv("PASSWORD", None)
        threads = list(map(int, os.getenv("THREADS", None).split(",")))
        thread_types = os.getenv("THREAD_TYPES", None).split(",")

    try:
        sess_cookies = cookies.load_cookies()
        session = cookies.load_session(sess_cookies)
        if not session:
            session = fbchat.Session.login(username, password)
        sess_types = (fbchat.Group, fbchat.User)
        logger.info("Successfully logged in as {}".format(username))
        client = fbchat.Client(session=session)
        chats = create_fb_threads(session, sess_types, threads, thread_types)
        logger.info(
            "Created chats for %d, %d of type %s, %s", *threads, *thread_types
        )
        processes = [main_papa(c) for c in chats]
        logger.info("Spawning processes to send messages for chats...")
        while True:
            curr_time = dt.now().time().strftime("%H:%M:%S")
            if curr_time  == os.getenv("PAPIEZOWA_TIME"):
                [p.start() for p in processes]
                logger.info(
                    "Successfuly spawned processes, start sending messages"
                )
                [p.join() for p in processes]
                break

        if not all([p.is_alive() for p in processes]):
            logger.info("Successfuly send messages. Logging out")
            cookies.save_cookies(session.get_cookies())
            session.logout()
            logger.info("Done!")
            sys.exit(0)
    except Exception as e:
        logger.error("Error: %s", e)
        sys.exit(1)
        session.logout()
