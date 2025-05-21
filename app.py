from flask import Flask, request, jsonify
from flask_cors import CORS
from meta_ai_api import MetaAI
import json
import re

app = Flask(__name__)
CORS(app)

ai = MetaAI()

@app.route("/summarize", methods=["POST"])
def summarize():
    try:
        data = request.get_json()
        post = data.get("post_text", "")
        comments = data.get("comments_text", "").split("\n")
        
        prompt = f"""
You are an intelligent comment summarizer and clusterer.

Task:
1. Read the post and its associated list of comments.
2. Group the comments into similar types or topics (e.g., questions, agreement, suggestions, etc.).
3. From each group, select the most representative or relevant comment.
4. Choose up to 5 such representative comments across the most common or impactful types.
5. Order the top 5 selected comments so that the most frequently discussed type appears first.
6. Assign a relevance score (between 0 and 1) to each selected comment.
7. Finally, write a concise summary explaining the overall direction and themes of these comments.

POST:
{post}

COMMENTS:
{chr(10).join(comments)}

Return the response in the following JSON format:
{{
  "top_comments": [
    {{ "text": "comment text", "score": 0.0 }},
    ...
  ],
  "summary": "Your summary here"
}}

If there are fewer than 5 distinct comment types, include only as many as are available.
Do not fabricate new comments if the list is empty—just return an appropriate message in the summary.
"""

        response = ai.prompt(message=prompt)
        output = response.get("message", "").strip()

        match = re.search(r'{.*}', output, re.DOTALL)
        if not match:
            raise ValueError("AI response did not return valid JSON.")

        parsed = json.loads(match.group(0))
        parsed["top_comments"] = sorted(parsed["top_comments"], key=lambda x: x["score"], reverse=True)
        return jsonify(parsed)


    except Exception as e:
        print("❌ BACKEND ERROR:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
