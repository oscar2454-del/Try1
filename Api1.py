import io
from datetime import datetime
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from bson import ObjectId
import pandas as pd

# Importaciones de tu configuración local
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

# Servir el HTML
@app.get("/", response_class=HTMLResponse)
async def home():
    with open("templates/base.html", "r", encoding="utf-8") as f:
        return f.read()

# CRUD Estudiantes
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
    res = await collection.insert_one({"nombre": nombre})
    return {"id": str(res.inserted_id), "nombre": nombre}

@app.delete("/eliminar/{id}")
async def eliminar(id: str):
    await collection.delete_one({"_id": ObjectId(id)})
    await db.asistencias.delete_many({"estudiante_id": id})
    return {"mensaje": "borrado"}

# Lógica de Asistencia
@app.post("/asistencia")
async def registrar_asistencia(estudiante_id: str = Form(...), estado: str = Form(...)):
    hoy = datetime.now().strftime("%Y-%m-%d")
    await db.asistencias.update_one(
        {"estudiante_id": estudiante_id, "fecha": hoy},
        {"$set": {"estado": estado, "timestamp": datetime.now()}},
        upsert=True
    )
    return {"status": "ok"}

# Exportar a Excel
@app.get("/exportar-excel")
async def exportar_excel():
    est_cursor = collection.find({})
    nombres = {str(e["_id"]): e["nombre"] async for e in est_cursor}
    
    asis_cursor = db.asistencias.find({})
    data = []
    async for a in asis_cursor:
        data.append({
            "Estudiante": nombres.get(a["estudiante_id"], "Desconocido"),
            "Fecha": a["fecha"],
            "Estado": a["estado"].capitalize()
        })
    
    if not data:
        raise HTTPException(status_code=404, detail="No hay datos de asistencia")

    df = pd.DataFrame(data)
    # Formato de matriz: Alumnos en filas, Fechas en columnas
    df_pivot = df.pivot(index="Estudiante", columns="Fecha", values="Estado").fillna("-")

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_pivot.to_excel(writer, sheet_name='Asistencias')
    
    output.seek(0)
    return StreamingResponse(
        output, 
        headers={'Content-Disposition': 'attachment; filename="asistencia_clase.xlsx"'},
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )