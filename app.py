from flask import Flask, flash, redirect, request, jsonify, session, url_for
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import requests
from flask import render_template
import re
from werkzeug.utils import secure_filename
from datetime import datetime 
import pandas as pd
from sklearn.cluster import KMeans
from datetime import datetime  

load_dotenv()
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = "your_super_secret_key"
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['UPLOAD_FOLDER'] = 'uploads' 
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 


mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["ecosystemDB"]


products_collection = db["products"]
users_collection = db["users"]
collection_invoices = db["invoices"]

users_collection.create_index("user_id", unique=True)
collection_invoices.create_index([("user_id", 1), ("date", -1)]) 
products_collection.create_index("name", unique=True) 

invoice_data = [
    {
    "invoice_number": "INV001",
    "products": ["Atta", "Sunflower Oil", "Salt", "Tur Dal", "Basmati Rice"],
    "date": "2025-07-01",
    "store": "Vishal Mega Mart"
  },
  {
    "invoice_number": "INV002",
    "products": ["Sugar", "Maggi", "Tea", "Instant Coffee", "Butter"],
    "date": "2025-07-01",
    "store": "Vijay Kirana Store"
  },
  {
    "invoice_number": "INV003",
    "products": ["Milk", "Parle-G Biscuits", "Hide & Seek Biscuits", "Cornflakes", "Mixed Fruit Jam"],
    "date": "2025-07-01",
    "store": "Shakti General Store"
  },
  {
    "invoice_number": "INV004",
    "products": ["Chilli Powder", "Garam Masala", "Rajma", "Chana Dal", "Poha"],
    "date": "2025-07-01",
    "store": "Daily Needs Corner"
  },
  {
    "invoice_number": "INV005",
    "products": ["Soap", "Shampoo", "Toothpaste", "Toothbrush", "Handwash"],
    "date": "2025-07-01",
    "store": "Ravi’s Superstore"
  },
  {
    "invoice_number": "INV006",
    "products": ["Antiseptic Liquid", "Body Lotion", "Face Wash", "Talcum Powder", "Baby Powder"],
    "date": "2025-07-01",
    "store": "Apna Bazaar"
  },
  {
    "invoice_number": "INV007",
    "products": ["Dish Bar", "Toilet Cleaner", "Detergent Powder", "Floor Cleaner", "Disinfectant"],
    "date": "2025-07-01",
    "store": "Reliance Fresh Mart"
  },
  {
    "invoice_number": "INV008",
    "products": ["Scrub Pad", "Mosquito Spray", "Air Freshener", "Phenyl", " Disinfectant Wipes"],
    "date": "2025-07-01",
    "store": "Family Kirana"
  },
  {
    "invoice_number": "INV009",
    "products": ["Chips", "Kurkure", "Fruit Juice", "Orange Juice", "Cheese Slices"],
    "date": "2025-07-01",
    "store": "Manoj General Store"
  },
  {
    "invoice_number": "INV010",
    "products": ["Bread", "Eggs", "Marie Gold Biscuits", "Almonds", "Protein Bar"],
    "date": "2025-07-01",
    "store": "Smart Ration Hub"
  }
]


if collection_invoices.count_documents({}) == 0:
    collection_invoices.insert_many(invoice_data)


def calculate_eco_score(product):
    score = 0
    if product.get("recyclable"): score += 2
    if product.get("reusable"): score += 2
    cf = product.get("carbon_footprint", 999)
    if cf < 1.5:
        score += 2
    elif cf < 3:
        score += 1
    if len(product.get("eco_certifications", [])) > 0: score += 1
    if "locally-produced" in product.get("sustainability_tags", []): score += 1
    if product.get("user_sentiment_score", 0) > 0.7: score += 1
    return min(score, 10)

def call_fastapi_ml(file):
    url = "http://localhost:8000/upload-bill"
    files = {"file": (file.filename, file.stream, file.content_type)}
    response = requests.post(url, files=files)
    return response.json() if response.status_code == 200 else {"error": "FastAPI call failed"}

# ---------- Routes ----------

# @app.route("/")
# def home():
#     return "Flask backend is working!"

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/add-product", methods=["POST"])
def add_product():
    data = request.json
    required_fields = [
        "name", "brand", "category", "material_type", "packaging_type",
        "reusable", "recyclable", "carbon_footprint", "origin_country",
        "eco_certifications", "sustainability_tags", "user_sentiment_score",
        "lifecycle_stage", "walmart_green_badge", "eco_points_rewarded",
        "last_updated"
    ]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields"}), 400

    eco_score = calculate_eco_score(data)
    data["eco_score"] = eco_score
    products_collection.insert_one(data)
    return jsonify({"message": "Product added successfully"}), 201

@app.route("/products", methods=["GET"])
def get_products():
    products = list(products_collection.find({}, {"_id": 0}))
    return jsonify(products)

@app.route("/product/<name>", methods=["GET"])
def get_product(name):
    product = products_collection.find_one({"name": name}, {"_id": 0})
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product)

