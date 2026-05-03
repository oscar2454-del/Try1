from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from bson import ObjectId

from db import collection
from models import Estudiante

app = FastAPI()

#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#HTML
@app.get("/")
async def home():
    return FileResponse("templates/base.html")


#Obtener
@app.get("/estudiantes")
async def obtener():
    datos = []
    cursor = collection.find({}).sort("_id", -1)

    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        datos.append(doc)

    return datos


#Agregar
@app.post("/agregar")
async def agregar(nombre: str = Form(...)):
    estudiante = Estudiante(nombre=nombre.strip())

    result = await collection.insert_one(estudiante.dict())

    return {
        "id": str(result.inserted_id),
        "nombre": estudiante.nombre
    }


# Eliminar
@app.delete("/eliminar/{id}")
async def eliminar(id: str):
    result = await collection.delete_one({"_id": ObjectId(id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No encontrado")

    return {"mensaje": "eliminado"}


#Editar
@app.put("/editar/{id}")
async def editar(id: str, nombre: str = Form(...)):
    nombre = nombre.strip()

    if not nombre:
        raise HTTPException(status_code=400, detail="Nombre vacío")

    await collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"nombre": nombre}}
    )

    return {"mensaje": "actualizado"}