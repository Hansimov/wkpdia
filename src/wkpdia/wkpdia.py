import requests

from pathlib import Path
from purehtml import purify_html_file
from tclogger import logger

from .constants import USER_AGENT, WIKIPEDIA_URL_ROOT


class WikipediaFetcher:
    def __init__(self, lang="en"):
        self.lang = lang
        self.output_folder = Path(__file__).parents[1] / ".cache" / "wikipedia"

        self.headers = {"User-Agent": USER_AGENT}

    def fetch(self, title, overwrite=False, output_format="markdown"):
        logger.note(f"> Fetching from Wikipedia: [{title}]")
        self.html_path = self.output_folder / f"{title}.html"

        if not overwrite and self.html_path.exists():
            logger.mesg(f"  > HTML exists: {self.html_path}")
            with open(self.html_path, "r", encoding="utf-8") as rf:
                self.html_str = rf.read()
        else:
            self.url = WIKIPEDIA_URL_ROOT + title
            req = requests.get(self.url, headers=self.headers)
            status_code = req.status_code
            if status_code == 200:
                logger.file(f"  - [{status_code}] {self.url}")
                self.html_str = req.text
                self.output_folder.mkdir(parents=True, exist_ok=True)
                with open(self.html_path, "w", encoding="utf-8") as wf:
                    wf.write(self.html_str)
                logger.success(f"  > HTML Saved at: {self.html_path}")
            else:
                if status_code == 404:
                    logger.err(f"{status_code} - Page not found : [{title}]")
                else:
                    logger.err(f"{status_code} Error")
                return (None, None)

        if output_format == "markdown":
            return self.to_markdown(overwrite=overwrite)
        else:
            return {"path": self.html_path, "str": self.html_str}

    def to_markdown(self, overwrite=False):
        self.markdown_path = self.html_path.with_suffix(".md")

        if not overwrite and self.markdown_path.exists():
            logger.mesg(f"  > Markdown exists: {self.markdown_path}")
            with open(self.markdown_path, "r", encoding="utf-8") as rf:
                self.markdown_str = rf.read()
        else:
            self.markdown_str = purify_html_file(self.html_path)
            with open(self.markdown_path, "w", encoding="utf-8") as wf:
                wf.write(self.markdown_str)
            logger.success(f"  > Mardown saved at: {self.markdown_path}")

        return {"path": self.markdown_path, "str": self.markdown_str}


def wkpdia_get(title, overwrite=False, output_format="markdown"):
    fetcher = WikipediaFetcher()
    return fetcher.fetch(title, overwrite=overwrite, output_format=output_format)


if __name__ == "__main__":
    title = "R._Daneel_Olivaw"
    res = wkpdia_get(title, overwrite=True, output_format="markdown")
    path = res["path"]
    content = res["str"]

    logger.file(f"> [{path}]:")
    logger.line(content)
