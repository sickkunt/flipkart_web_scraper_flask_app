from flask import Flask, render_template, request, redirect, url_for, send_file
from bs4 import BeautifulSoup
import requests
import pandas as pd
import os

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
    HEADERS = {'User-Agent': '', 'Accept-Language': 'en-US, en;q=0.5'}
    webpage = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(webpage.content, "html.parser")
    links = soup.find_all("a", class_='_1fQZEK')
    links_list = [link.get('href') for link in links]
    data = {"title": [], "price": [], "rating": [], "discount": []}
    
    for link in links_list:
        new_webpage = requests.get("https://www.flipkart.com" + link, headers=HEADERS)
        new_soup = BeautifulSoup(new_webpage.content, "html.parser")
        data['title'].append(get_title(new_soup))
        
    
    flipkart_df = pd.DataFrame(data)
    flipkart_df.dropna(subset=['title'], inplace=True)
    
   
    static_dir = os.path.join(os.getcwd(), 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    
    csv_path = os.path.join(static_dir, "flipkart_data.csv")
    flipkart_df.to_csv(csv_path, index=False)  
    return csv_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        csv_filename = scrape_flipkart_data(url)
        return redirect(url_for('download', filename=os.path.basename(csv_filename)))  
    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    csv_path = os.path.join("static", filename)
    return send_file(csv_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

