from flask import Flask, request, jsonify
from flask_cors import CORS
from meta_ai_api import MetaAI
import json
import re
import os

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
You are an intelligent comment summarizer and clusterer, with a strong focus on sentiment analysis.

Task:
1. Read the post and its associated list of comments.
2. Classify each comment into types (e.g., suggestions, agreement, questions, complaints) **and analyze sentiment** (positive, neutral, negative).
3. Strictly select only comments with **positive sentiment** that are constructive, appreciative, or supportive.
4. Completely ignore and exclude all neutral or negative comments, regardless of relevance.
5. From the positive comments, select up to 5 most representative ones based on clarity and usefulness.
6. Choose up to 5 such representative comments, ordered with **positive ones first**, and assign a relevance score (between 0 and 1) based on positivity, clarity, and usefulness.
7. Write a **concise summary** reflecting the main tone (especially positive feedback) and themes from these comments.

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

If no comments exist, return a summary stating that no comments were available.
Do not fabricate or guess missing data.
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
    port = int(os.environ.get("PORT", 5000))  # Required for Render
    app.run(host="0.0.0.0", port=port)
