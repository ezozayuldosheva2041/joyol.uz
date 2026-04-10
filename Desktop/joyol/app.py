from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.secret_key = 'joyol-secret-key-2026'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///joyol.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth'
login_manager.login_message = ''

# ===== MODELS =====

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reservations = db.relationship('Reservation', backref='user', lazy=True)

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cuisine = db.Column(db.String(100))
    description = db.Column(db.Text)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    image_url = db.Column(db.String(300))
    price_range = db.Column(db.String(50))
    rating = db.Column(db.Float, default=0.0)
    capacity = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    reservations = db.relationship('Reservation', backref='restaurant', lazy=True)
    reviews = db.relationship('Review', backref='restaurant', lazy=True)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(10), nullable=False)
    guests = db.Column(db.Integer, nullable=False)
    occasion = db.Column(db.String(50))
    special_request = db.Column(db.Text)
    status = db.Column(db.String(20), default='confirmed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='user_reviews', lazy=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ===== SEED DATA =====

def seed_restaurants():
    if Restaurant.query.count() > 0:
        return
    restaurants = [
        Restaurant(name="Afsona Restaurant", cuisine="Uzbek", description="Modern Uzbek cuisine with traditional ornaments and an open tandoor kitchen. One of Tashkent's most beloved fine dining spots.", address="Toshkent ko'chasi 4, Yunusobod", phone="+998 71 252 56 81", image_url="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&q=80", price_range="$$$", rating=4.9, capacity=120),
        Restaurant(name="Caravan Restaurant", cuisine="Uzbek", description="Tashkent's first and most iconic restaurant. Cozy Silk Road caravanserai atmosphere with authentic Uzbek and international dishes.", address="A. Qahhor ko'chasi 22, Mirzo Ulugbek", phone="+998 71 150 66 06", image_url="https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=600&q=80", price_range="$$", rating=4.8, capacity=200),
        Restaurant(name="Besh Qozon Pilaf Center", cuisine="Uzbek", description="Famous for Tashkent's best plov cooked in giant open kazan pots. A true local institution — arrive early before it sells out.", address="Shayxontohur tumani, Chilonzor", phone="+998 71 246 00 01", image_url="https://images.unsplash.com/photo-1544148103-0773bf10d330?w=600&q=80", price_range="$", rating=4.9, capacity=300),
        Restaurant(name="Syrovarnya", cuisine="Italian", description="Industrial-chic Italian restaurant where you can watch mozzarella and burrata being made fresh. Extensive wine list and wood-fired pizza.", address="Shota Rustaveli ko'chasi 5, Yakkasaroy", phone="+998 71 200 01 01", image_url="https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&q=80", price_range="$$$", rating=4.7, capacity=150),
        Restaurant(name="Jumanji Restaurant", cuisine="Asian Fusion", description="One of Tashkent's oldest restaurants with 20+ years of history. Massive menu spanning Uzbek, Chinese, Japanese and international dishes.", address="Yusuf Xos Hojib ko'chasi 62/2, Yunusobod", phone="+998 88 133 44 22", image_url="https://images.unsplash.com/photo-1559339352-11d035aa65de?w=600&q=80", price_range="$$$", rating=4.6, capacity=180),
        Restaurant(name="City Grill New", cuisine="European", description="Elegant steakhouse in the city centre with laconic decor and premium meat dishes. Famous for City Grill steak and grilled fish.", address="Shahrisabz ko'chasi 23, Mirzo Ulugbek", phone="+998 90 977 71 16", image_url="https://images.unsplash.com/photo-1466978913421-dad2ebd01d17?w=600&q=80", price_range="$$$$", rating=4.7, capacity=100),
        Restaurant(name="Gruzinskiy Dvorik", cuisine="Georgian", description="Warm Georgian hospitality with authentic khinkali, khachapuri and chakapuli. Art-adorned walls and generous portions make it a favourite.", address="Taras Shevchenko ko'chasi 28, Mirzo Ulugbek", phone="+998 71 252 00 28", image_url="https://images.unsplash.com/photo-1551632436-cbf8dd35adfa?w=600&q=80", price_range="$$", rating=4.8, capacity=140),
        Restaurant(name="Sette Restaurant", cuisine="Italian", description="Fine Italian dining on the 7th floor of Hyatt Regency with panoramic Tashkent views. Chef from Turin, authentic recipes, sunset terrace.", address="Hyatt Regency, Navoi ko'chasi 1A, Mirzo Ulugbek", phone="+998 71 207 12 34", image_url="https://images.unsplash.com/photo-1424847651672-bf20a4b0982b?w=600&q=80", price_range="$$$$", rating=4.8, capacity=80),
        Restaurant(name="Basilic Restaurant", cuisine="European", description="Beautiful courtyard restaurant serving Mediterranean and Italian cuisine. Known for veal with porcini mushrooms and duck magret.", address="Abdulla Qodiriy ko'chasi 14, Yakkasaroy", phone="+998 71 252 30 32", image_url="https://images.unsplash.com/photo-1537047902294-62a40c20a6ae?w=600&q=80", price_range="$$$", rating=4.7, capacity=90),
        Restaurant(name="Navat Restaurant", cuisine="Uzbek", description="Modern Central Asian restaurant chain with contemporary twists on traditional plov, shashlik and lagman. Popular among locals and tourists.", address="Amir Temur xiyoboni 7, Shayxontohur", phone="+998 71 200 02 02", image_url="https://images.unsplash.com/photo-1544025162-d76694265947?w=600&q=80", price_range="$$", rating=4.6, capacity=160),
        Restaurant(name="Affresco Restaurant", cuisine="Italian", description="Tashkent's best Italian restaurant with authentic regional recipes. Excellent handmade pasta, Neapolitan pizza and a curated Italian wine list.", address="Mirzo Ulugbek tumani, Chilonzor", phone="+998 71 246 50 50", image_url="https://images.unsplash.com/photo-1498579150354-977475b7ea0b?w=600&q=80", price_range="$$$", rating=4.8, capacity=110),
        Restaurant(name="Forn Lebnen", cuisine="Middle Eastern", description="Authentic Lebanese and Middle Eastern cuisine opened in 2020. Famous for hummus, shawarma, falafel, baba ghanoush and fresh pita.", address="Shota Rustaveli ko'chasi 12, Yakkasaroy", phone="+998 90 311 22 33", image_url="https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600&q=80", price_range="$$", rating=4.7, capacity=80),
        Restaurant(name="Khan Chapan", cuisine="Uzbek", description="Traditional Uzbek restaurant with authentic cultural atmosphere. Plov, shashlik, samsa and soups in a setting that reflects Uzbek heritage.", address="Yunusobod tumani, Yunusobod", phone="+998 71 267 00 67", image_url="https://images.unsplash.com/photo-1482275548304-a58859dc31b7?w=600&q=80", price_range="$$", rating=4.6, capacity=200),
        Restaurant(name="Sultan Saray", cuisine="Uzbek", description="Late-night plov institution — every night at 11pm the chef prepares fresh Uzbek plov. Also serves European dishes, BBQ and pizza.", address="Chorsu maydoni yaqin, Shayxontohur", phone="+998 71 244 00 44", image_url="https://images.unsplash.com/photo-1555244162-803834f70033?w=600&q=80", price_range="$$", rating=4.5, capacity=250),
        Restaurant(name="Tandiriy Restaurant", cuisine="Uzbek", description="Refined gastronomic destination with tandoor-roasted lamb, hot samsas and Tashkent wedding plov. Harmonious blend of tradition and modern design.", address="Furkat ko'chasi 2A, Tashkent City Boulevard", phone="+998 88 100 22 55", image_url="https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=600&q=80", price_range="$$$", rating=4.7, capacity=120),
        Restaurant(name="Plov Lounge & Banquet Hall", cuisine="Uzbek", description="Sophisticated plov dining near Alay Bazaar. Elevated Uzbek cuisine with grilled sturgeon and oven-baked beef ribs alongside classic plov.", address="Abdulla Qodiriy ko'chasi 25, Mirzo Ulugbek", phone="+998 71 241 25 25", image_url="https://images.unsplash.com/photo-1563245372-f21724e3856d?w=600&q=80", price_range="$$$", rating=4.6, capacity=180),
        Restaurant(name="L'Opera Ristorante", cuisine="Italian", description="A haven for Italian food lovers with premium ingredients and modern interior. Perfect for romantic dinners with authentic pasta and risotto.", address="Amir Temur ko'chasi 20, Mirzo Ulugbek", phone="+998 71 207 20 20", image_url="https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&q=80", price_range="$$$$", rating=4.8, capacity=70),
        Restaurant(name="Kaspiyka Seafood", cuisine="Seafood", description="Tashkent's favourite seafood restaurant with a fresh marine-inspired menu. Guests can also purchase fresh seafood to take home.", address="Yunusobod ko'chasi 15, Yunusobod", phone="+998 71 267 15 15", image_url="https://images.unsplash.com/photo-1559339352-11d035aa65de?w=600&q=80", price_range="$$$", rating=4.6, capacity=100),
        Restaurant(name="Restaurant 12", cuisine="European", description="Stylish restaurant on the 12th floor with stunning panoramic views of Tashkent. Modern interpretations of European and Pan-Asian cuisines.", address="Navoiy ko'chasi 1, Mirzo Ulugbek", phone="+998 71 207 12 00", image_url="https://images.unsplash.com/photo-1424847651672-bf20a4b0982b?w=600&q=80", price_range="$$$$", rating=4.7, capacity=90),
        Restaurant(name="Bosphorus Qorasaroy", cuisine="Turkish", description="Authentic Turkish restaurant welcoming families of all ages. From menemen for breakfast to pide flatbread for dinner. Has a children's playground.", address="Qorasaroy ko'chasi 8, Chilonzor", phone="+998 71 276 80 80", image_url="https://images.unsplash.com/photo-1466978913421-dad2ebd01d17?w=600&q=80", price_range="$$", rating=4.5, capacity=160),
        Restaurant(name="SEZAM Turkish Restaurant", cuisine="Turkish", description="Large Turkish restaurant with open-air and indoor seating including a dedicated kids' floor. Great for family outings with authentic Turkish cuisine.", address="Mirzo Ulugbek ko'chasi 55, Mirzo Ulugbek", phone="+998 71 268 55 55", image_url="https://images.unsplash.com/photo-1544025162-d76694265947?w=600&q=80", price_range="$$", rating=4.5, capacity=220),
        Restaurant(name="MANDU Dumpling House", cuisine="Uzbek", description="Tashkent's most beloved manti specialist — large wooden steamers cook handmade dumplings served with cream sauce. Locals say it's the best.", address="Mirabad tumani, Mirabad", phone="+998 71 233 22 22", image_url="https://images.unsplash.com/photo-1563245372-f21724e3856d?w=600&q=80", price_range="$", rating=4.7, capacity=60),
        Restaurant(name="Lali Restaurant", cuisine="Uzbek", description="Created by renowned restaurateur Arkady Novikov, Lali showcases Uzbekistan's rich culinary heritage in a stunning contemporary setting.", address="Amir Temur xiyoboni 3, Shayxontohur", phone="+998 71 200 10 10", image_url="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&q=80", price_range="$$$$", rating=4.9, capacity=100),
        Restaurant(name="Silk 96 Wine & Lounge", cuisine="European", description="Sophisticated wine lounge known for its large wine list, shisha and cozy atmosphere. Famous for burrata with nuts and crispy eggplant salad.", address="Shota Rustaveli ko'chasi 96, Yakkasaroy", phone="+998 71 252 96 96", image_url="https://images.unsplash.com/photo-1551632436-cbf8dd35adfa?w=600&q=80", price_range="$$$", rating=4.6, capacity=80),
        Restaurant(name="Navvat Lounge Bar", cuisine="European", description="Relaxed atmosphere with wide selection of craft cocktails, shisha and light bites. Perfect for evening outings and celebrations with friends.", address="Yunusobod 14-mavze, Yunusobod", phone="+998 71 268 14 14", image_url="https://images.unsplash.com/photo-1537047902294-62a40c20a6ae?w=600&q=80", price_range="$$", rating=4.5, capacity=100),
        Restaurant(name="Eco Café Tashkent", cuisine="Vegetarian", description="Tashkent's favourite vegan and vegetarian café. Vegan plov, manti, lagman and samsa. Also serves protein bowls, avocado toast and pita rolls.", address="Mirzo Ulugbek ko'chasi 45, Mirzo Ulugbek", phone="+998 90 300 45 45", image_url="https://images.unsplash.com/photo-1498579150354-977475b7ea0b?w=600&q=80", price_range="$", rating=4.6, capacity=50),
        Restaurant(name="Qanotchi Steakhouse", cuisine="Steakhouse", description="Premium Tashkent steakhouse with a wide range of Uzbek meat dishes, craft salads, and excellent beef and lamb cuts. Beer and wine available.", address="Chilonzor tumani, Chilonzor", phone="+998 71 276 10 10", image_url="https://images.unsplash.com/photo-1466978913421-dad2ebd01d17?w=600&q=80", price_range="$$$", rating=4.6, capacity=90),
        Restaurant(name="Tarnovboshi Restaurant", cuisine="Uzbek", description="Popular meat specialist with incredible lamb chops, fish, skewers and plov. Serves breakfast, lunch, brunch and dinner. Great for groups.", address="Shayxontohur ko'chasi 18, Shayxontohur", phone="+998 71 244 18 18", image_url="https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600&q=80", price_range="$$", rating=4.6, capacity=170),
        Restaurant(name="Karimbek Restaurant", cuisine="Uzbek", description="Well-regarded Tashkent restaurant known for grilled beef and lamb dishes, diverse menu and excellent outdoor seating. Suitable for families.", address="Yunusobod 20-mavze, Yunusobod", phone="+998 71 267 20 20", image_url="https://images.unsplash.com/photo-1555244162-803834f70033?w=600&q=80", price_range="$$", rating=4.5, capacity=150),
        Restaurant(name="Cafe 1991", cuisine="Middle Eastern", description="Lebanese and broader Middle Eastern cuisine in a cosy setting. Central Asian fusion dishes alongside classics like hummus, tabbouleh and shawarma.", address="Amir Temur ko'chasi 33, Mirzo Ulugbek", phone="+998 71 236 19 91", image_url="https://images.unsplash.com/photo-1559339352-11d035aa65de?w=600&q=80", price_range="$$", rating=4.5, capacity=70),
        Restaurant(name="Bon! French Café", cuisine="French", description="Chain of cozy French coffeehouses in central Tashkent. Famous for Getano ice cream, fresh croissants and expertly brewed coffee from early morning.", address="Usmon Nosir ko'chasi 63, Yakkasaroy", phone="+998 71 200 03 43", image_url="https://images.unsplash.com/photo-1482275548304-a58859dc31b7?w=600&q=80", price_range="$$", rating=4.7, capacity=60),
        Restaurant(name="Brasserie Tashkent", cuisine="European", description="Chic and stylish European brasserie perfect for casual meals or special occasions. Diverse menu with salads, grills and European classics.", address="Mirzo Ulugbek ko'chasi 12, Mirzo Ulugbek", phone="+998 71 268 12 50", image_url="https://images.unsplash.com/photo-1424847651672-bf20a4b0982b?w=600&q=80", price_range="$$$", rating=4.5, capacity=90),
        Restaurant(name="MONA Restaurant & Lounge", cuisine="European", description="Elegant dining combined with vibrant nightlife. Gourmet cuisine, stylish contemporary decor and a sophisticated lounge bar experience.", address="Navoiy ko'chasi 9, Mirzo Ulugbek", phone="+998 71 207 09 09", image_url="https://images.unsplash.com/photo-1537047902294-62a40c20a6ae?w=600&q=80", price_range="$$$$", rating=4.6, capacity=120),
        Restaurant(name="ALFA & Bakery", cuisine="Korean", description="Surprisingly authentic Korean food in Tashkent. Famous for kimbap, tteokbokki and the signature dakjuk chicken porridge. Bakery on site.", address="Shota Rustaveli ko'chasi 30, Yakkasaroy", phone="+998 71 252 30 30", image_url="https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=600&q=80", price_range="$$", rating=4.7, capacity=60),
        Restaurant(name="Prime Steakhouse", cuisine="Steakhouse", description="Tashkent's premier steakhouse with a brazier placed in the centre of the restaurant so guests can watch steaks cook over open fire.", address="Amir Temur xiyoboni 15, Shayxontohur", phone="+998 71 200 15 15", image_url="https://images.unsplash.com/photo-1466978913421-dad2ebd01d17?w=600&q=80", price_range="$$$$", rating=4.8, capacity=80),
        Restaurant(name="Furusato Japanese", cuisine="Japanese", description="Authentic Japanese restaurant with fresh sushi, sashimi, ramen and teppanyaki. Tashkent's top destination for Japanese cuisine lovers.", address="Yunusobod 11-mavze, Yunusobod", phone="+998 71 267 11 11", image_url="https://images.unsplash.com/photo-1544025162-d76694265947?w=600&q=80", price_range="$$$", rating=4.7, capacity=70),
        Restaurant(name="Dragon Palace", cuisine="Chinese", description="Elegant Chinese restaurant with classic dim sum, Peking duck and Sichuan dishes. The most authentic Chinese dining experience in Tashkent.", address="Mirzo Ulugbek ko'chasi 88, Mirzo Ulugbek", phone="+998 71 268 88 88", image_url="https://images.unsplash.com/photo-1563245372-f21724e3856d?w=600&q=80", price_range="$$$", rating=4.5, capacity=130),
        Restaurant(name="Samarkand Terrace", cuisine="Uzbek", description="Open-air terrace restaurant serving traditional Samarkand-style plov, shashlik and non bread baked fresh in a tandoor. Great outdoor ambience.", address="Chilonzor 9-mavze, Chilonzor", phone="+998 71 276 09 09", image_url="https://images.unsplash.com/photo-1482275548304-a58859dc31b7?w=600&q=80", price_range="$$", rating=4.7, capacity=200),
        Restaurant(name="Nasha Pizza", cuisine="Italian", description="Beloved Tashkent pizza restaurant with wood-fired Neapolitan pies, craft beer and a lively atmosphere. Locals' favourite for casual dining.", address="Yunusobod ko'chasi 5, Yunusobod", phone="+998 71 267 05 05", image_url="https://images.unsplash.com/photo-1498579150354-977475b7ea0b?w=600&q=80", price_range="$$", rating=4.6, capacity=80),
        Restaurant(name="Köşebaşı Turkish Grill", cuisine="Turkish", description="One of Tashkent's most popular Turkish restaurants with premium Anatolian grills, mezze platters and fresh Turkish bread baked daily.", address="Mirabad ko'chasi 22, Mirabad", phone="+998 71 233 22 00", image_url="https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600&q=80", price_range="$$$", rating=4.6, capacity=140),
        Restaurant(name="Plov Centre Yunusobod", cuisine="Uzbek", description="Tashkent's most famous plov centre serving the city's national dish from morning. Giant kazan pots, horse meat plov and traditional accompaniments.", address="Yunusobod 7-mavze, Yunusobod", phone="+998 71 267 07 07", image_url="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&q=80", price_range="$", rating=4.9, capacity=400),
        Restaurant(name="Cafe de Flore Tashkent", cuisine="French", description="Chic Parisian-inspired café with quiche, croque-monsieur, crème brûlée and fine French wines. Romantic setting in the heart of Tashkent.", address="Amir Temur ko'chasi 11, Mirzo Ulugbek", phone="+998 71 236 11 55", image_url="https://images.unsplash.com/photo-1551632436-cbf8dd35adfa?w=600&q=80", price_range="$$$", rating=4.7, capacity=60),
        Restaurant(name="Besh Qozon Chilonzor", cuisine="Uzbek", description="Second branch of the beloved plov institution in Chilonzor district. Same massive open kitchen, same unbeatable plov. Always packed at lunch.", address="Chilonzor 14-mavze, Chilonzor", phone="+998 71 276 14 14", image_url="https://images.unsplash.com/photo-1555244162-803834f70033?w=600&q=80", price_range="$", rating=4.8, capacity=350),
        Restaurant(name="Surkhon Restaurant", cuisine="Uzbek", description="Upscale Uzbek fine dining with a focus on dishes from the Surkhondaryo region. Rich lamb dishes, tandoor bread and rare regional specialities.", address="Mirzo Ulugbek ko'chasi 30, Mirzo Ulugbek", phone="+998 71 268 30 30", image_url="https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=600&q=80", price_range="$$$", rating=4.6, capacity=100),
        Restaurant(name="Himalaya Indian Restaurant", cuisine="Indian", description="Tashkent's most popular Indian restaurant with aromatic curries, tandoori dishes, biryani and fresh naan. Vegetarian-friendly menu.", address="Yunusobod 9-mavze, Yunusobod", phone="+998 71 267 09 90", image_url="https://images.unsplash.com/photo-1424847651672-bf20a4b0982b?w=600&q=80", price_range="$$", rating=4.5, capacity=80),
        Restaurant(name="Chaikhana National", cuisine="Uzbek", description="Traditional teahouse restaurant in a garden setting. Shashlik, lagman, somsa and green tea served on low tables with cushions under mulberry trees.", address="Shayxontohur ko'chasi 55, Shayxontohur", phone="+998 71 244 55 55", image_url="https://images.unsplash.com/photo-1482275548304-a58859dc31b7?w=600&q=80", price_range="$", rating=4.7, capacity=300),
        Restaurant(name="Osteria Roma", cuisine="Italian", description="Intimate Italian osteria with homestyle Roman cooking. Daily fresh pasta, slow-cooked ragù, tiramisu and a well-chosen Sicilian wine selection.", address="Mirabad ko'chasi 15, Mirabad", phone="+998 71 233 15 15", image_url="https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&q=80", price_range="$$$", rating=4.6, capacity=55),
        Restaurant(name="Kebab House", cuisine="Uzbek", description="Casual neighbourhood kebab restaurant with 12 varieties of shashlik, stuffed peppers, bread from the tandoor and cold Sarbast beer.", address="Chilonzor 3-mavze, Chilonzor", phone="+998 71 276 03 03", image_url="https://images.unsplash.com/photo-1544025162-d76694265947?w=600&q=80", price_range="$", rating=4.5, capacity=120),
        Restaurant(name="Tashkent Garden Restaurant", cuisine="European", description="Sprawling garden restaurant with live music on weekends. International menu, wood-fired grill and beautiful landscaped outdoor seating.", address="Navoiy ko'chasi 25, Mirzo Ulugbek", phone="+998 71 268 25 25", image_url="https://images.unsplash.com/photo-1537047902294-62a40c20a6ae?w=600&q=80", price_range="$$$", rating=4.6, capacity=250),
        Restaurant(name="Golden Plov", cuisine="Uzbek", description="Award-winning plov restaurant run by a master oshpaz with 30 years experience. Fergana-style and Tashkent-style plov both available daily.", address="Yunusobod 3-mavze, Yunusobod", phone="+998 71 267 03 03", image_url="https://images.unsplash.com/photo-1563245372-f21724e3856d?w=600&q=80", price_range="$$", rating=4.8, capacity=150),
        Restaurant(name="Mediterranean House", cuisine="Mediterranean", description="Fresh Mediterranean cuisine with Greek salads, grilled octopus, hummus, falafel and fresh seafood. Bright, airy terrace with a Santorini feel.", address="Mirzo Ulugbek ko'chasi 60, Mirzo Ulugbek", phone="+998 71 268 60 60", image_url="https://images.unsplash.com/photo-1559339352-11d035aa65de?w=600&q=80", price_range="$$$", rating=4.6, capacity=90),
        Restaurant(name="Tashkent Banquet Hall", cuisine="Uzbek", description="Premium Uzbek banquet venue for weddings, birthday celebrations and corporate events. Capacity for 500 guests with live music and national performances.", address="Chilonzor 20-mavze, Chilonzor", phone="+998 71 276 20 20", image_url="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&q=80", price_range="$$$", rating=4.7, capacity=500),
    ]
    for r in restaurants:
        db.session.add(r)
    db.session.commit()
    print(f"Seeded {len(restaurants)} restaurants")
with app.app_context():
    db.create_all()
    seed_restaurants()
    print('Database ready!')

# ===== ROUTES =====

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/auth')
def auth():
    return render_template('auth.html')

@app.route('/register', methods=['POST'])
def register():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    next_page = request.form.get('next') or request.args.get('next') or '/dashboard'
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return redirect('/auth')
    new_user = User(
        name=first_name + ' ' + last_name,
        email=email, phone=phone,
        password=generate_password_hash(password)
    )
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    return redirect(next_page)

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    next_page = request.form.get('next') or '/dashboard'
    if not next_page or next_page == '/':
        next_page = '/dashboard'
    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        login_user(user)
        owned = Restaurant.query.filter_by(owner_id=user.id).first()
        if owned:
            return redirect('/admin')
        if user.is_admin:
            return redirect('/admin')
        return redirect(next_page)
    flash("Incorrect email or password. Please try again.", 'error')
    return redirect('/auth?next=' + next_page)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/dashboard')
@login_required
def dashboard():
    reservations = Reservation.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', reservations=reservations, now=datetime.utcnow())

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/profile/update', methods=['POST'])
@login_required
def profile_update():
    form_type = request.form.get('form_type')
    if form_type == 'info':
        current_user.name = request.form.get('name')
        current_user.phone = request.form.get('phone')
        current_user.email = request.form.get('email')
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    elif form_type == 'password':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        if not check_password_hash(current_user.password, current_password):
            flash('Current password is incorrect!', 'error')
        elif new_password != confirm_password:
            flash('New passwords do not match!', 'error')
        else:
            current_user.password = generate_password_hash(new_password)
            db.session.commit()
            flash('Password updated successfully!', 'success')
    return redirect('/profile')

@app.route('/review/<int:restaurant_id>', methods=['POST'])
@login_required
def add_review(restaurant_id):
    rating = int(request.form.get('rating', 0))
    comment = request.form.get('comment', '').strip()
    if rating < 1 or rating > 5 or not comment:
        return redirect('/restaurants')
    existing = Review.query.filter_by(user_id=current_user.id, restaurant_id=restaurant_id).first()
    if existing:
        return redirect('/restaurants')
    review = Review(user_id=current_user.id, restaurant_id=restaurant_id, rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()
    return redirect('/restaurants')

@app.route('/book/<int:restaurant_id>', methods=['GET', 'POST'])
def book(restaurant_id):
    if not current_user.is_authenticated:
        return redirect('/auth?next=/book/' + str(restaurant_id))

    restaurant = Restaurant.query.get_or_404(restaurant_id)

    if request.method == 'POST':
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        guests = request.form.get('guests', 2)
        occasion = request.form.get('occasion', '')
        special = request.form.get('special_request', '')

        if not date_str or not time_str:
            flash('Please select a date and time.', 'error')
            return render_template('book.html', restaurant=restaurant, today=date.today().isoformat())

        reservation = Reservation(
            user_id=current_user.id,
            restaurant_id=restaurant.id,
            date=datetime.strptime(date_str, '%Y-%m-%d').date(),
            time=time_str,
            guests=int(guests),
            occasion=occasion,
            special_request=special,
            status='confirmed'
        )
        db.session.add(reservation)
        db.session.commit()
        flash('Your table has been reserved!', 'success')
        return redirect('/dashboard')

    return render_template('book.html', restaurant=restaurant, today=date.today().isoformat())

@app.route('/cancel/<int:res_id>')
@login_required
def cancel_reservation(res_id):
    res = Reservation.query.get_or_404(res_id)
    if res.user_id == current_user.id:
        diff = (datetime.utcnow() - res.created_at).total_seconds() / 60
        if diff <= 30:
            res.status = 'cancelled'
            db.session.commit()
    return redirect('/dashboard')

@app.route('/restaurants')
def restaurants():
    all_restaurants = Restaurant.query.all()
    return render_template('restaurants.html', restaurants=all_restaurants)

@app.route('/about')
def about():
    return render_template('about.html')


# ===== ADMIN ROUTES =====
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect('/auth')
        if not current_user.is_admin:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated

@app.route('/admin')
@login_required
def admin():
    # Restaurant owner kirganmi?
    owned = Restaurant.query.filter_by(owner_id=current_user.id).first()
    if owned:
        reservations = Reservation.query.filter_by(restaurant_id=owned.id).all()
        return render_template('admin.html',
            users=[],
            restaurants=[owned],
            reservations=reservations,
            reviews=[],
            is_owner=True,
            owned_restaurant=owned
        )
    # Super admin
    if not current_user.is_admin:
        return redirect('/')
    return render_template('admin.html',
        users=User.query.all(),
        restaurants=Restaurant.query.all(),
        reservations=Reservation.query.all(),
        reviews=Review.query.all(),
        is_owner=False,
        owned_restaurant=None
    )

@app.route('/admin/cancel-reservation/<int:res_id>', methods=['POST'])
@admin_required
def admin_cancel_reservation(res_id):
    res = Reservation.query.get_or_404(res_id)
    res.status = 'cancelled'
    db.session.commit()
    flash('Reservation cancelled.', 'success')
    return redirect('/admin')

@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Cannot delete admin users.', 'error')
        return redirect('/admin')
    Reservation.query.filter_by(user_id=user.id).delete()
    Review.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect('/admin')

@app.route('/admin/delete-review/<int:review_id>', methods=['POST'])
@admin_required
def admin_delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted.', 'success')
    return redirect('/admin')

@app.route('/admin')
@login_required
def restaurant_admin():
    restaurant = Restaurant.query.filter_by(owner_id=current_user.id).first()
    if not restaurant:
        return redirect('/')
    reservations = Reservation.query.filter_by(
        restaurant_id=restaurant.id
    ).order_by(Reservation.date.desc()).all()
    return render_template('admin.html',
        restaurant=restaurant,
        reservations=reservations
    )

@app.route('/restaurant-admin/cancel/<int:res_id>', methods=['POST'])
@login_required
def owner_cancel_reservation(res_id):
    restaurant = Restaurant.query.filter_by(owner_id=current_user.id).first()
    res = Reservation.query.get_or_404(res_id)
    if res.restaurant_id == restaurant.id:
        res.status = 'cancelled'
        db.session.commit()
    return redirect('/restaurant-admin')

if __name__ == '__main__':
    app.run(debug=True)