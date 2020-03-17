import scrapy

def check_perc(pantry,ings):

    retval=0
    for i in range(len(ings)):
        if ings[i]:
            ings[i]=ings[i].lower()

    for supply in pantry:
        for ingredient in ings:
            if ingredient:
                if supply.lower() in ingredient:
                    retval+=1
    if len(ings)>0:
        retval=retval/len(ings)
    return retval

def check(items):
    pantry_file=open('pantry.txt','r')
    pantry=[]
    for supply in pantry_file.readlines():
        supply=supply.strip('\n')
        supply=supply.strip(' ')
        pantry.append(supply)
    pantry_file.close()
    val={}
    for item in items.keys():
        val[item]=check_perc(pantry,items[item])


    return val




class RecipeSpider(scrapy.Spider):
    items={}
    name = "recipe_spider"
    start_urls = ['https://chefsavvy.com/category/main-dish/']

    def parse(self,response):
        SET_SELECTOR = '.griditem'
        for recipe in response.css(SET_SELECTOR):
            url='.//div/header/a/@href'
            url=recipe.xpath(url).get()

            if url:
                yield scrapy.Request(url, callback =self.parse_dir_contents)

            NEXT_PAGE_SELECTOR = '.navfull a ::attr(href)'
            next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
            if next_page:
                yield scrapy.Request(
                    response.urljoin(next_page),
                    callback=self.parse
                )
            NEXT_PAGE_SELECTOR = '.navright a ::attr(href)'
            next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
            if next_page:
                yield scrapy.Request(
                    response.urljoin(next_page),
                    callback=self.parse
                )



    def parse_dir_contents(self,response):
        ingredients=[]
        nam=response.xpath('//title/text()').extract_first()
        for ing in response.css('.wprm-recipe-ingredient'):
            item=ing.xpath('span[@class="wprm-recipe-ingredient-name"]/text()').extract_first()
            ingredients.append(item)
        self.items[nam]=ingredients


    def closed(self, reason):
        foods=check(self.items)
        file=open('Recipe.txt','w')
        best=max(foods.values())
        best_food=list(foods.keys())[list(foods.values()).index(best)]
        file.write("Best recipe for you - {}\n".format(best_food))
        file.write("Ingredients - \n")
        for ing in self.items[best_food]:
            file.write("-{}\n".format(ing))
        file.close()


