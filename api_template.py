from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Definición del modelo de usuario
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "fecha_registro": self.fecha_registro
        }

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[str] = None

    
# Crear las tablas en la base de datos por primera vez
Base.metadata.create_all(bind=engine)


app = FastAPI()

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
@app.post("/usuarios")
def crear_usuario(nombre: str, email: str, db: Session = Depends(get_db)):
    fecha_registro = datetime.utcnow()
    usuario = Usuario(nombre=nombre, email=email, fecha_registro=fecha_registro)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario.to_dict()

@app.get("/usuarios")
def obtener_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).all()
    return [usuario.to_dict() for usuario in usuarios]

@app.put("/usuarios/{usuario_id}")
def actualizar_usuario(usuario_id: int, usuario: UsuarioUpdate, db: Session = Depends(get_db)):
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db_usuario.nombre = usuario.nombre
    db_usuario.email = usuario.email
    db.commit()
    db.refresh(db_usuario)
    return db_usuario.to_dict()

@app.patch("/usuarios/{usuario_id}")
def actualizar_usuario_parcial(usuario_id: int, usuario: UsuarioUpdate, db: Session = Depends(get_db)):
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if usuario.nombre is not None:
        db_usuario.nombre = usuario.nombre
    if usuario.email is not None:
        db_usuario.email = usuario.email
    db.commit()
    db.refresh(db_usuario)
    return db_usuario.to_dict()


@app.delete("/usuarios/{usuario_id}")
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(db_usuario)
    db.commit()
    return {"message": "Usuario eliminado correctamente"}

# ======================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
    