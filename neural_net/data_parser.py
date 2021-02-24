import requests

from bs4 import BeautifulSoup, Tag

ROOT_URL = "http://www.vatican.va/"
MAIN_URL = f"{ROOT_URL}content/john-paul-ii/pl.html"


def main():
    root_tree = requests.get(MAIN_URL)
    soup = BeautifulSoup(root_tree.text, "html.parser")

    menu_with_data = soup.find(id="accordionmenu")
    subjects_links = _get_subjects_links(menu_with_data)
    text_urls = _get_texts_urls_from_subjects(subjects_links)
    return text_urls


def _get_subjects_links(menu):
    subjects_urls = []
    for item in menu.ul:
        if isinstance(item, Tag):
            if "has-sub" in item.attrs.get("class", []):
                urls = item.find_all("a")
                urls = [u.attrs.get("href", None) for u in urls]
                urls = urls[1:]
            else:
                urls = [item.a.attrs.get("href", None)]
            subjects_urls.extend(urls)
    return subjects_urls


def _get_texts_urls_from_subjects(subjects_links):
    text_urls = []
    for url in subjects_links:
        temp = []
        req = requests.get(ROOT_URL + url)
        sub_soup = BeautifulSoup(req.text, "html.parser")
        data_div = sub_soup.find("div", class_="vaticanindex")
        items = data_div.find_all("div", class_="item")
        for item in items:
            h2_content = item.find("h2")
            langs = h2_content.find_all("a")
            pl_url = (
                filter(lambda x: "/pl/" in x.attrs.get("href", None), langs)
            )
            pl_url = [p.attrs.get("href", None) for p in pl_url]
            temp.extend(pl_url)
        text_urls.extend(temp)
    return text_urls


def extract_text_from_url(urls):
    s = ""
    for url in urls:
        req = requests.get(ROOT_URL + url)
        soup = BeautifulSoup(req.text, "html.parser")
        main_text = soup.find(
            "div", class_="text parbase container vaticanrichtext"
        )
        s += main_text.text.strip("\n")
    return s


if __name__ == "__main__":
    text_urls = main()
    texts = extract_text_from_url(text_urls)
    with open("./data.txt", "w") as f:
        f.write(texts)
