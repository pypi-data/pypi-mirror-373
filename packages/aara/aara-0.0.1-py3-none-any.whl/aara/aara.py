import argparse

import urllib.request
from bs4 import BeautifulSoup

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, ListView, ListItem, Static
from textual.containers import VerticalGroup, Horizontal, VerticalScroll

def get_arxiv_articles(category):

    url = f"https://arxiv.org/list/{category}/new"

    response = urllib.request.urlopen(url)
    response_text = response.read().decode("utf-8")

    soup = BeautifulSoup(response_text, "html.parser")

    date_content = soup.find('h3', string=lambda s: s and "Showing new listings for" in s)
    date_str = date_content.text.strip()[len("Showing new listings for "):] if date_content else "Date header not found."

    new_articles = soup.find_all('dl')[0]

    dts = new_articles.find_all('dt')
    dds = new_articles.find_all('dd')

    articles = []

    for dt, dd in zip(dts, dds):
        arxiv_id = dt.find('a', title='Abstract')
        arxiv_id = arxiv_id.text.strip().split(':')[1] if arxiv_id else "N/A"

        title = dd.find('div', class_='list-title mathjax')
        title = title.text.replace('Title:', '').strip() if title else "N/A"

        authors = dd.find('div', class_='list-authors')
        authors = authors.text.replace('Authors:', '').strip() if authors else "N/A"

        abstract = dd.find('p', class_='mathjax')
        abstract = abstract.text.strip() if abstract else "N/A"

        comments = dd.find('div', class_='list-comments')
        comments = comments.text.replace('Comments:', '').strip() if comments else ""

        subjects = dd.find('div', class_='list-subjects')
        subjects = subjects.text.replace('Subjects:', '').strip() if subjects else ""

        articles.append({
            "arxiv_id": arxiv_id,
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "comments": comments,
            "subjects": subjects
        })

    return date_str, articles

class AARA(App):
    CSS = """
    Horizontal {
        height: 1fr;
    }
    ListView {
        width: 40%;
        border: solid round #888;
    }
    ListView:focus {
        border: solid round white;
    }
    VerticalScroll#abstract {
        padding: 1 2;
        border: solid round #888;
    }
    VerticalScroll#abstract:focus {
        border: solid round white;
    }
    """

    BINDINGS = [
                ("q", "quit", "Quit"),
                ("{", "jump_five_up()", "Jump Five Up"),
                ("}", "jump_five_down()", "Jump Five Down"),
                ("g", "jump_top()", "Jump to Top"),
                ("G", "jump_bottom()", "Jump to Bottom"),
                ("a", "open_url('abs')", "Open Abstract"),
                ("s", "open_url('pdf')", "Open PDF")
               ]

    def __init__(self, category):
        super().__init__()
        self.category = category
        self.date_str, self.articles = get_arxiv_articles(self.category)

    def compose(self) -> ComposeResult:
        yield Header()

        with VerticalGroup():
            yield Static(f"[dim]{self.category} | {self.date_str} | Total Articles: {len(self.articles)}[/dim]")
        with Horizontal():

            self.list_view = ListView(*[
                ListItem(Static(f"[dim][{i+1:>2}][/dim] [b]{article['title']}[/b]"))
                for i, article in enumerate(self.articles)
            ])
            yield self.list_view

            self.abstract_view = VerticalScroll(Static("Select an article to view its abstract."), id="abstract")
            yield self.abstract_view

        yield Footer()

    def on_mount(self):
        self.list_view.focus()
        if self.articles:
            self.show_abstract(0)

    def show_abstract(self, idx):
        info = self.articles[idx]
        self.abstract_view.children[0].update(
            f"[dim]arxiv:{info['arxiv_id']}[/dim]\n"
            +f"[skyblue][b][u]{info['title']}[/u][/b][/skyblue]\n"
            +f"[khaki]{info['authors']}[/khaki]\n"
            +"\n"
            +f"{info['abstract']}\n"
            +"\n"
            +f"[dim]Comments: {info['comments']}[/dim]\n"
            +f"[dim]Subjects: {info['subjects']}[/dim]"
        )

    def on_resize(self, event):
        self.show_abstract(self.list_view.index)

    def on_list_view_highlighted(self, event):
        self.show_abstract(self.list_view.index)

    def action_open_url(self, urltype):
        arxiv_id = self.articles[self.list_view.index]['arxiv_id']
        arxiv_url = f"https://arxiv.org/{urltype}/{arxiv_id}"
        self.open_url(arxiv_url)

    def action_jump_five_up(self):
        for _ in range(5):
            self.list_view.action_cursor_up()

    def action_jump_five_down(self):
        for _ in range(5):
            self.list_view.action_cursor_down()

    def action_jump_top(self):
        for _ in range(self.list_view.index):
            self.list_view.action_cursor_up()

    def action_jump_bottom(self):
        for _ in range(len(self.articles) - 1 - self.list_view.index):
            self.list_view.action_cursor_down()

    def on_key(self, event):
        if event.key in ("h", "left"):
            self.list_view.focus()
        elif event.key in ("j"):
            if self.list_view.has_focus:
                self.list_view.action_cursor_down()
            elif self.abstract_view.has_focus and self.abstract_view.allow_vertical_scroll:
                self.abstract_view.action_scroll_down()
        elif event.key in ("k"):
            if self.list_view.has_focus:
                self.list_view.action_cursor_up()
            elif self.abstract_view.has_focus and self.abstract_view.allow_vertical_scroll:
                self.abstract_view.action_scroll_up()
        elif event.key in ("l", "right"):
            self.abstract_view.focus()

def main():
    parser = argparse.ArgumentParser(description="ArXiv Article Reader")
    parser.add_argument("category", help="ArXiv category to fetch articles from")
    args = parser.parse_args()

    app = AARA(category=args.category)
    app.run()

if __name__ == "__main__":
    main()