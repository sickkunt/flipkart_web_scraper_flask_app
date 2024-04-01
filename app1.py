from flask import Flask, render_template, request, redirect, url_for
from bs4 import BeautifulSoup
import requests
import pandas as pd

app = Flask(__name__)

def get_title(soup):
    try:
        title = soup.find("span", class_='B_NuCI')
        title_string = title.text.strip() if title else ""
    except AttributeError:
        title_string = ""
    return title_string

def get_price(soup):
    try:
        price = soup.find("div", class_='_30jeq3._16Jk6d')
        price_value = price.text.strip() if price else ""
    except AttributeError:
        price_value = ""
    return price_value

def get_rating(soup):
    try:
        rating = soup.find("div", class_='_2d4LTz')
        rating_value = rating.text.strip() if rating else ""
    except AttributeError:
        rating_value = ""
    return rating_value

def get_discount(soup):
    try:
        discount = soup.find("div", class_='_1V_ZGU')
        discount_value = discount.text.strip() if discount else ""
    except AttributeError:
        discount_value = ""
    return discount_value

def scrape_flipkart_data(url):
    HEADERS = {'User-Agent': 'Your User Agent Here', 'Accept-Language': 'en-US, en;q=0.5'}
    webpage = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(webpage.content, "html.parser")
    links = soup.find_all("a", class_='_1fQZEK')
    links_list = [link.get('href') for link in links]
    data = {"title": [], "price": [], "rating": [], "discount": []}
    
    for link in links_list:
        new_webpage = requests.get("https://www.flipkart.com" + link, headers=HEADERS)
        new_soup = BeautifulSoup(new_webpage.content, "html.parser")
        data['title'].append(get_title(new_soup))
        data['price'].append(get_price(new_soup))
        data['rating'].append(get_rating(new_soup))
        data['discount'].append(get_discount(new_soup))
    
    flipkart_df = pd.DataFrame(data)
    flipkart_df.dropna(subset=['title'], inplace=True)
    return flipkart_df

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        flipkart_data = scrape_flipkart_data(url)
        flipkart_data.to_csv("flipkart_data.csv", index=False)
        return redirect(url_for('download'))
    return render_template('index.html')

@app.route('/download')
def download():
    return redirect('/static/flipkart_data.csv')

if __name__ == '__main__':
    app.run(debug=True)