@app.route("/product/<name>", methods=["PUT"])
def update_product(name):
    data = request.json
    existing_product = products_collection.find_one({"name": name})
    if not existing_product:
        return jsonify({"error": "Product not found"}), 404

    updated_product = {**existing_product, **data}
    updated_product["eco_score"] = calculate_eco_score(updated_product)
    products_collection.update_one({"name": name}, {"$set": updated_product})
    return jsonify({"message": "Product updated successfully", "eco_score": updated_product["eco_score"]})

@app.route("/product/<name>", methods=["DELETE"])
def delete_product(name):
    result = products_collection.delete_one({"name": name})
    if result.deleted_count == 0:
        return jsonify({"error": "Product not found"}), 404
    return jsonify({"message": "Product deleted successfully"})

@app.route("/top-eco-products", methods=["GET"])
def top_eco_products():
    top_products = list(
        products_collection.find({}, {"_id": 0}).sort("eco_score", -1).limit(10)
    )
    return jsonify(top_products)

@app.route("/user/<user_id>")
def get_user(user_id):
    """Get detailed user information including recent activity"""
    user = users_collection.find_one({"user_id": user_id}, {"_id": 0, "password": 0})
    if not user:
        return jsonify({"error": "User not found"}), 404

    
    last_invoice = collection_invoices.find_one(
        {"user_id": user_id},
        sort=[("date", -1)],  
        projection={"_id": 0, "invoice_number": 1, "date": 1, "products": 1}
    )

    response_data = {
        **user,
        "last_points_earned": user.get("last_points_earned", 0),
        "total_points": user.get("eco_points", 0)
    }

    if last_invoice:
        
        products_info = []
        total_score = 0
        
        for product_name in last_invoice["products"]:
            product = products_collection.find_one({
                "name": {
                    "$regex": f"^{re.escape(product_name.strip())}$",
                    "$options": "i"
                }
            })
            if product:
                score = calculate_eco_score(product)
                total_score += score
                products_info.append({
                    "name": product["name"],
                    "category": product.get("category", "General"),
                    "points": score
                })

        response_data.update({
            "last_invoice": last_invoice["invoice_number"],
            "last_purchase_date": last_invoice["date"],
            "last_products": products_info,
            "last_points_earned": total_score
        })

    return jsonify(response_data)

# @app.route("/signup", methods=["POST"])
# def signup():
#     data = request.json
#     if users_collection.find_one({"email": data["email"]}):
#         return jsonify({"error": "User already exists"}), 409

#     user = {
#         "user_id": data["email"].split("@")[0],
#         "name": data["name"],
#         "email": data["email"],
#         "password": data["password"],
#         "eco_points": 0,
#         "products": []
#     }

#     users_collection.insert_one(user)
#     return jsonify({"message": "Signup successful", "user_id": user["user_id"]}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    
    user = users_collection.find_one({"email": data["email"]})
    if not user or user["password"] != data["password"]:
        return jsonify({"error": "Invalid credentials"}), 401

   
    session["user_email"] = user["email"]
    session["user_name"] = user["name"]
    return jsonify({
        "message": "Login successful",
        "user_id": user["user_id"],
        "user_name": user["name"],
        "eco_points": user.get("eco_points", 0)
    }), 200



