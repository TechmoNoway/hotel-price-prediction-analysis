import json
import pandas as pd
import time
import random
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


def setup_selenium_driver(headless=False):
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument("--headless")
    
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.set_page_load_timeout(60)
    driver.maximize_window()
    
    return driver


def aggressive_scroll_and_load(driver, target_hotels=20, max_attempts=20):
    print(f"Scrolling to load {target_hotels} hotels...")
    
    loaded_count = 0
    attempt = 0
    
    while loaded_count < target_hotels and attempt < max_attempts:
        # Method 1: Progressive scroll
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        scroll_step = scroll_height // 10
        
        for i in range(10):
            scroll_pos = scroll_step * (i + 1)
            driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
            time.sleep(0.5)
        
        # Method 2: End key scrolling
        body = driver.find_element(By.TAG_NAME, "body")
        for _ in range(3):
            body.send_keys(Keys.END)
            time.sleep(1)
        
        # Method 3: JavaScript aggressive loading
        driver.execute_script("""
            // Scroll to bottom multiple times
            for(let i = 0; i < 5; i++) {
                window.scrollTo(0, document.body.scrollHeight);
                // Trigger various events
                window.dispatchEvent(new Event('scroll'));
                window.dispatchEvent(new Event('resize'));
                window.dispatchEvent(new Event('load'));
            }
            
            // Try to find and click load more buttons
            const loadButtons = document.querySelectorAll('[data-selenium="load-more"], .load-more, [aria-label*="load"], [aria-label*="more"]');
            loadButtons.forEach(btn => {
                if(btn.style.display !== 'none') {
                    btn.click();
                }
            });
            
            // Force lazy loading by bringing elements into view
            const cards = document.querySelectorAll('li.PropertyCard');
            cards.forEach(card => {
                card.scrollIntoView({ behavior: 'smooth', block: 'center' });
            });
        """)
        
        time.sleep(random.uniform(3, 5))
        
        current_hotels = driver.find_elements(By.CSS_SELECTOR, "li.PropertyCard")
        current_count = len(current_hotels)
        
        print(f"Attempt {attempt + 1}: Found {current_count} hotel elements")
        
        if current_count > loaded_count:
            loaded_count = current_count
            if attempt > 5:
                attempt = max(0, attempt - 2)
        
        attempt += 1
        
        if loaded_count >= target_hotels:
            print(f"Success! Found {loaded_count} hotels (target: {target_hotels})")
            break
    
    print(f"Result: {loaded_count} hotel elements loaded after {attempt} attempts")
    return loaded_count


