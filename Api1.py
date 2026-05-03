from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from db import collection

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

@app.get("/estudiantes")
async def obtener_estudiantes():
    datos = []
    cursor = collection.find({})

    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        datos.append(doc)

    return datos

@app.post("/agregar")
async def agregar_estudiante(nombre: str = Form(...)):
    data = {"nombre": nombre}
    await collection.insert_one(data)
    return {"mensaje": "ok"}