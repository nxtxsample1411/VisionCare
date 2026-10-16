import os
import io
import base64
import fitz  # PyMuPDF
import docx
import requests

from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from groq import Groq

# --------------------------------------
# Load environment variables
# --------------------------------------
load_dotenv()

app = FastAPI()

# --------------------------------------
# CORS CONFIG
# --------------------------------------
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------
# Initialize Groq Client
# --------------------------------------
try:
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("Groq API key missing. Add it to .env")

    client = Groq(api_key=groq_api_key)

except Exception as e:
    print(f"Error initializing Groq client: {e}")
    client = None


# --------------------------------------
# PICK DEFAULT MODEL
# --------------------------------------
def get_default_model():
    try:
        models = client.models.list()
        chat_keywords = ["llama", "mixtral", "gemma", "mistral", "chat", "vicuna"]

        for m in models.data:
            model_id = m.id.lower()
            if "guard" in model_id:
                continue
            if any(kw in model_id for kw in chat_keywords):
                return m.id

    except Exception as e:
        print("Error fetching models:", e)

    return "llama-3.3-70b-versatile"


DEFAULT_MODEL = get_default_model()

# --------------------------------------
# Pydantic Models
# --------------------------------------
class ChatRequest(BaseModel):
    message: str


# --------------------------------------
# ROOT
# --------------------------------------
@app.get("/")
def home():
    return {"message": "VisionCare backend running successfully (OSM Version)."}


# ============================================================
# ⭐ OSM DOCTOR FINDER — NO GOOGLE NEEDED ⭐
# ============================================================
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]

@app.get("/api/doctor-finder/nearby")
def doctor_finder_osm(lat: float, lng: float, radius: int = 5000):
    """
    Finds nearby eye doctors, optometrists, clinics, hospitals using OSM (OpenStreetMap) data.
    """

    query = f"""
    [out:json][timeout:25];
    (
      node["healthcare"="doctor"](around:{radius},{lat},{lng});
      node["healthcare"="optometrist"](around:{radius},{lat},{lng});
      node["medical_specialty"="ophthalmology"](around:{radius},{lat},{lng});
      node["amenity"="clinic"](around:{radius},{lat},{lng});
      node["amenity"="hospital"](around:{radius},{lat},{lng});
    );
    out body;
    """

    headers = {
        "User-Agent": "VisionCareApp/1.0 (contact: support@visioncare.com)",
        "Referer": "http://localhost:3000/",
        "Accept": "application/json"
    }

    response = None
    last_error = ""
    for url in OVERPASS_URLS:
        try:
            response = requests.post(url, data={"data": query}, headers=headers, timeout=15)
            if response.status_code == 200:
                break
            else:
                last_error = f"Status {response.status_code} from {url}"
        except Exception as e:
            last_error = str(e)

    if response is None or response.status_code != 200:
        detail_msg = f"OSM Overpass API request failed: {last_error}"
        raise HTTPException(status_code=500, detail=detail_msg)

    data = response.json()

    doctors = []
    for element in data.get("elements", []):
        tags = element.get("tags", {})

        doctors.append({
            "name": tags.get("name", "Unknown"),
            "address": tags.get("addr:full") or tags.get("addr:street") or "Address not available",
            "type": tags.get("healthcare") or tags.get("amenity") or "Clinic",
            "lat": element.get("lat"),
            "lng": element.get("lon")
        })

    return {"count": len(doctors), "results": doctors}


# ============================================================
# AI ENDPOINTS (UNCHANGED)
# ============================================================

@app.post("/chat/")
async def handle_chat_message(request: ChatRequest):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system",
                 "content": "You are VisionCare AI, an expert eye health assistant. Provide helpful, accurate responses about eye health, vision conditions, and eye care. Always recommend consulting a professional for serious concerns."},
                {"role": "user", "content": request.message}
            ],
            model=DEFAULT_MODEL,
        )

        reply = chat_completion.choices[0].message.content
        return {"reply": reply, "model": DEFAULT_MODEL}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-file/")
