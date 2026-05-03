from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from db import collection
import os

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def home():
    return {"ok": True}

#Obtener
@app.get("/estudiantes")
async def obtener_estudiantes():
    datos = []

    try:
        cursor = collection.find({}).sort("_id", -1)

        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            datos.append(doc)

        return datos

    except Exception:
        return {"error": "Error al obtener datos"}


#Agregar
@app.post("/agregar")
async def agregar_estudiante(nombre: str = Form(...)):
    nombre = nombre.strip()

    if not nombre:
        return {"error": "Nombre vacío"}

    if len(nombre) > 50:
        return {"error": "Nombre demasiado largo"}

    try:
        result = await collection.insert_one({"nombre": nombre})

        return {
            "mensaje": "ok",
            "id": str(result.inserted_id),
            "nombre": nombre
        }

    except Exception:
        return {"error": "Error al guardar"}