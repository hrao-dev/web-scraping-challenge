#!/usr/bin/env python
# coding: utf-8

# Dependencies
from bs4 import BeautifulSoup
from splinter import Browser
import requests
import pymongo


# Initialize PyMongo to work with MongoDBs
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

# Define database and collection
db = client.mars_db
collection = db.items

def mars_news(browser):
    # #### NASA Mars News

    import time

    # URL of page to be scraped
    news_url = 'https://mars.nasa.gov/news/'
    browser.visit(news_url)
    time.sleep(10)

    # HTML Object
    news_html = browser.html

    # Parse HTML with Beautiful Soup
    news_soup = BeautifulSoup(news_html, 'html.parser')
    #print(news_soup.prettify())

    # Retrieve the element that contains latest news title and paragraph text
    news_results = news_soup.find('div', class_='grid_layout')
    #print(news_results.prettify())

    title_loc = news_results.find('div',class_='content_title')
    #print(title_loc)

    # Scrape the Latest News Title
    news_title = title_loc.find('a').text
    #print("Latest News title: "+news_title)

    # Scrape the Latest Paragraph Text
    news_para_text = news_results.find('div',class_='article_teaser_body').text
    #print("Latest News Paragraph text: "+news_para_text)

    return news_title, news_para_text

def mars_image(browser):
    # #### JPL Mars Space Images - Featured Image

    # URL of page to be scraped
    image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(image_url)

    # HTML Object
    image_html = browser.html

    # Find and click the 'FULL IMAGE' button
    image_button = browser.find_by_id('full_image')

    # Interact with elements
    image_button.click()

    # Find and click the 'more info ' button
    info_button = browser.find_by_text('more info     ')
    info_button.click()

    image_loc = browser.find_by_tag('figure')
    elems = image_loc.find_by_tag('a')
    #elems = b.find_by_tag("a")
    for e in elems:
        featured_image_url = e["href"]
        #print("Latest Featured Image URL: "+featured_image_url)
    return featured_image_url

def mars_weather(browser):
    # #### Mars Weather

    import re

    # URL of page to be scraped
    weather_url = 'https://twitter.com/marswxreport?lang=en'

    # Retrieve page with the requests module
    response = requests.get(weather_url)

    # Create BeautifulSoup object; parse with 'lxml'
    weather_soup = BeautifulSoup(response.text, 'lxml')
    #print(weather_soup.prettify())

    tweets = weather_soup.find('div', class_='tweet')
    #print(tweets.prettify())

    weather_tweet = tweets.find('p', class_ = 'TweetTextSize').text
    if 'sol' and 'pressure' in weather_tweet:
        weather_tweet = re.sub('pic.*', '', weather_tweet)
    else:
        weather_tweet = "Latest weather information not available"
        
    #print("Latest Weather Tweet: "+weather_tweet)
    return weather_tweet

def mars_facts(browser):
 
    # #### Mars Facts

    import pandas as pd

    # URL of page to be scraped
    facts_url = 'https://space-facts.com/mars/'
    facts_table = pd.read_html(facts_url)[0]
    facts_table.columns = ['Description', 'Value']
    #facts_table = facts_table.drop([7,8])
    facts_table = facts_table.set_index('Description')
    facts_html = facts_table.to_html()
    #print(facts_table)
    #print(facts_html)
    return facts_html

def mars_hemi(browser):

    # #### Mars Hemispheres

    from selenium import webdriver

    # URL of page to be scraped
    hemi_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemi_url)

    hrefs = []
    hemi_image_urls = []
    img_link = ""
    hemisphere = {}

    parent_elements = browser.find_by_id('product-section')
    for elem in parent_elements:
        links = elem.find_by_tag('a')
        for l in links:
            if (img_link != l["href"]):
                img_link = l["href"]
                hrefs.append(img_link)
    for href in hrefs:
            browser.visit(href)
            hemi_title = browser.find_by_css('h2').first.text
            img_id = browser.find_by_id('wide-image')
            img_elem = img_id.find_by_tag('a')
            hemi_url= img_elem["href"]
            hemisphere = dict({'title':hemi_title, 'img_url':hemi_url})
            #print(hemisphere)
            hemi_image_urls.append(hemisphere)
    #print(hemi_image_urls)
    return hemi_image_urls

def scrape():
    mars_data = {}
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)
    news_title, news_para = mars_news (browser)
    image = mars_image(browser)
    tweet = mars_weather(browser)
    facts = mars_facts(browser)
    hemi_images = mars_hemi(browser)
    mars_data = {'news_title':news_title,'news_paragraph': news_para,'featured_image':image,'weather':tweet,'facts':facts,'hemispheres':hemi_images}
    
    # Close the browser
    browser.quit()
    return mars_data

if __name__ == "__main__":
    print(scrape())

