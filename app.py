import os
import base64
import json

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from openai import OpenAI

app = FastAPI()

HTML = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Educational Chart Analyzer</title>
</head>

<body style="font-family:Arial;max-width:700px;margin:auto;padding:20px">

<h1>AI Educational Chart Analyzer</h1>

<p>
Upload a chart screenshot for educational analysis.
This tool does not provide Buy/Sell signals or guaranteed predictions.
</p>

<input id="file" type="file" accept="image/*">

<br><br>

<button onclick="analyze()">Analyze Chart</button>

<pre id="output">Ready.</pre>

<script>
async function analyze() {

    const file = document.getElementById("file").files[0];

    if (!file) {
        document.getElementById("output").textContent =
        "Please select a chart image.";
        return;
    }

    const form = new FormData();
    form.append("file", file);

    document.getElementById("output").textContent =
    "Analyzing...";

    try {

        const response = await fetch("/analyze", {
            method: "POST",
            body: form
        });

        const result = await response.json();

        document.getElementById("output").textContent =
        JSON.stringify(result, null, 2);

    } catch (error) {

        document.getElementById("output").textContent =
        "Error: " + error.message;

    }
}
</script>

</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return {
            "error": "OPENAI_API_KEY is not configured."
        }

    image_data = await file.read()

    encoded_image = base64.b64encode(
        image_data
    ).decode("utf-8")

    client = OpenAI(api_key=api_key)

    prompt = """
Analyze this chart screenshot for educational purposes only.

Do not provide Buy/Sell instructions,
trading signals, guaranteed predictions,
or financial advice.

Return JSON with these fields:

trend
momentum
candle_structure
market_structure
support
resistance
reversal_signs
volatility
reasons
educational_note

Use concise English.
If something cannot be determined from the image,
say "unclear".
"""

    response = client.responses.create(

        model=os.getenv(
            "VISION_MODEL",
            "gpt-5.6"
        ),

        input=[
            {
                "role": "user",
                "content": [

                    {
                        "type": "input_text",
                        "text": prompt
                    },

                    {
                        "type": "input_image",
                        "image_url":
                        f"data:{file.content_type};base64,{encoded_image}"
                    }

                ]
            }
        ]
    )

    try:

        return json.loads(
            response.output_text
        )

    except Exception:

        return {
            "analysis":
            response.output_text
         }
