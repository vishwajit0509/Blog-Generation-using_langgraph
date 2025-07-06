import requests

API_URL = "http://localhost:8000/blogs"

# ---------- CASE 1: Text → Text ----------
data1 = {
    "input_type": "text",
    "output_type": "text",
    "text_input": "Agentic AI",
    "language": "english"
}
res1 = requests.post(API_URL, data=data1)
print("📝 Text → Text:", res1.status_code, res1.json())

# ---------- CASE 2: Text → Voice ----------
data2 = {
    "input_type": "text",
    "output_type": "voice",
    "text_input": "Agentic AI",
    "language": "french"
}
res2 = requests.post(API_URL, data=data2)
print("📝 Text → 🔊 Voice:", res2.status_code, res2.json())

# ---------- CASE 3: Voice → Text ----------
data3 = {
    "input_type": "voice",
    "output_type": "text",
    "language": "hindi"
}
files3 = {
    "voice_input": ("agentic_ai.mp3", open("./voice_inputs/agentic_ai.mp3", "rb"), "audio/mpeg")
}
res3 = requests.post(API_URL, data=data3, files=files3)
print("🔊 Voice → 📝 Text:", res3.status_code)
try:
    print(res3.json())
except Exception:
    print("Response was not JSON")

# ---------- CASE 4: Voice → Voice ----------
data4 = {
    "input_type": "voice",
    "output_type": "voice",
    "language": "german"
}
files4 = {
    "voice_input": ("ethical_ai.mp3", open("./voice_inputs/ethical_ai.mp3", "rb"), "audio/mpeg")
}
res4 = requests.post(API_URL, data=data4, files=files4)
print("🔊 Voice → 🔊 Voice:", res4.status_code)
# Save the voice output file (optional)
if res4.status_code == 200:
    with open("generated_voice_output.mp3", "wb") as f:
        f.write(res4.content)
        print("✅ Saved voice output as generated_voice_output.mp3")