@app.route("/signup", methods=["POST", "OPTIONS"])
def signup():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200  # CORS  

    data = request.json
    if users_collection.find_one({"email": data["email"]}):
        return jsonify({"error": "User already exists"}), 409

    user = {
        "user_id": data["email"].split("@")[0],
        "name": data["name"],
        "email": data["email"],
        "password": data["password"],
        "eco_points": 0,
        "products": []
    }

    users_collection.insert_one(user)
    return jsonify({"message": "Signup successful", "user_id": user["user_id"]}), 201

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('user_name', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login_page'))  


@app.route("/upload-receipt", methods=["POST"])
def upload_receipt():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    result = call_fastapi_ml(file)
    if "error" in result:
        return jsonify(result), 500

    invoice_number = result["invoice_number"]
    user_id = request.headers.get("user-id")  
    
    if not user_id:
        return jsonify({"error": "User ID required"}), 400

    collection_invoices.insert_one({
        "invoice_number": invoice_number.upper(),
        "user_id": user_id,
        "products": result["products"],
        "date": datetime.now().strftime("%Y-%m-%d"),
        "store": result.get("store", "Unknown Store")
    })

    # Rest calculation...
    total_score = 0
    for product_name in result["products"]:
        product = products_collection.find_one({
            "name": {
                "$regex": f"^{re.escape(product_name.strip())}$",
                "$options": "i"
            }
        })
        if product:
            total_score += calculate_eco_score(product)

    # Update user points
    users_collection.update_one(
        {"user_id": user_id},
        {"$inc": {"eco_points": total_score}}
    )

    return jsonify({
        "message": "Receipt processed successfully",
        "invoice_number": invoice_number,
        "eco_points_earned": total_score,
        "products": result["products"]
    }), 200


@app.route("/invoice/<invoice_number>", methods=["GET"])
def get_invoice_details(invoice_number):
    invoice = collection_invoices.find_one({"invoice_number": invoice_number.upper()})
    
    if not invoice:
        return jsonify({"error": "Invoice not found"}), 404

    products_info = []
    total_score = 0

    for product_name in invoice["products"]:
        product = products_collection.find_one({
            "name": {
                "$regex": f"^{re.escape(product_name.strip())}$",
                "$options": "i"
            }
        })
        if product:
            score = calculate_eco_score(product)
            product["eco_score"] = score
            total_score += score
            products_info.append({k: product[k] for k in product if k != "_id"})
        else:
            products_info.append({
                "name": product_name,
                "eco_score": 0,
                "note": "Product details not found in database"
            })

    avg_score = round(total_score / len(products_info), 2) if products_info else 0

    #Save score to invoice document
    collection_invoices.update_one(
        {"invoice_number": invoice_number.upper()},
        {"$set": {
            "total_score": total_score,
            "average_score": avg_score
        }}
    )

    #Updating eco points
    user_email = session.get("user_email")
    if user_email:
        user = users_collection.find_one({"email": user_email})
        if user:
            current_points = user.get("eco_points", 0)
            users_collection.update_one(
                {"email": user_email},
                {"$set": {"eco_points": current_points + total_score}}
            )

    return jsonify({
        "invoice_number": invoice["invoice_number"],
        "store": invoice.get("store", ""),
        "date": invoice.get("date", ""),
        "products": products_info,
        "total_score": total_score,
        "average_score": avg_score
    }), 200


@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    user_id = request.args.get("user_id")
    users = list(users_collection.find({}, {"_id": 0, "password": 0}))  # Exclude sensitive data
    
    # Sort all users by eco_points descending
    users.sort(key=lambda u: u.get("eco_points", 0), reverse=True)

    # Assign tiers to all users
    for user in users:
        points = user.get("eco_points", 0)
        if points >= 100:
            user["tier"] = "Gold"
        elif points >= 50:
            user["tier"] = "Silver"
        else:
            user["tier"] = "Bronze"

    return jsonify(users)

@app.route("/api/check-session", methods=["GET"])
def check_session():
    user_email = session.get("user_email")
    if user_email:
        user = users_collection.find_one({"email": user_email}, {"_id": 0, "password": 0})
        if user:
            return jsonify({
                "loggedIn": True,
                "user_id": user["user_id"],
                "user_name": user["name"],
                "user_email": user["email"]
            })
    
    return jsonify({"loggedIn": False})



@app.route("/api/start", methods=["POST"])
def api_start():
    return jsonify({"message": "Welcome to EcoSphere backend!"}), 200

@app.route("/")
def root_redirect():
    return render_template("index.html")

@app.route("/index.html")
def home():
    return render_template("index.html")

@app.route("/login-page")
def login_page():
    return render_template("login.html")

@app.route("/signup-page")
def signup_page():
    return render_template("signup.html")

@app.route("/invoice-page")
def invoice_page():
    return render_template("invoice.html")

@app.route("/leaderboard-page")
def leaderboard_page():
    return render_template("leaderboard.html")

@app.route("/debug-products")
def debug_products():
    output = []
    for p in products_collection.find():
        output.append({
            "name": p.get("name"),
            "recyclable": p.get("recyclable"),
            "carbon_footprint": p.get("carbon_footprint"),
            "eco_certifications": p.get("eco_certifications")
        })
    return jsonify(output)

@app.route('/dashboard-data', methods=['GET'])
def dashboard_data():
    
    invoices = list(collection_invoices.find({}))
   
    df = pd.DataFrame(invoices)
    avg_scores = df.groupby('user_id')['total_score'].mean().reset_index()
    
    # KMeans clustering
    kmeans = KMeans(n_clusters=3)
    avg_scores['cluster'] = kmeans.fit_predict(avg_scores[['total_score']])
    
    # Map clusters to labels
    cluster_labels = {0: 'Eco-conscious', 1: 'Neutral', 2: 'High carbon'}
    avg_scores['cluster_label'] = avg_scores['cluster'].map(cluster_labels)
    
    # Prepare response data
    response_data = avg_scores[['user_id', 'total_score', 'cluster_label']].to_dict(orient='records')
    
    return jsonify(response_data)

@app.route('/api/sentiment-data', methods=['GET'])
def sentiment_data():
    data = {
        "eco_positive": 70,
        "neutral": 20,
        "non_eco": 10
    }
    return jsonify(data)

@app.route('/sentiment.html', methods=['GET'])
def sentiment_page():
    return render_template('sentiment.html')

@app.route('/api/eco-points-data', methods=['GET'])
def eco_points_data():
    
    data = {
        "labels": ["January", "February", "March"],
        "points": [10, 20, 30]
    }
    return jsonify(data)

@app.route('/api/user-engagement-data', methods=['GET'])
def user_engagement_data():
    data = {
        "labels": ["User  1", "User  2", "User  3"],
        "engagement": [5, 10, 15]
    }
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
