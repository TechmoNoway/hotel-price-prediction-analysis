from crawlbase import CrawlingAPI
from bs4 import BeautifulSoup
import json


crawling_api = CrawlingAPI({'token': ''})

def fetch_agoda_page(url):
    options = {
        'scroll': 'true',
        'scroll_interval': '100'
    }

    response = crawling_api.get(url, options)
    if response['headers']['pc_status'] == '200':
        return response['body'].decode('utf-8')
    else:
        print("Error fetching the page.")
        return None

def extract_agoda_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    hotels = []

    for hotel in soup.select('div#contentContainer ol.hotel-list-container > li.PropertyCard'):
        name = hotel.select_one('h3[data-selenium="hotel-name"]').text.strip() if hotel.select_one('h3[data-selenium="hotel-name"]') else ''
        price = hotel.select_one('div[data-element-name="final-price"]').text.strip() if hotel.select_one('div[data-element-name="final-price"]') else ''
        rating = hotel.select_one('p[data-element-name="review-score"]').text.strip() if hotel.select_one('p[data-element-name="review-score"]') else ''
        link = hotel.select_one('a.PropertyCard__Link')['href'] if hotel.select_one('a.PropertyCard__Link') else ''
        location = hotel.select_one('button[data-selenium="area-city-text"] span').text.strip() if hotel.select_one('button[data-selenium="area-city-text"] span') else ''
        special_offer = hotel.select_one('div[data-element-name="consolidated-applied-discount-badge"] span').text.strip() if hotel.select_one('div[data-element-name="consolidated-applied-discount-badge"] span') else ''
        review_count = hotel.select_one('div[data-element-name="property-card-review"] + p').text.strip() if hotel.select_one('div[data-element-name="property-card-review"] + p') else ''
        original_price = hotel.select_one('div[data-element-name="first-cor"] span[aria-hidden="true"]').text.strip() if hotel.select_one('div[data-element-name="first-cor"] span[aria-hidden="true"]') else ''
        currency = hotel.select_one('span.PropertyCardPrice__Currency').text.strip() if hotel.select_one('span.PropertyCardPrice__Currency') else False  
        amenities = [span.text.strip() for span in hotel.select('div[data-element-name="pill-each-item"] span')]
        star_rating = hotel.select_one('div[data-testid="rating-container"] .ScreenReaderOnly__ScreenReaderOnlyStyled-sc-szxtre-0').text.strip() if hotel.select_one('div[data-testid="rating-container"] .ScreenReaderOnly__ScreenReaderOnlyStyled-sc-szxtre-0') else ''


        hotels.append({
            'name': name,
            'price': price,
            'rating': rating,
            'link': f"https://www.agoda.com{link}",
            'location': location,
            'special_offer': special_offer,
            'review_count': review_count,
            'original_price': original_price,
            'currency': currency,
            'star_rating': star_rating,
            'amenities': amenities
        })

    return hotels

def save_to_json(data, filename='hotels_data.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=10)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    url = "https://www.agoda.com/search?city=13170&rooms=1&adults=2"
    html_content = fetch_agoda_page(url)

    if html_content:
        hotels_data = extract_agoda_data(html_content)  
        save_to_json(hotels_data)