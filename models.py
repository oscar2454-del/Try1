from pydantic import BaseModel, Field

class Estudiante(BaseModel):
    nombre: str = Field(min_length=1, max_length=50)