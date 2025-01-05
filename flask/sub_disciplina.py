from flask import Flask, jsonify, request
import pymongo
from flask_cors import CORS

# Create the Flask app
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

# MongoDB connection
client = pymongo.MongoClient("mongodb://root:example@localhost:27017/")
db = client["qconcursos"]  # Database name
collection = db["subtopics"]  # Collection name

@app.route('/subtopics', methods=['GET'])
def get_sub_topics():
    try:
        # Fetch all items from the collection
        subtopics = list(collection.find({}, {"_id": 0}))  # Exclude the '_id' field from the response
        return jsonify(subtopics), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/subtopics', methods=['DELETE'])
def delete_all_sub_topics():
    try:
        result = collection.delete_many({})  # Correct method name
        return jsonify({"deleted_count": result.deleted_count}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_sub_topics_by_disciplina(disciplina):
    try:
        result = collection.find_one({disciplina: {"$exists": True}})
        
        if not result:
            return None 
    
        return result.get(disciplina, [])  
        
    except Exception as e:
        print(f"Error in get_topics_by_disciplina: {e}")
        return None  


@app.route('/subtopics/percentages', methods=['GET'])
def get_percentages():
    disciplina = request.args.get('disciplina')
    print(f"Received disciplina: {disciplina}")  

    if not disciplina:
        return jsonify({"error": "The 'disciplina' parameter is required"}), 400

    # Get topics data for the requested disciplina
    data = get_sub_topics_by_disciplina(disciplina)
    
    if not data:
        return jsonify({"error": f"No data found for disciplina: {disciplina}"}), 404

    result = []

    # Iterate through each topic in the disciplina
    for topic in data:
        topic_name = topic["name"]
        nested_subjects = topic.get("nested_subjects", [])

        # Process each nested subject
        for nested_subject in nested_subjects:
            subitems = nested_subject.get("subitems", [])

            # Process only subitems with caption "QUESTÕES"
            for subitem in subitems:
                if subitem["caption"] == "QUESTÕES":
                    # Extract the value (QUESTÕES)
                    questoes_value = float(subitem["value"].replace(".", "").replace(",", "."))
                    
                    # Add topic, nested subject, and subitem info to the result
                    result.append({
                        "topic_name": topic_name,
                        "nested_subject_name": nested_subject["name"],
                        "subitem_name": subitem["caption"],
                        "questoes_value": questoes_value
                    })

    # Calculate total questions from all subitems
    total_questions = sum(item["questoes_value"] for item in result)

    # Calculate the percentage for each subitem
    for item in result:
        item["percentage"] = (item["questoes_value"] / total_questions) * 100

    # Sort the results by percentage in descending order
    sorted_data = sorted(result, key=lambda x: x["percentage"], reverse=True)

    return jsonify(sorted_data)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)