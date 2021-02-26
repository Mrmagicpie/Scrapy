#
#                             OhNo scraper.py | 2021 (c) Mrmagicpie
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
from scrapy import Spider
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
class OhNoScraper(Spider):

    name       = "ohno"
    start_urls = [input("Enter your URL: "),]
    count      = 1

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def parse(self, response):
        sel = scrapy.Selector(response)
        results = sel.xpath("//a[contains(@href, '')]/@href")
        for result in results:
            href = result.extract()
            if href.startswith("#"): continue
            elif href.startswith("/") or not href.startswith("http"): href = self.start_urls[0] + href

            yield scrapy.http.Request(
                    url=href,
                    callback=self.parse_two,
                    method="GET"
                )

        print("Final count:" + self.count)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def parse_two(self, response):

        self.count = self.count + 1
        print(self.count)

        sel = scrapy.Selector(response)
        results = sel.xpath("//a[contains(@href, '')]/@href")
        for result in results:
            href = result.extract()
            if href.startswith("https://facebook") \
                    or href.startswith("https://apple"): continue
            elif href.startswith("#"): continue
            elif href.startswith("/"): href = self.start_urls[0] + href
            # time.sleep(0.5)
            yield scrapy.http.Request(
                url=href,
                callback=self.parse_two,
                method="GET"
            )

#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
