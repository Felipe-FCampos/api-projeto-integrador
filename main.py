# main.py
from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

import models, schemas
from database import engine, SessionLocal, Base

from passlib.context import CryptContext

# -------------------------------------------------------------------
#  Inicialização do banco (cria as tabelas, se ainda não existirem)
# -------------------------------------------------------------------
Base.metadata.create_all(bind=engine)

app = FastAPI()

# -------------------------------------------------------------------
#  Contexto para hash de senhas (usando bcrypt)
# -------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# -------------------------------------------------------------------
#  Dependência para obter a sessão do DB em cada request
# -------------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------------------------------------------
#  Endpoint para cadastrar novo usuário
# -------------------------------------------------------------------
@app.post("/users/", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1) Verifica se já existe um usuário com mesmo e-mail
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado."
        )

    hashed_pwd = hash_password(user_in.password)
    user = models.User(
        nome=user_in.nome,
        email=user_in.email,
        hashed_password=hashed_pwd
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@app.get("/users/", response_model=schemas.UserOut)
def get_user(
    email: str = Query(..., description="Email do usuário para login"),
    password: str = Query(..., description="Senha em texto puro para validação"),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )

    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha inválida."
        )

    return user

