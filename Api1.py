from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from bson import ObjectId
from datetime import datetime

from db import collection, db 
from models import Estudiante

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def home():
    # Retorna el HTML que definimos abajo
    with open("templates/base.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/estudiantes")
async def obtener():
    datos = []
    cursor = collection.find({}).sort("nombre", 1)
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        datos.append(doc)
    return datos

@app.post("/agregar")
async def agregar(nombre: str = Form(...)):
    nombre = nombre.strip()
    if not nombre:
        raise HTTPException(status_code=400, detail="Nombre vacío")
    estudiante = Estudiante(nombre=nombre)
    result = await collection.insert_one(estudiante.dict())
    return {"id": str(result.inserted_id), "nombre": nombre}

@app.delete("/eliminar/{id}")
async def eliminar(id: str):
    await collection.delete_one({"_id": ObjectId(id)})
    await db.asistencias.delete_many({"estudiante_id": id})
    return {"mensaje": "eliminado"}

@app.post("/asistencia")
async def registrar_asistencia(estudiante_id: str = Form(...), estado: str = Form(...)):
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")

    await db.asistencias.update_one(
        {"estudiante_id": estudiante_id, "fecha": fecha_hoy},
        {
            "$set": {
                "estado": estado,
                "ultimo_cambio": datetime.now()
            }
        },
        upsert=True
    )
    return {"status": "ok", "fecha": fecha_hoy}