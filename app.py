from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_jwt_extended import JWTManager, create_access_token
import bcrypt
app = Flask(__name__)
jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = "ILOVEPLANTS"
client = MongoClient("mongodb+srv://killer:Dg1Z8DfSbQxm0b0t@cluster0.j1ccr.mongodb.net/")
db = client["flaskDatabase"]
user_collection = db["user"]

def user_ser(user):
    return{
        "id": str(user.get("_id")),
        "name": user.get("name"),
        "password": user.get("password"),
        "age": user.get("age"),
        "hobbies": user.get("hobbies")
    }

@app.route("/registerAndGetUser", methods=["POST", "GET"])
def register():
    # print(request.method)
    if request.method == "POST":
        data = request.json
        if not data:
            return jsonify({"err":"No data Provided"})
        hashed_pass = bcrypt.hashpw(data.get("password").encode("utf-8"), bcrypt.gensalt())
        data["password"] = hashed_pass
        # print(data)
        user_collection.insert_one(data)
        return "registered"
    elif request.method == "GET":
        users = user_collection.find({})
        return jsonify([user_ser(user) for user in users])
        
@app.route("/UpdateAndDeleteAndRetrieveUser/<id>", methods=['GET', "PUT", "DELETE"])
def UpdateAndDeleteAndRetrieve(id):
    if request.method == "GET":
        user = user_collection.find_one({"_id": ObjectId(id)})
        return jsonify(user_ser(user))
    elif request.method == "PUT":
        data = ''
        if request.content_type == "application/json":
            data = request.get_json()
        else:
            data = request.form.to_dict()
        # print(data)
        if not data:
            return jsonify({"error": "No data provided"}), 400
        user = user_collection.update_one({"_id": ObjectId(id)}, {"$set": data})
        # print(user)
        return jsonify({"message": "user updated","updated": data})
    elif request.method == "DELETE":
        const = user_collection.delete_one({"_id": ObjectId(id)})
        if const.deleted_count == 0:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "deleted"})
    

@app.route("/listGetAndPostReview/<id>", methods=["GET", "POST"])
def reviewGP(id):
    if request.method == "POST":
        reviews = user_collection.find_one({"_id": ObjectId(id)}, {"_id": 0})
        if reviews == None:
            return jsonify({"error": "User Not Found"})
        data = request.json
        
        if type(data) == dict:
            user_collection.update_one({"_id": ObjectId(id)}, {"$addToSet": {"hobbies": {"$each": data}}})
        user_collection.update_one({"_id": ObjectId(id)}, {"$addToSet": {"hobbies": data}})
        review = user_collection.find_one({"_id": ObjectId(id)})
        return jsonify({"message": user_ser(review)})
@app.route("/login", methods=["POST"])
def login():
    data  = request.json 
    if not data:
        return jsonify({"err": "No data Provided"}), 400
    user = user_collection.find_one({"name": data.get("name")})
    if not user:
        return jsonify({"err":"User NOt Found"}), 404
    
    isPass = bcrypt.checkpw(data.get("password").encode("utf-8"), user.get("password"))
    if not isPass:
        return jsonify({"err":"Invalid Details"}), 400
    # print(isPass)
    # print(user.get("password").decode("utf-8"))
    # print(data.get("password").encode("utf-8"))
    jwtToken = create_access_token(user.get("name"))
    # print(jwtToken)
    return jsonify({"msg":"successful", "jwt":jwtToken})
if __name__ == "__main__":
    app.run(debug=True)