def crawling_data_aggressive(driver, city_id, city_name, country, max_hotels=20):
    print(f"\n=== Aggressive Crawling {city_name}, {country} (ID: {city_id}) ===")
    
    url = f"https://www.agoda.com/search?city={city_id}&rooms=1&adults=2&ds=fFGwJCVBk6LsmuRE"
    
    try:
        print(f"Loading URL: {url}")
        driver.get(url)
        
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.PropertyCard"))
            )
            print("Initial hotels loaded")
        except Exception as e:
            print(f"Hotels failed to load: {e}")
            return []
        
        time.sleep(5)
        
        initial_hotels = driver.find_elements(By.CSS_SELECTOR, "li.PropertyCard")
        print(f"Initial hotel count: {len(initial_hotels)}")
        
        aggressive_scroll_and_load(driver, max_hotels)
        
        print("Final page stabilization...")
        time.sleep(5)
        
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        
        hotel_cards = soup.select('li.PropertyCard')
        print(f"📄 Hotel cards in HTML: {len(hotel_cards)}")
        
        if not hotel_cards:
            print("No hotel cards found in HTML")
            return []

        hotels = []
        extracted_count = 0
        
        for i, hotel in enumerate(hotel_cards):
            if extracted_count >= max_hotels:
                break
                
            try:
                name_selectors = [
                    'h3[data-selenium="hotel-name"]',
                    'h3',
                    '.PropertyCard__HotelName',
                    '[data-testid="property-card-name"]',
                    '.PropertyCard h3',
                    '.hotel-name',
                    '[data-selenium="hotel-name"]'
                ]
                
                name = ''
                for selector in name_selectors:
                    name_elem = hotel.select_one(selector)
                    if name_elem:
                        name = name_elem.text.strip()
                        break
                
                price_selectors = [
                    'div[data-element-name="final-price"]',
                    '[data-selenium="display-price"]',
                    '.PropertyCardPrice__Value',
                    '[data-testid="property-card-price"]',
                    '.PropertyCard__Price',
                    '.price',
                    '[data-price]',
                    '.PropertyCardPrice span'
                ]
                
                price_text = ''
                for selector in price_selectors:
                    price_elem = hotel.select_one(selector)
                    if price_elem:
                        price_text = price_elem.text.strip()
                        break
                
                if not price_text:
                    currency_elems = hotel.select('*')
                    for elem in currency_elems:
                        text = elem.text.strip()
                        if '₫' in text or 'VND' in text or 'đ' in text:
                            if re.search(r'\d+', text):
                                price_text = text
                                break
                
                if not name or not price_text:
                    if i < 10:
                        print(f"Hotel {i+1}: name='{name[:20]}' price='{price_text[:20]}' - SKIPPED")
                    continue
                
                price_numeric = None
                if price_text:
                    price_numbers = re.findall(r'[\d,.]+', price_text.replace('₫', '').replace('đ', ''))
                    if price_numbers:
                        try:
                            price_numeric = int(price_numbers[0].replace(',', '').replace('.', ''))
                        except ValueError:
                            pass
                
                rating_text = ''
                rating_score = ''
                
                # Method 1: Look for rating in property-card-review section
                review_section = hotel.select_one('[data-element-name="property-card-review"]')
                if review_section:
                    score_elem = review_section.select_one('span.jqsyMk, span[class*="jqsyMk"]')
                    if score_elem:
                        rating_score = score_elem.text.strip()
                    
                    text_elem = review_section.select_one('span.fmebpQ, span[class*="fmebpQ"]')
                    if text_elem:
                        rating_text = text_elem.text.strip()
                    
                    if rating_score and rating_text:
                        rating_text = f"{rating_score} {rating_text}"
                    elif rating_score:
                        rating_text = rating_score
                
                # Method 2: Fallback to ReviewWithDemographic
                if not rating_text:
                    review_demo = hotel.select_one('.ReviewWithDemographic p')
                    if review_demo:
                        demo_text = review_demo.text.strip()
                        if demo_text:
                            rating_text = demo_text
                
                stars = None
                star_selectors = ['div[data-testid="rating-container"]', '.stars', '.PropertyCard__StarRating']
                for selector in star_selectors:
                    elem = hotel.select_one(selector)
                    if elem:
                        star_match = re.search(r'(\d+)', elem.text)
                        if star_match:
                            stars = int(star_match.group(1))
                            break
                
                location = ''
                location_selectors = ['button[data-selenium="area-city-text"] span', '.PropertyCard__Location']
                for selector in location_selectors:
                    elem = hotel.select_one(selector)
                    if elem:
                        location = elem.text.strip()
                        break
                
                review_count_text = ''
                review_count_number = None
                
                # Method 1: Look in ReviewWithDemographic section
                review_demo = hotel.select_one('.ReviewWithDemographic')
                if review_demo:
                    demo_text = review_demo.get_text()
                    review_matches = re.findall(r'(\d{1,3}(?:,\d{3})*)\s+reviews?', demo_text, re.IGNORECASE)
                    if review_matches:
                        review_count_text = f"{review_matches[0]} reviews"
                        try:
                            review_count_number = int(review_matches[0].replace(',', ''))
                        except ValueError:
                            pass
                
                # Method 2: Fallback selectors if Method 1 fails
                if not review_count_text:
                    review_count_selectors = [
                        'p[aria-hidden="true"]',
                        '.ReviewWithDemographic p:last-child'
                    ]
                    for selector in review_count_selectors:
                        elem = hotel.select_one(selector)
                        if elem and 'review' in elem.text:
                            review_count_text = elem.text.strip()
                            review_matches = re.findall(r'(\d{1,3}(?:,\d{3})*)\s+reviews?', review_count_text, re.IGNORECASE)
                            if review_matches:
                                try:
                                    review_count_number = int(review_matches[0].replace(',', ''))
                                except ValueError:
                                    pass
                            break
                
                amenities = []
                amenity_elems = hotel.select('div[data-element-name="pill-each-item"] span')
                amenities = [elem.text.strip() for elem in amenity_elems if elem.text.strip()]
                
                hotel_data = {
                    "hotel_name": name,
                    "city": city_name,
                    "country": country,
                    "price_per_night_text": price_text,
                    "price_per_night": price_numeric,
                    "rating": rating_text,
                    "review_count_text": review_count_text,  
                    "review_count": review_count_number,   
                    "stars": stars,
                    "location": location,
                    "amenities": amenities,
                }

                hotels.append(hotel_data)
                extracted_count += 1
                
                review_status = f"({review_count_number} reviews)" if review_count_number else "(no reviews)"
                print(f"Hotel {extracted_count}: {name[:35]} - {rating_text} - {review_status}")

            except Exception as e:
                print(f"Error extracting hotel {i+1}: {e}")
                continue

        print(f"Successfully extracted {len(hotels)} hotels from {city_name}")
        return hotels

    except Exception as e:
        print(f"Error: {e}")
        return []


