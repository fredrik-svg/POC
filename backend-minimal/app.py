import os
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI(title="Mini Backend - Vector Stores")

# Tillåt enkel test från valfria origin (skärp i prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/vector-stores")
def create_vs(name: str = Form("kund_sv")):
    vs = client.vector_stores.create(name=name)
    return {"id": vs.id, "name": vs.name}

@app.post("/vector-stores/{vs_id}/files")
async def add_file(vs_id: str, file: UploadFile):
    contents = await file.read()
    up = client.files.create(file=(file.filename, contents), purpose="assistants")
    client.vector_stores.files.create(vector_store_id=vs_id, file_id=up.id)
    return {"ok": True, "file_id": up.id, "vector_store_id": vs_id}
