import json
from bs4 import BeautifulSoup
from crawlbase import CrawlingAPI
import pandas as pd


crawling_api = CrawlingAPI({"token": "mAxUuT0XAE85j8BokcX2xQ"})


def crawling_data(city_id, city_name, country):
    options = {"scroll": "true", "scroll_interval": "20"}

    response = crawling_api.get(
        f"https://www.agoda.com/search?city={city_id}&rooms=1&adults=2&ds=fFGwJCVBk6LsmuRE",
        options,
    )
    if response["headers"]["pc_status"] == "200":
        soup = BeautifulSoup(response["body"].decode("utf-8"), "html.parser")
        hotels = []
        hotel_cards = soup.select("div[data-selenium='hotel-item']")

        print(hotel_cards)

        # if not hotel_cards:
        #     print("None hotel found, could be blocked.")

        # for card in hotel_cards:
        #     try:
        #         name = card.select_one("h3").get_text(strip=True)
        #         price_elem = card.select_one("[data-selenium='display-price']")
        #         price = (
        #             int(
        #                 price_elem.get_text(strip=True)
        #                 .replace("đ", "")
        #                 .replace(",", "")
        #                 .replace(".", "")
        #             )
        #             if price_elem
        #             else None
        #         )
        #         rating_elem = card.select_one("[data-selenium='review-score']")
        #         rating = (
        #             float(rating_elem.get_text(strip=True)) if rating_elem else None
        #         )
        #         review_elem = card.select_one("[data-selenium='review-count']")
        #         review_count = (
        #             int(
        #                 review_elem.get_text(strip=True)
        #                 .replace("reviews", "")
        #                 .replace("(", "")
        #                 .replace(")", "")
        #                 .strip()
        #             )
        #             if review_elem
        #             else None
        #         )
        #         stars_elem = card.select_one(".PropertyCard__StarRating")
        #         stars = int(stars_elem.get_text(strip=True)[0]) if stars_elem else None
        #         location_elem = card.select_one(".PropertyCard__Location")
        #         location = location_elem.getText(strip=True) if location_elem else ""
        #         content_detail_elem = card.select_one(".PropertyCard__ContentDetail")
        #         content_detail = (
        #             content_detail_elem.getText(strip=True)
        #             if content_detail_elem
        #             else "",
        #         )
        #         link_elem = (card.select_one("a.PropertyCard__Link"),)
        #         link = link_elem["href"] if link_elem else ""

        #         hotels.append(
        #             {
        #                 "hotel_name": name,
        #                 "city": city_name,
        #                 "country": country,
        #                 "price_per_night": price,
        #                 "rating": rating,
        #                 "review_count": review_count,
        #                 "stars": stars,
        #                 "location": location,
        #                 "content": content_detail,
        #                 "link": link,
        #             }
        #         )

        #     except Exception as e:
        #         continue

        #     if len(hotels) >= 30:
        #         break

        return hotels

    else:
        print("Error crawling the page.")
        return None

def save_to_json(data, filename='hotels_data.json'):
    with open(filename, 'w') as f:
        json.dump(data, f)
    print(f"Data saved to {filename}")

def save_to_csv(data, filename='hotels_data.csv'):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"Data saved to {filename}")

def save_to_excel(data, filename='hotels_data.xlsx'):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)

if __name__ == "__main__":
    cities = [
        ("Ho Chi Minh", "Vietnam", "13170"),
        ("Hanoi", "Vietnam", "14484"),
        ("Da Nang", "Vietnam", "14543"),
        ("Tokyo", "Japan", "1868"),
        ("Osaka", "Japan", "1879"),
        ("Kyoto", "Japan", "1889"),
        ("Seoul", "South Korea", "1889"),
        ("Busan", "South Korea", "2213"),
        ("Jeju", "South Korea", "2223"),
    ]

    all_hotels = []

    for city in cities:
        hotels = crawling_data(city_id=city[2], city_name=city[0], country=[1])
        all_hotels.extend(hotels)

    save_to_json(all_hotels)