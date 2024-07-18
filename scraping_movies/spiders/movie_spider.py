import io
import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
from sentence_transformers import SentenceTransformer


class MoviesSpider(scrapy.Spider):
    name = "movies"

    start_urls = [
        "https://en.wikipedia.org/wiki/Lists_of_films",
    ]

    def parse(self, response):
        all_years = response.css("div.hlist a::text").getall()
        all_years_links = response.css("div.hlist a::attr(href)").getall()

        for year, link in zip(all_years, all_years_links):
            if (
                year.isdigit()
                and int(year) >= self.start_date
                and int(year) <= self.end_date
            ):

                # yield response.follow(link, self.parse_year)
                yield response.follow(link, self.parse_year, meta={"year": year})

        # page = response.url.split("/")[-2]
        # filename = f"quotes-{page}.html"
        # Path(filename).write_bytes(response.body)
        # self.log(f"Saved file {filename}")

    def parse_year(self, response):
        from scrapy.shell import inspect_response

        year = response.meta["year"]
        # inspect_response(response, self)
        h3 = response.xpath("//h3[span[contains(text(), 'By country/region')]]")[0]
        ul = h3.xpath("following-sibling::ul[1]")
        lists = ul.css("li a")
        for list in lists:
            country = (
                list.css("a::text")
                .get()
                .lower()
                .replace("list of", "")
                .replace(f"films of {year}", "")
                .strip()
            )

            if country in self.countries:
                yield response.follow(
                    list.css("a::attr(href)").get(),
                    self.parse_country,
                    meta={"year": year},
                )

    def parse_country(self, response):
        from scrapy.shell import inspect_response

        tables = response.css(
            "table.wikitable.sortable"
        ).getall()  # TODO Maybe just wikitable?
        for table_found in tables:
            t = pd.read_html(io.StringIO(table_found), extract_links="all")
            for table in t:
                # print(table)
                title_column = None
                for idx, col in enumerate(table.columns):
                    if "title" in col[0].lower():
                        title_column = idx

                if title_column is not None:
                    # print(table.iloc[:, title_column].tolist())
                    for row in table.iloc[:, title_column].tolist():  # .tolist())
                        if not isinstance(row, tuple):
                            continue
                        title, link = row
                        if link is not None:
                            yield response.follow(
                                link,
                                self.parse_movie,
                                meta={"title": title, "year": response.meta["year"]},
                            )

            # inspect_response(response, self)
            # inspect_response(response, self)
        # for table in response.css("table.wikitable.sortable"):

        #     rows = table.xpath(".//tr")

        #     title_row = rows[0]
        #     ths = title_row.xpath(".//th")
        #     for idx, th in enumerate(ths):
        #         if "title" in th.xpath("string()").get().lower():
        #             title_column = idx
        #             break

        #     for row in rows[1:]:
        #         tds = row.xpath(".//td")
        #         title = tds[title_column].xpath("string()").get()
        #         print(title)

    def parse_movie(self, response):
        print(response.request.url)
        h2 = response.xpath("//h2[span[contains(text(), 'Plot')]]")
        if h2:
            h2 = h2[0]
            paragraphs = []
            for siblings in ("preceding-sibling", "following-sibling"):
                ps = h2.xpath(f"{siblings}::*")
                if siblings == "preceding-sibling":
                    ps = ps[::-1]

                for p in ps:
                    if (
                        p.root.tag == "h2"
                        or p.root.tag == "h3"
                        or p.root.tag == "h1"
                        or p.root.tag == "div"
                    ):
                        break
                    if p.root.tag == "p":
                        paragraphs.append(
                            "".join(
                                line.strip()
                                for line in p.xpath(".//text()").extract()
                                if line.strip()
                            )
                        )
            text = "\n".join(paragraphs)

            # Get image
            img = response.xpath("//table//img/@src").get()

            # Get embeddings
            model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            embeddings = model.encode([text])

            yield {
                "title": response.meta["title"],
                "year": int(response.meta["year"]),
                "summary": text,
                "img": img,
                "embeddings": embeddings.tolist()[0],
                "url": response.request.url,
            }


if __name__ == "__main__":
    process = CrawlerProcess(
        settings={
            "FEED_FORMAT": "json",
            "FEED_URI": "movies2006.json",
            "FEED_EXPORT_ENCODING": "utf-8",  # Set the encoding to UTF-8
            "LOG_LEVEL": "WARNING",
        }
    )
    process.crawl(
        MoviesSpider,
        start_date=2000,
        end_date=2024,
        countries=["spanish", "american", "british"],
    )
    process.start()
