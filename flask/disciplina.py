from flask import Flask, jsonify, request
import pymongo
from flask_cors import CORS

# Create the Flask app
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

# MongoDB connection
client = pymongo.MongoClient("mongodb://root:example@localhost:27017/")
db = client["qconcursos"]  # Database name
collection = db["topics"]  # Collection name

@app.route('/topics', methods=['GET'])
def get_topics():
    try:
        # Fetch all items from the collection
        topics = list(collection.find({}, {"_id": 0}))  # Exclude the '_id' field from the response
        return jsonify(topics), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/topics', methods=['DELETE'])
def delete_all_topics():
    try:
        result = collection.delete_many({})  # Correct method name
        return jsonify({"deleted_count": result.deleted_count}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_topics_by_disciplina(disciplina):
    try:
        result = collection.find_one({disciplina: {"$exists": True}})
        if not result:
            return None  # No result found for this disciplina
        return result.get(disciplina, [])
    
    except Exception as e:
        print(f"Error in get_topics_by_disciplina: {e}")
        return None  # In case of error, return None


@app.route('/topics/percentages', methods=['GET'])
def get_percentages():
    disciplina = request.args.get('disciplina')
    print(f"Received disciplina: {disciplina}")  

    if not disciplina:
        return jsonify({"error": "The 'disciplina' parameter is required"}), 400

    data = get_topics_by_disciplina(disciplina)
    
    for item in data:

        item["questoes_count"] = int(item["questoes_count"].replace(".", ""))
    total_questions = sum(item["questoes_count"] for item in data)

    for item in data:
        item["percentage"] = (item["questoes_count"] / total_questions) * 100

    sorted_data = sorted(data, key=lambda x: x["percentage"], reverse=True)

    return jsonify(sorted_data)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
