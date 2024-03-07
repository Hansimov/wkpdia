import requests

from pathlib import Path
from purehtml import purify_html_file
from tclogger import logger


class WikipediaFetcher:
    def __init__(self):
        self.output_root = Path(__file__).parents[1] / ".cache"

    def construct_request_params(self, title, lang="en", proxy=None):
        self.url = f"https://{lang}.wikipedia.org/wiki/{title}"
        requests_params = {
            "url": self.url,
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            },
            "timeout": 15,
        }
        if proxy:
            requests_params["proxies"] = {"http": proxy, "https": proxy}
        return requests_params

    def fetch(
        self,
        title,
        overwrite=False,
        output_format="markdown",
        lang="en",
        proxy=None,
        verbose=False,
    ):
        logger.enter_quiet(not verbose)
        logger.note(f"> Fetching from Wikipedia: [{title}]")
        self.output_folder = self.output_root / f"{lang}-wikipedia"
        self.html_path = self.output_folder / f"{title}.html"
        if not overwrite and self.html_path.exists():
            logger.mesg(f"  > HTML exists: {self.html_path}")
            with open(self.html_path, "r", encoding="utf-8") as rf:
                self.html_str = rf.read()
        else:
            requests_params = self.construct_request_params(
                title=title, lang=lang, proxy=proxy
            )
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
                    err_msg = f"{status_code} - Page not found: ({lang}) [{title}]"
                else:
                    err_msg = f"{status_code} - Error"
                logger.err(err_msg)
                raise ConnectionError(err_msg)

        if output_format == "markdown":
            res = self.to_markdown(overwrite=overwrite)
        else:
            res = {"path": self.html_path, "str": self.html_str, "format": "html"}

        logger.exit_quiet(not verbose)
        return res

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
            logger.success(f"  > Markdown saved at: {self.markdown_path}")

        return {
            "path": self.markdown_path,
            "str": self.markdown_str,
            "format": "markdown",
        }


def wkpdia_get(
    title,
    overwrite=False,
    output_format="markdown",
    lang="en",
    proxy=None,
    verbose=False,
):
    fetcher = WikipediaFetcher()
    return fetcher.fetch(
        title,
        overwrite=overwrite,
        output_format=output_format,
        lang=lang,
        proxy=proxy,
        verbose=verbose,
    )


if __name__ == "__main__":
    title = "R._Daneel_Olivaw"
    res = wkpdia_get(
        title,
        overwrite=True,
        output_format="markdown",
        lang="en",
        proxy="http://127.0.0.1:11111",
        verbose=False,
    )
    path, content, output_format = res["path"], res["str"], res["format"]

    logger.file(f"> [{output_format}] [{path}]:")
    # logger.line(content)
