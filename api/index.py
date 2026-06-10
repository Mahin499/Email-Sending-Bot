import os
import sys
from flask import Flask, request, jsonify

# Add root folder to sys.path to enable loading parent modules on Vercel
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from email_generator import EmailGenerator

app = Flask(__name__)

# Instantiate email generator with Vercel environmental variables
use_llm = os.getenv("USE_LLM", "false").lower() == "true"
groq_key = os.getenv("GROQ_API_KEY", "")
generator = EmailGenerator(use_llm=use_llm, groq_api_key=groq_key)

@app.route("/api/generate", methods=["POST"])
def generate():
    """
    Exposes the email personalization logic as a serverless endpoint.
    Expects a JSON body matching the target contact record schema.
    """
    data = request.json or {}
    try:
        subject, body = generator.generate(data)
        warnings = generator.validate_email(subject, body)
        return jsonify({
            "subject": subject,
            "body": body,
            "warnings": warnings
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    """
    Catch-all endpoint returning API usage instructions.
    """
    return jsonify({
        "status": "online",
        "message": "The Closer Cold Email Generator API is running on Vercel!",
        "endpoints": {
            "POST /api/generate": "Submit contact details to generate personalized cold outreach"
        }
    })
