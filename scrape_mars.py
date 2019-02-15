# import all dependencies
from splinter import Browser
from bs4 import BeautifulSoup as bs
import time
import pandas as pd


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {'executable_path': 'chromedriver.exe'}  #my path is very different and found this to be an easier way to call the chromedriver
    return Browser("chrome", **executable_path, headless=False)

def scrape_info():
    browser = init_browser()

    url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    browser.visit(url)

    time.sleep(1)

    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")

    news_title = soup.find("div", class_="content_title").text
    avg_temps = soup.find('div', id='weather')
    news_para = soup.findfind("div", class_="article_teaser_body").text
    mars_results["news_title"] = news_title
    mars_results["news_para"] = news_para

    # Featured image
    jpl_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(jpl_url)
    time.sleep(1)

    html = browser.html
    soup = bs(html, 'html.parser')

    # ?????
    featured_img_base = "https://www.jpl.nasa.gov"
    featured_img_url_raw = soup.find("div", class_="carousel_items").find("article")["style"]
    featured_img_url = featured_img_url_raw.split("'")[1]
    featured_img = featured_img_base + featured_img_url

    mars_results["featured_img"] = featured_img

    # Mars weather tweet scraping

    twitter_url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(weather_twitter_url)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # find info on if statements in scraping
    tweets = soup.find("div", class_="stream").find("ol").find_all("li", class_="js-stream-item")
    for tweet in tweets:
        tweet_text = tweet.find("div", class_="js-tweet-text-container").text
        if "Sol " in tweet_text:
                mars_weather = tweet_text.strip()
                break

    mars_results["mars_weather"] = mars_weather

    # Mars facts scraping

    facts_url = "https://space-facts.com/mars/"
    tables = pd.read_html(facts_url)
    time.sleep(1)
    facts_df = tables[0]
    facts_df.columns = ["Fact","Value"]

    facts_df = facts_df.set_index("Fact")
    cleaned_df = facts_df.to_html()
    cleaned_df = cleaned_df.replace('\n', '')
    
    mars_results["cleaned_df"] = cleaned_df

    # Mars hemispheres photo scraping
    base_url = "https://astrogeology.usgs.gov"
    hemisphere_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemisphere_url)

    html = browser.html
    soup = bs(html, 'html.parser')
    
    hemisphere_image_urls = []

    links = soup.find_all("div", class_="item")

    for link in links:
        img_dict = {}
        title = link.find("h3").text
        next_link = link.find("div", class_="description").a["href"]
        full_next_link = base_url + next_link
        
        browser.visit(full_next_link)
        
        pic_html = browser.html
        pic_soup = bs(pic_html, 'html.parser')
        
        url = pic_soup.find("img", class_="wide-image")["src"]

        img_dict["title"] = title
        img_dict["img_url"] = base_url + url
        
        hemisphere_image_urls.append(img_dict)

    mars_results["hemisphere_image_urls"] = hemisphere_image_urls

    return mars_results
