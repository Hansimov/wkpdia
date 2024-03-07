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

    def construct_request_params(self, title, proxy=None):
        self.url = WIKIPEDIA_URL_ROOT + title
        requests_params = {
            "url": self.url,
            "headers": self.headers,
            "timeout": 15,
        }
        if proxy:
            requests_params["proxies"] = {"http": proxy, "https": proxy}
        return requests_params

    def fetch(self, title, overwrite=False, output_format="markdown", proxy=None):
        logger.note(f"> Fetching from Wikipedia: [{title}]")
        self.html_path = self.output_folder / f"{title}.html"

        if not overwrite and self.html_path.exists():
            logger.mesg(f"  > HTML exists: {self.html_path}")
            with open(self.html_path, "r", encoding="utf-8") as rf:
                self.html_str = rf.read()
        else:
            requests_params = self.construct_request_params(title=title, proxy=proxy)
            req = requests.get(**requests_params)

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
                    err_msg = f"{status_code} - Page not found : [{title}]"
                else:
                    err_msg = f"{status_code} - Error"
                logger.err(err_msg)
                raise Exception(err_msg)

        if output_format == "markdown":
            return self.to_markdown(overwrite=overwrite)
        else:
            return {"path": self.html_path, "str": self.html_str, "format": "html"}

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

        return {
            "path": self.markdown_path,
            "str": self.markdown_str,
            "format": "markdown",
        }


def wkpdia_get(title, overwrite=False, output_format="markdown", proxy=None):
    fetcher = WikipediaFetcher()
    return fetcher.fetch(
        title, overwrite=overwrite, output_format=output_format, proxy=proxy
    )


if __name__ == "__main__":
    title = "R._Daneel_Olivaw"
    res = wkpdia_get(
        title, overwrite=True, output_format="markdown", proxy="http://127.0.0.1:11111"
    )
    path, content, output_format = res["path"], res["str"], res["format"]

    logger.file(f"> [{output_format}] [{path}]:")
    logger.line(content)
