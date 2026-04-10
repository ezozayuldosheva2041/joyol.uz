from app import app, db, User, Restaurant
from werkzeug.security import generate_password_hash

owners = [
    (1,  "Afsona Restaurant",           "rest1@joyol.uz",  "rest1pass"),
    (2,  "Caravan Restaurant",           "rest2@joyol.uz",  "rest2pass"),
    (3,  "Besh Qozon Pilaf Center",      "rest3@joyol.uz",  "rest3pass"),
    (4,  "Syrovarnya",                   "rest4@joyol.uz",  "rest4pass"),
    (5,  "Jumanji Restaurant",           "rest5@joyol.uz",  "rest5pass"),
    (6,  "City Grill New",               "rest6@joyol.uz",  "rest6pass"),
    (7,  "Gruzinskiy Dvorik",            "rest7@joyol.uz",  "rest7pass"),
    (8,  "Sette Restaurant",             "rest8@joyol.uz",  "rest8pass"),
    (9,  "Basilic Restaurant",           "rest9@joyol.uz",  "rest9pass"),
    (10, "Navat Restaurant",             "rest10@joyol.uz", "rest10pass"),
    (11, "Affresco Restaurant",          "rest11@joyol.uz", "rest11pass"),
    (12, "Forn Lebnen",                  "rest12@joyol.uz", "rest12pass"),
    (13, "Khan Chapan",                  "rest13@joyol.uz", "rest13pass"),
    (14, "Sultan Saray",                 "rest14@joyol.uz", "rest14pass"),
    (15, "Tandiriy Restaurant",          "rest15@joyol.uz", "rest15pass"),
    (16, "Plov Lounge & Banquet Hall",   "rest16@joyol.uz", "rest16pass"),
    (17, "L'Opera Ristorante",           "rest17@joyol.uz", "rest17pass"),
    (18, "Kaspiyka Seafood",             "rest18@joyol.uz", "rest18pass"),
    (19, "Restaurant 12",               "rest19@joyol.uz", "rest19pass"),
    (20, "Bosphorus Qorasaroy",          "rest20@joyol.uz", "rest20pass"),
    (21, "SEZAM Turkish Restaurant",     "rest21@joyol.uz", "rest21pass"),
    (22, "MANDU Dumpling House",         "rest22@joyol.uz", "rest22pass"),
    (23, "Lali Restaurant",              "rest23@joyol.uz", "rest23pass"),
    (24, "Silk 96 Wine & Lounge",        "rest24@joyol.uz", "rest24pass"),
    (25, "Navvat Lounge Bar",            "rest25@joyol.uz", "rest25pass"),
    (26, "Eco Café Tashkent",            "rest26@joyol.uz", "rest26pass"),
    (27, "Qanotchi Steakhouse",          "rest27@joyol.uz", "rest27pass"),
    (28, "Tarnovboshi Restaurant",       "rest28@joyol.uz", "rest28pass"),
    (29, "Karimbek Restaurant",          "rest29@joyol.uz", "rest29pass"),
    (30, "Cafe 1991",                    "rest30@joyol.uz", "rest30pass"),
    (31, "Bon! French Café",             "rest31@joyol.uz", "rest31pass"),
    (32, "Brasserie Tashkent",           "rest32@joyol.uz", "rest32pass"),
    (33, "MONA Restaurant & Lounge",     "rest33@joyol.uz", "rest33pass"),
    (34, "ALFA & Bakery",                "rest34@joyol.uz", "rest34pass"),
    (35, "Prime Steakhouse",             "rest35@joyol.uz", "rest35pass"),
    (36, "Furusato Japanese",            "rest36@joyol.uz", "rest36pass"),
    (37, "Dragon Palace",                "rest37@joyol.uz", "rest37pass"),
    (38, "Samarkand Terrace",            "rest38@joyol.uz", "rest38pass"),
    (39, "Nasha Pizza",                  "rest39@joyol.uz", "rest39pass"),
    (40, "Köşebaşı Turkish Grill",       "rest40@joyol.uz", "rest40pass"),
    (41, "Plov Centre Yunusobod",        "rest41@joyol.uz", "rest41pass"),
    (42, "Cafe de Flore Tashkent",       "rest42@joyol.uz", "rest42pass"),
    (43, "Besh Qozon Chilonzor",         "rest43@joyol.uz", "rest43pass"),
    (44, "Surkhon Restaurant",           "rest44@joyol.uz", "rest44pass"),
    (45, "Himalaya Indian Restaurant",   "rest45@joyol.uz", "rest45pass"),
    (46, "Chaikhana National",           "rest46@joyol.uz", "rest46pass"),
    (47, "Osteria Roma",                 "rest47@joyol.uz", "rest47pass"),
    (48, "Kebab House",                  "rest48@joyol.uz", "rest48pass"),
    (49, "Tashkent Garden Restaurant",   "rest49@joyol.uz", "rest49pass"),
    (50, "Golden Plov",                  "rest50@joyol.uz", "rest50pass"),
    (51, "Mediterranean House",          "rest51@joyol.uz", "rest51pass"),
    (52, "Tashkent Banquet Hall",        "rest52@joyol.uz", "rest52pass"),
]

with app.app_context():
    print("\n===== RESTAURANT OWNER CREDENTIALS =====")
    for order, rest_name, email, password in owners:
        restaurant = Restaurant.query.filter_by(name=rest_name).first()
        if not restaurant:
            print(f"not found: {rest_name}")
            continue
        if restaurant.owner_id:
            print(f"already have: {rest_name}")
            continue
        existing = User.query.filter_by(email=email).first()
        if not existing:
            u = User(
                name=rest_name + " Admin",
                email=email,
                password=generate_password_hash(password)
            )
            db.session.add(u)
            db.session.flush()
            restaurant.owner_id = u.id
        else:
            restaurant.owner_id = existing.id
        print(f"#{order:>2} {rest_name}")
        print(f"      Email : {email}")
        print(f"      Parol : {password}")
        print()
    db.session.commit()
    print("ready")
    print("=========================================\n")
