from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import openai
import os
import json
from dotenv import load_dotenv

# 1. Load the environment variables BEFORE setting up OpenAI
load_dotenv()

# 2. Setup the application
app = FastAPI(title="Smart Camera Monitor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Initialize OpenAI client (It will now successfully find the key)
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 4. The AI Instructions
CAMERA_PROMPT = """You are a smart security camera assistant.
Analyze the image and respond with a valid JSON object containing:
{
  "notable_objects": ["list", "of", "things", "in", "view"],
  "description": "Clear, concise description of the scene.",
  "alert_needed": true or false (true only if someone is approaching or something unusual happens),
  "spoken_summary": "A short, natural sentence summarizing the scene to be read aloud (e.g., 'A car just passed by' or 'Nothing moving')."
}"""

class ImagePayload(BaseModel):
    image_base64: str

# 5. The Web Interface
@app.get("/", response_class=HTMLResponse)
async def home_interface():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Camera Monitor</title>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
                background: #f4f4f9; 
                color: #333; 
                margin: 0; 
                padding: 15px; 
                display: flex; 
                flex-direction: column; 
                align-items: center; 
            }
            .camera-box { 
                background: #fff; 
                padding: 10px; 
                border-radius: 12px; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
                width: 100%; 
                max-width: 600px; 
                margin-bottom: 20px; 
                box-sizing: border-box;
            }
            video { 
                width: 100%; 
                border-radius: 8px; 
                background: #000; 
            }
            .controls { 
                display: flex; 
                justify-content: center; 
                margin-top: 15px; 
            }
            button { 
                padding: 12px 24px; 
                background: #007bff; 
                color: white; 
                border: none; 
                border-radius: 8px; 
                font-size: 16px; 
                cursor: pointer; 
                transition: background 0.2s; 
                width: 100%;
                font-weight: 600;
            }
            button.active { 
                background: #dc3545; 
            }
            .log-box { 
                background: #fff; 
                padding: 15px; 
                border-radius: 12px; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
                width: 100%; 
                max-width: 600px; 
                height: 300px; 
                overflow-y: auto; 
                box-sizing: border-box;
            }
            .log-entry { 
                margin-bottom: 12px; 
                padding-bottom: 12px; 
                border-bottom: 1px solid #eee; 
                font-size: 14px; 
                line-height: 1.5;
            }
            .log-entry:last-child { 
                border-bottom: none; 
            }
            .time-stamp {
                color: #666;
                font-size: 12px;
                margin-bottom: 4px;
            }
            .alert-badge { 
                background: #ffeeba; 
                color: #856404; 
                padding: 2px 6px; 
                border-radius: 4px; 
                font-size: 12px; 
                font-weight: bold;
                display: inline-block;
                margin-bottom: 5px;
            }
            canvas { display: none; }
        </style>
    </head>
    <body>
        <div class="camera-box">
            <video id="video" autoplay playsinline muted></video>
            <div class="controls">
                <button id="toggleBtn">Start Monitoring</button>
            </div>
        </div>
        
        <div class="log-box" id="logArea">
            <div class="log-entry">Waiting to start...</div>
        </div>

        <canvas id="canvas"></canvas>

        <script>
            const video = document.getElementById('video');
            const canvas = document.getElementById('canvas');
            const btn = document.getElementById('toggleBtn');
            const logArea = document.getElementById('logArea');
            let isMonitoring = false;

            async function setupCamera() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
                    video.srcObject = stream;
                } catch (err) {
                    logArea.innerHTML = `<div class="log-entry"><strong>Error:</strong> Could not access camera. Please check permissions.</div>`;
                }
            }

            function speak(text) {
                if (!text) return;
                const utterance = new SpeechSynthesisUtterance(text);
                window.speechSynthesis.speak(utterance);
            }

            async function analyzeFrame() {
                if (!isMonitoring) return;
                
                const ctx = canvas.getContext('2d');
                canvas.width = video.videoWidth; 
                canvas.height = video.videoHeight;
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                
                const base64Image = canvas.toDataURL('image/jpeg', 0.8).split(',')[1];

                try {
                    const response = await fetch('/analyze', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ image_base64: base64Image })
                    });
                    
                    const result = await response.json();
                    
                    const timeString = new Date().toLocaleTimeString();
                    const alertHtml = result.alert_needed ? `<div class="alert-badge">⚠️ ALERT</div>` : '';
                    const logHtml = `
                        <div class="log-entry">
                            <div class="time-stamp">${timeString}</div>
                            ${alertHtml}
                            <div>${result.description}</div>
                            <div style="color: #666; font-size: 12px; margin-top: 4px;">Seen: ${result.notable_objects.join(', ')}</div>
                        </div>
                    `;
                    
                    logArea.innerHTML = logHtml + logArea.innerHTML;

                    if (result.spoken_summary) {
                        speak(result.spoken_summary);
                    }

                } catch (error) {
                    console.error("Analysis failed:", error);
                }
                
                setTimeout(analyzeFrame, 4000);
            }

            btn.addEventListener('click', () => {
                isMonitoring = !isMonitoring;
                
                if (isMonitoring) {
                    btn.innerText = "Stop Monitoring";
                    btn.classList.add('active');
                    speak("Monitoring started.");
                    logArea.innerHTML = '<div class="log-entry">Analysis running. Waiting for first result...</div>';
                    analyzeFrame();
                } else {
                    btn.innerText = "Start Monitoring";
                    btn.classList.remove('active');
                    speak("Monitoring paused.");
                }
            });

            setupCamera();
        </script>
    </body>
    </html>
    """

# 6. The API Endpoint for Image Analysis
@app.post("/analyze")
async def analyze(req: ImagePayload):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": CAMERA_PROMPT},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{req.image_base64}", "detail": "high"}},
                    {"type": "text", "text": "What do you see?"}
                ]}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Server Error during analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to process image.")