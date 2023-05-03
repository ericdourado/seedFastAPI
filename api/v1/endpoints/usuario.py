from typing import List
from fastapi import APIRouter, status, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from models.usuario_model import UsuarioModel
from core.deps import get_session
from core.security import gerar_hash_senha, comparar_senha
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from schemas.usuario_schema import *
from core.auth import criar_acess_token, get_current_user

router = APIRouter()


@router.get('/me', response_model=UsuarioSchemaBase)
async def me(usuario = Depends(get_current_user)):
    return usuario
    
    
@router.post('/login')
async def autentica_user(logindata: LoginData,db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(UsuarioModel).filter(UsuarioModel.email == logindata.email)
        result = await session.execute(query)
        usuario: UsuarioSchemaCreate = result.scalars().unique().one_or_none()
    
        if(comparar_senha(logindata.senha, usuario.senha)):
            token = criar_acess_token(str(usuario.id))
            return {
                "usuario": usuario,
                "acess_token":token
                    }
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário não encontrado")    

            
            
@router.post('/signup', status_code=status.HTTP_201_CREATED, response_model=UsuarioSchemaBase)
async def post_usuario(usuario: UsuarioSchemaCreate, db: AsyncSession = Depends(get_session), usuarioLogado = Depends(get_current_user)):
    novo_usuario: UsuarioModel = UsuarioModel(
        nome=usuario.nome, email=usuario.email, senha=gerar_hash_senha(usuario.senha), criado_em = str(datetime.now()), atualizado_em = str(datetime.now()))
    async with db as session:
        try:
            session.add(novo_usuario)
            await session.commit()
            return novo_usuario
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Não foi possivel criar novo usuário')
        
        
@router.get('/', response_model=List[UsuarioSchemaBase])
async def get_usuarios(db: AsyncSession = Depends(get_session), usuarioLogado = Depends(get_current_user)):
    async with db as session:
        query = select(UsuarioModel)
        result = await session.execute(query)
        usuarios: List[UsuarioSchemaBase] = result.scalars().unique().all()
        return usuarios
    
@router.get('/{id}', response_model=UsuarioSchemaBase)
async def get_usuario(id: int, db: AsyncSession = Depends(get_session), usuarioLogado = Depends(get_current_user)):
    async with db as session:
        query = select(UsuarioModel).filter(UsuarioModel.id == id)
        result = await session.execute(query)
        usuario: UsuarioSchemaBase = result.scalars().unique().one_or_none()
        if usuario:
            return usuario
        else:
            raise HTTPException(detail='Usuário não encontrado',
                                status_code=status.HTTP_404_NOT_FOUND)
        
@router.delete('/{id}', status_code= status.HTTP_204_NO_CONTENT)
async def delete_usuario(id: int, db: AsyncSession = Depends(get_session), usuarioLogado = Depends(get_current_user)):
    async with db as session:
        query = select(UsuarioModel).filter(UsuarioModel.id == id)
        result = await session.execute(query)
        usuario: UsuarioModel = result.scalars().unique().one_or_none()
        if usuario:
            await session.delete(usuario)
            await session.commit()
            Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            raise HTTPException(detail='Usuário não encontrado',
                                status_code=status.HTTP_404_NOT_FOUND)
        
@router.put('/{id}', response_model=UsuarioSchemaBase ,status_code= status.HTTP_202_ACCEPTED)
async def put_usuario(id: int, usuario: UsuarioSchemaCreate,db: AsyncSession = Depends(get_session), usuarioLogado = Depends(get_current_user)):
    async with db as session:
        query = select(UsuarioModel).filter(UsuarioModel.id == id)
        result = await session.execute(query)
        usuario_update: UsuarioSchemaCreate = result.scalars().unique().one_or_none()
        if usuario:
            usuario_update.nome = usuario.nome
            usuario_update.email = usuario.email 
            usuario_update.senha = usuario.senha
            usuario_update.atualizado_em = str(datetime.now())
            await session.commit()
            return usuario_update
        else:
            raise HTTPException(detail='Usuário não encontrado',
                                status_code=status.HTTP_404_NOT_FOUND)
        

