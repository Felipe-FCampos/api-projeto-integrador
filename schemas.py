from pydantic import BaseModel, EmailStr, ValidationError

class UserCreate(BaseModel):
    nome: str
    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "example": {
                "nome": "Maria Silva",
                "email": "maria@example.com",
                "password": "senhaSegura123"
            }
        }


class UserOut(BaseModel):
    id: int
    nome: str
    email: EmailStr

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "maria@example.com",
                "password": "senhaSegura123"
            }
        }