async def analyze_document(file: UploadFile = File(...)):
    contents = await file.read()
    filename = file.filename
    text = ""

    try:
        # Check if it's an image
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            img_base64 = base64.b64encode(contents).decode("utf-8")
            
            if filename.lower().endswith(".png"):
                mime = "image/png"
            elif filename.lower().endswith((".jpg", ".jpeg")):
                mime = "image/jpeg"
            else:
                mime = "image/webp"

            analysis = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a professional medical assistant. Analyze the provided medical report/document image and cleanly summarize the findings. Provide general informational insights based on the text you read in the image."},
                    {"role": "user", "content": [
                        {"type": "text", "text": "Please summarize this medical report."},
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_base64}"}}
                    ]}
                ],
                model=VISION_MODEL,
                temperature=0.3
            )
            summary = analysis.choices[0].message.content
            return {"filename": filename, "analysis": summary}

        elif filename.lower().endswith(".pdf"):
            with fitz.open(stream=contents, filetype="pdf") as doc:
                text = "".join(page.get_text() for page in doc)

        elif filename.lower().endswith(".docx"):
            with io.BytesIO(contents) as stream:
                doc_file = docx.Document(stream)
                text = "\n".join([p.text for p in doc_file.paragraphs])

        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a PDF, DOCX, JPG, or PNG.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {e}")

    if not text.strip():
        raise HTTPException(status_code=400, detail="No readable text found.")

    try:
        analysis = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Summarize this document professionally."},
                {"role": "user", "content": text[:8000]}
            ],
            model=DEFAULT_MODEL
        )

        summary = analysis.choices[0].message.content
        return {"filename": filename, "analysis": summary}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Failure: {e}")


# ============================================================
# ⭐ EYE DISEASE PREDICTION — GROQ VISION ⭐
# ============================================================

VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

@app.post("/predict")
async def predict_eye_disease(image: UploadFile = File(...)):
    """
    Accepts an eye image upload and uses Groq Vision LLM to analyze it
    for potential eye diseases.
    """
    try:
        # Read and encode image to base64
        contents = await image.read()
        img_base64 = base64.b64encode(contents).decode("utf-8")

        # Determine MIME type
        filename = image.filename or "image.png"
        if filename.lower().endswith(".png"):
            mime = "image/png"
        elif filename.lower().endswith((".jpg", ".jpeg")):
            mime = "image/jpeg"
        elif filename.lower().endswith(".webp"):
            mime = "image/webp"
        else:
            mime = "image/png"

        # Call Groq Vision model
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert ophthalmologist AI assistant. "
                        "Analyze the provided eye image and identify any potential eye diseases or conditions. "
                        "You MUST respond in EXACTLY this JSON format and nothing else:\n"
                        '{"disease": "<condition name or Normal>", "confidence": <0.0 to 1.0>, "details": "<brief explanation>"}\n'
                        "If the image is not an eye image, respond with:\n"
                        '{"disease": "Not an eye image", "confidence": 0.0, "details": "Please upload a clear image of an eye."}\n'
                        "Common conditions to look for: Diabetic Retinopathy, Glaucoma, Cataracts, "
                        "Macular Degeneration, Conjunctivitis, Pterygium, Keratoconus, Normal/Healthy Eye. "
                        "Respond ONLY with the JSON, no markdown, no extra text."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this eye image for any diseases or abnormalities."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime};base64,{img_base64}"
                            }
                        }
                    ]
                }
            ],
            model=VISION_MODEL,
            temperature=0.3,
            max_tokens=300
        )

        reply = chat_completion.choices[0].message.content.strip()

        # Try to parse the JSON response
        import json
        try:
            result = json.loads(reply)
            return {
                "disease": result.get("disease", "Unknown"),
                "confidence": float(result.get("confidence", 0.5)),
                "details": result.get("details", "")
            }
        except json.JSONDecodeError:
            # If model didn't return valid JSON, return a safe response
            return {
                "disease": "Analysis Complete",
                "confidence": 0.5,
                "details": reply
            }

    except Exception as e:
        print(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


# ============================================================
# END OF FILE
# ============================================================
