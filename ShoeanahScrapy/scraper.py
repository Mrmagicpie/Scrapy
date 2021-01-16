#
#           ShoeanahScrapy scraper.py | 2021 (c) Mrmagicpie
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
import scrapy
from pprint import PrettyPrinter
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
class projectItem(scrapy.item.Item):
    """
    A fancy scrapy project dictionary.
    """
    package            = scrapy.Field()
    version            = scrapy.Field()
    author             = scrapy.Field()
    project_url        = scrapy.Field()
    linkTo             = scrapy.Field()
    description        = scrapy.Field()
    release            = scrapy.Field()
    pip                = scrapy.Field()
    rss                = scrapy.Field()
    short_description  = scrapy.Field()
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
class PyPiScraper(scrapy.Spider):
    """
    The main Scrapy spider class.
    """

    # PPrint because cool.
    pp = PrettyPrinter(indent=4)

    # All scrapy spider names must be unique or it gets confused and might run the wrong one.
    name = "PyPi"

    # PyPi Search value. Not scrapy related.
    search = "discord"

    # start_urls must be a list of urls you want to scrape.
    start_urls = ["https://pypi.org/search/?q=" + search,]

    # Not sure what this does but we have it :KEK:
    sourceIndex = ['Python Package Index',]

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # Try to always start your scraper using a "parse" or "start_request" function
    def parse(self, response):
        """
        Start the request sequence by loading the search page, gathering how many pages in total and then starting the request(s).
        :param response: Basic scrapy request response.
        :return: Returns a sequence of requests.
        """

        # Find number of search results.
        page_numbers = response.xpath('//a[@class="button button-group__button"][3]/text()').extract_first()
        # Turn the str into an int.
        page_numbers = int(page_numbers)
        # Not sure how to do it better at the moment so this keeps track of what page to request.
        number = 0
        # Loop through all the page numbers.
        for page in range(page_numbers):
            number = number + 1
            # Specify the URL to scrape to be used in our request.
            url = "https://pypi.org/search/?q=discord&page=" + f"{number}"
            # Specify the scrapy request, url is our url with page number above, and callback is what function we want
            # to call when we make this request.
            request = scrapy.Request(url, callback=self.parse_two)
            # Yield the request(make the request)
            yield request

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def parse_two(self, response):
        """
        Callback function from parse to deal with each requested page.
        :param response: Basic scrapy request response.
        :return: Returns the first part of our package dictionary.
        """
        # Put all HTML contents into an html file named "response.html".
        # with open("response.html", "w") as f:
        #     f.write(response.text)
        # Using our fancy dictionary class.
        project = projectItem()
        # Find all packages listed on the page.
        package_table = response.xpath("//ul[@aria-label='Search results']/li")
        # Loop through each one to pull information.
        for packages in package_table:
            # Find the package name.
            project['package'] = packages.xpath(".//span[@class='package-snippet__name']/text()").extract_first()
            if self.search in project['package'].lower():
                # Get the current package version from the package block.
                project['version'] = packages.xpath(".//span[@class='package-snippet__version']/text()").extract_first()
                # Find the href link from the block.
                project['linkTo'] = packages.xpath(".//a[@class='package-snippet']/@href").extract_first()
                # Turn it into a usable link for scrapy to use in followLinkTo.
                project['linkTo'] = "https://pypi.org" + project['linkTo']
                # Find the release date of the package.
                project['release'] = packages.xpath(".//time/text()").extract_first().replace("\n", "").strip()
                # Get the short description shown on the search page.
                project['short_description'] = packages.xpath('.//p[@class="package-snippet__description"]/text()').extract_first()
                # self.pp.pprint(project)
                # Form our request using the packages linkTo, specify we want to use followLinkTo for the callback and
                # and send a copy of the current information so we can use it in followLinkTo.
                request = scrapy.Request(project['linkTo'], callback=self.followLinkTo, meta={'item': project.copy()})
                # Yield the request(make the request)
                yield request
            # If the package title does not include your search pass so we don't gather non accurate information.
            else:
                pass

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def followLinkTo(self, response):
        """
        Callback function to sort through the HTML from each packages individual page.
        :param response: Basic scrapy request response.
        :return: Returns the final package dictionary.
        """
        # Redefine our project dictionary using the "parse" callback's version.
        project = response.meta['item']
        # Scrape the package's description.
        project['description'] = response.xpath("//div[@class='project-description']").extract_first()
        # Scrape the package's pip install command.
        project['pip'] = response.xpath("//span[@id='pip-command']/text()").extract_first()
        # Scrape the package's home URL(ex. GitHub or Docs website).
        project['project_url'] = response.xpath("//a[@class='vertical-tabs__tab vertical-tabs__tab--with-icon vertical-tabs__tab--condensed']/@href").extract_first()
        # Scrape the package's RSS feed href.
        project['rss'] = response.xpath('//span[@class="reset-text margin-top"]/a[2]/@href').extract_first()
        # Turn the package's scraped RSS feed into a usable URL.
        project['rss'] = "https://pypi.org" + project['rss']
        # Define where to find the Authors.
        sidebar_author = response.xpath("//div[@class='sidebar-section'][5]/span")
        # Predefine the Authors list to append authors to.
        project['author'] = []
        # Loop over each author in the selection.
        for author in sidebar_author:
            # Find the author's name.
            oop = author.xpath(".//span[@class='sidebar-section__maintainer']/a/span[2]/text()").extract_first()
            # Strip/replace common characters if the author is not None.
            if oop is not None:
                oop = oop.replace("\n", "") \
                    .replace(" ", "")
            # Add the author to the authors list.
            project['author'].append(oop)
        # Print the package to the terminal.
        self.pp.pprint(project)
        # Yield the final request(to be handled by a pipeline or other output)
        yield project

#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
# Don't mind this, blame: https://github.com/ShuanaOnGitHub
# def check_for_big_pp(self, ppcheck):
#     if ppcheck >= 8: # inches
#         print("Uwu, nice pp bro")
#     else:
#         print("no smol pp :W")

#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#