def save_to_json(data, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"JSON saved to {filename}")
    except Exception as e:
        print(f"Error saving JSON: {e}")


def save_to_csv(data, filename):
    try:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"CSV saved to {filename}")
    except Exception as e:
        print(f"Error saving CSV: {e}")


def aggressive_crawl_cities(cities_list, headless=False, delay_range=(10, 20)):
    all_hotels = []
    successful_cities = 0
    failed_cities = 0
    driver = None
    
    print("AGGRESSIVE SELENIUM CRAWLER - FINAL VERSION")
    print(f"Headless mode: {headless} (Recommended: False for better results)")
    print("Target: 20 hotels per city")
    
    try:
        driver = setup_selenium_driver(headless=headless)
        
        for i, (city_name, country, city_id) in enumerate(cities_list):
            try:
                print(f"\nProgress: {i+1}/{len(cities_list)} cities")
                
                hotels = crawling_data_aggressive(driver, city_id, city_name, country, max_hotels=20)
                
                if hotels and len(hotels) > 0:
                    all_hotels.extend(hotels)
                    successful_cities += 1
                    print(f"{city_name}: {len(hotels)} hotels collected")
                else:
                    failed_cities += 1
                    print(f"{city_name}: No hotels collected")
                
                if i < len(cities_list) - 1:
                    delay = random.uniform(delay_range[0], delay_range[1])
                    print(f"💤 Waiting {delay:.1f}s before next city...")
                    time.sleep(delay)
                    
            except KeyboardInterrupt:
                print(f"\nInterrupted after {i+1} cities")
                break
            except Exception as e:
                failed_cities += 1
                print(f"Error with {city_name}: {e}")
                continue
        
    finally:
        if driver:
            driver.quit()
            print("Browser closed")
    
    print("\nFINAL RESULTS")
    print(f"Successful cities: {successful_cities}")
    print(f"Failed cities: {failed_cities}")
    print(f"Total hotels: {len(all_hotels)}")
    
    return all_hotels


if __name__ == "__main__":
    cities = [
        ("Ho Chi Minh", "Vietnam", "13170"),
        ("Hanoi", "Vietnam", "2758"),
        ("Da Nang", "Vietnam", "16440"),
        ("Nha Trang", "Vietnam", "2679"),
        ("Hoi An", "Vietnam", "16552"),
        ("Phu Quoc", "Vietnam", "17188"),
        ("Sapa", "Vietnam", "17160"),
        ("Phan Thiet", "Vietnam", "16264"),
        ("Dalat", "Vietnam", "15932"),
        ("Hue", "Vietnam", "3738"),
    ]
    
    print("VIETNAM HOTEL CRAWLER - FINAL 10 CITIES")
    print("This will open a visible browser window")
    print("Close browser manually to stop crawling")
    print("Estimated time: 30-45 minutes for all 10 cities")
    
    all_hotels = aggressive_crawl_cities(
        cities, 
        headless=False,  
        delay_range=(12, 20)  
    )
    
    if all_hotels:
        print("\nSaving final results...")
        save_to_json(all_hotels, 'vietnam_hotels_data.json')
        save_to_csv(all_hotels, 'vietnam_hotels_data.csv')
              
        city_counts = {}
        for hotel in all_hotels:
            city = hotel['city']
            city_counts[city] = city_counts.get(city, 0) + 1
        
        print("\nHotels by city (Final Results):")
        for city, count in city_counts.items():
            print(f"  {city}: {count} hotels")
            
        prices = [h['price_per_night'] for h in all_hotels if h['price_per_night']]
        if prices:
            print(f"\nPrice statistics:")
            print(f"  Cheapest: ₫{min(prices):,}")
            print(f"  Most expensive: ₫{max(prices):,}")
            print(f"  Average: ₫{sum(prices)//len(prices):,}")
        
        print(f"\nFINAL SUCCESS: {len(all_hotels)} hotels from {len(set(h['city'] for h in all_hotels))} cities!")
    else:
        print("No data collected!")