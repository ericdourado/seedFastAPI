import datetime
from typing import Optional, List
from pydantic import BaseModel as SCBaseModel, EmailStr
from datetime import datetime

class UsuarioSchemaBase(SCBaseModel):
    id: Optional[int]
    nome: str
    email: str
    criado_em: Optional[datetime]
    atualizado_em: Optional[datetime]

    class Config:
        orm_mode = True

class UsuarioSchemaCreate(UsuarioSchemaBase):
    senha: str

    class Config:
        orm_mode = True


class LoginData(SCBaseModel):
    email: EmailStr
    senha: str
    


