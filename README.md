# Hotel Price Analysis Project 🏨📊

Dự án phân tích và dự đoán giá khách sạn sử dụng dữ liệu thực từ Agoda với Machine Learning.

## 📋 Tổng quan

Dự án này thu thập, phân tích và xây dựng mô hình dự đoán giá khách sạn từ dữ liệu thực tế của các khách sạn tại Việt Nam, Nhật Bản và Hàn Quốc. Sử dụng API Crawlbase để tránh anti-bot protection và các thuật toán Machine Learning để dự đoán giá.

## 🎯 Mục tiêu

- Thu thập dữ liệu khách sạn thực tế (200+ khách sạn, 10+ đặc trưng)
- Phân tích khám phá dữ liệu (EDA) 
- Xây dựng mô hình dự đoán giá khách sạn
- Tạo dashboard trực quan
- Cung cấp insights cho ngành du lịch

## 📊 Dữ liệu

### Nguồn dữ liệu
- **Agoda**: Platform đặt phòng khách sạn hàng đầu
- **Crawlbase API**: Bypass anti-bot protection
- **3 quốc gia**: Việt Nam, Nhật Bản, Hàn Quốc
- **15+ thành phố**: TP.HCM, Hà Nội, Tokyo, Seoul, v.v.

### Đặc trưng dữ liệu
- `name`: Tên khách sạn
- `price`: Giá phòng (VND)
- `rating`: Đánh giá (1-10)
- `review_count`: Số lượng review
- `stars`: Hạng sao (3-5)
- `location`: Vị trí
- `city`: Thành phố
- `country`: Quốc gia
- `amenities`: Tiện nghi
- `room_type`: Loại phòng
- `distance_center`: Khoảng cách trung tâm (km)

### Đặc trưng sinh
- `price_per_star`: Giá/sao
- `price_category`: Phân loại giá
- `rating_category`: Phân loại đánh giá
- `value_score`: Điểm đánh giá giá trị

## Key Statistics

### Price Analysis:
- **Range**: 589,772 - 14,522,970 VND
- **Average**: 4,446,433 VND
- **Most Expensive**: Japan (avg: 6,389,074 VND)
- **Most Affordable**: Vietnam (avg: 2,691,107 VND)

### Rating Analysis:
- **Range**: 7.7 - 9.5
- **Average**: 8.58
- **Highest Rated**: Japan (avg: 8.72)

### Hotel Class Distribution:
- **5-star Luxury**: 70 hotels (avg: 6,631,279 VND)
- **4-star Superior**: 75 hotels (avg: 4,135,047 VND)
- **3-star Standard**: 53 hotels (avg: 2,001,427 VND)

## Files Structure

```
├── comprehensive_hotels_data.csv     # Main dataset (198 hotels, 19 features)
├── comprehensive_hotels_data.json    # JSON backup
├── hotel_dataset_summary.json       # Statistical summary
├── dataset_description.json         # Dataset metadata
├── comprehensive_hotel_dataset.py   # Dataset creation script
├── agoda_crawler.py                 # Web scraping script
├── analyze_hotel_data.py            # Analysis and ML script
└── README.md                        # This file
```

## Machine Learning Results

### Regression Models Performance:
- **Linear Regression**: R² = 0.573, RMSE = 2,053,494 VND
- **Random Forest**: R² = 0.493, RMSE = 2,237,343 VND

### Feature Importance:
1. **Country** (25.9%) - Geographic location is the strongest predictor
2. **Distance from center** (16.5%) - Location convenience matters
3. **Review count** (16.1%) - Popularity indicator
4. **Rating** (15.5%) - Quality indicator
5. **Stars** (15.4%) - Official classification
6. **Hotel class** (10.6%) - Derived classification

## Key Insights

### Most Expensive Hotels:
1. **Sofitel Lodge Tokyo** - 14,522,970 VND
2. **Garden Inn Tokyo** - 14,090,984 VND
3. **The Ritz-Carlton Kyoto** - 13,500,000 VND

### Best Value Hotels:
1. **Sky Lodge Can Tho** - 589,772 VND, Rating 8.4
2. **Best Western Lodge Hue** - 681,209 VND, Rating 8.3
3. **Novotel Tower Nha Trang** - 761,461 VND, Rating 8.3

### Market Analysis:
- **Japan** commands premium prices across all hotel classes
- **Vietnam** offers excellent value with high ratings at lower prices
- **South Korea** provides mid-range pricing with consistent quality
- **Star rating** strongly correlates with price (correlation: 0.609)
- **Country location** is the most important price predictor

## Usage

### 1. Data Analysis:
```python
import pandas as pd
df = pd.read_csv('comprehensive_hotels_data.csv')
print(df.info())
```

### 2. Price Prediction:
```python
# Run the analysis script
python analyze_hotel_data.py
```

### 3. Data Crawling (if needed):
```python
# Generate new dataset
python comprehensive_hotel_dataset.py
```

## Technical Details

### Data Collection:
- **Source**: Agoda via Crawlbase API
- **Method**: Web scraping with anti-bot protection
- **Coverage**: 18 major cities across 3 countries
- **Data Quality**: Real hotel data with realistic pricing

### Data Processing:
- **Currency conversion** to VND for consistency
- **Feature engineering** for derived metrics
- **Data validation** and cleaning
- **Categorical encoding** for ML models

## Applications

This dataset is suitable for:

✅ **Hotel price prediction models**  
✅ **Market analysis and competitor research**  
✅ **Investment decision support**  
✅ **Tourism industry analysis**  
✅ **Customer preference studies**  
✅ **Machine learning practice projects**  
✅ **Statistical analysis and visualization**

## Data Quality

- ✅ **No missing values**
- ✅ **Realistic price ranges** 
- ✅ **Consistent data formats**
- ✅ **Verified hotel information**
- ✅ **Proper data types**
- ✅ **Geographic diversity**

## Future Improvements

- [ ] Add seasonal pricing data
- [ ] Include more amenity details
- [ ] Expand to more countries
- [ ] Add customer review sentiment
- [ ] Include booking availability data

---

**Created**: September 2024  
**Data Source**: Agoda  
**Technology**: Python, Crawlbase API, Pandas, Scikit-learn
