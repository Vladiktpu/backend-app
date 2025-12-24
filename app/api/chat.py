from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.api import deps
from app.core.config import settings
from app.db.database import get_db
from app.db.models import User, ChatSession, Message
from app.schemas.chat import ChatSession as ChatSessionSchema, ChatHistory, MessageCreate, Message as MessageSchema
from app.services.bot import bot_service
from jose import jwt, JWTError

router = APIRouter()

@router.post("/sessions", response_model=ChatSessionSchema)
async def create_session(
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    session = ChatSession(user_id=current_user.id)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session

@router.get("/sessions", response_model=List[ChatSessionSchema])
async def get_sessions(
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(ChatSession).where(ChatSession.user_id == current_user.id))
    return result.scalars().all()

@router.get("/sessions/{session_id}", response_model=ChatHistory)
async def get_session_history(
    session_id: int,
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(ChatSession.id == session_id)
    )
    session = result.scalars().first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this session")
    
    return session

async def get_current_user_ws(
    token: str,
    db: AsyncSession
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: int,
    token: Annotated[str, Query()],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    await websocket.accept()
    
    user = await get_current_user_ws(token, db)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    session = result.scalars().first()
    
    if not session or session.user_id != user.id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        while True:
            data = await websocket.receive_json()
            message_text = data.get("content")
            
            if not message_text or not message_text.strip():
                await websocket.send_json({"error": "Message cannot be empty"})
                continue
            
        
            user_message = Message(
                session_id=session_id,
                content=message_text,
                is_from_user=True
            )
            db.add(user_message)
            await db.commit() 
            
           
            bot_response_text = bot_service.get_response(message_text)
            bot_message = Message(
                session_id=session_id,
                content=bot_response_text,
                is_from_user=False
            )
            db.add(bot_message)
            await db.commit()
            
           
            await websocket.send_json({
                "role": "bot",
                "content": bot_response_text,
                "timestamp": str(bot_message.created_at)
            })
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        
        print(f"WebSocket error: {e}")
        await websocket.close()
