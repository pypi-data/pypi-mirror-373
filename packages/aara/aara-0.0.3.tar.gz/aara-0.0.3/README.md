# An arXiv Reading App (aara)

A super simple [Textual](https://github.com/Textualize/textual) application for reading the latest posts on the arXiv in the terminal. This scrapes the arXiv "new" page from the category you specify. I found the arXiv search API to be lacking in functionality and the RSS feeds are blank if there was no update that day (e.g. like on a Saturday or Sunday). So, I wrote my own terminal app to read the arXiv.

## Installation

To install:

``` sh
pip install aara
```

For development only (using `uv`):

``` sh
git clone https://github.com/jsnguyen/aara
cd aara
uv run aara astro-ph
```

## Usage

Just run:

``` sh
# For astro-ph
aara astro-ph
```

More generally:

``` sh
aara <arXiv category>
```

## Command Line Arguments

None yet!

## Bindings

Basic vim bindings are implemented, `hjkl`, `g`, `G`, and `{}`. The arrow keys can also be used for navigation. Note that scrolling in abstract window using the vim bindings doesn't work quite yet, but this is a pretty rare occurrence.

`a` opens the abstract of the article using your webbrowser

`s` will open the pdf of the article directly

`q` to quit
