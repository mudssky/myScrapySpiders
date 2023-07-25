import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes3"
    start_urls = [
        "https://quotes.toscrape.com/page/1/",
    ]

    def parse(self, response):
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(),
                "author": quote.css("small.author::text").get(),
                "tags": quote.css("div.tags a.tag::text").getall(),
            }

        # next_page = response.css("li.next a::attr(href)").get()
        # if next_page is not None:
            # next_page = response.urljoin(next_page)
            # yield scrapy.Request(next_page, callback=self.parse)
            # 


        # response.follow直接支持相对 URL - 无需调用 urljoin
        # <a>元素有一个快捷方式：response.follow自动使用它们的 href 属性。
        for href in response.css("ul.pager a::attr(href)"):
            yield response.follow(href, callback=self.parse)

        # 进一步缩短，虽然我认为意义不大了，除非你真的要编写大量爬虫才需要省那么一点时间
        # 不如只记第一个方法，减少记忆的负担。
        # yield from response.follow_all(css="ul.pager a", callback=self.parse)