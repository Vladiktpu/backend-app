from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, Message
from schemas import MessageCreate, MessageResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Учебный backend-проект")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/messages", response_model=MessageResponse)
def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    if not message.text.strip():
        raise HTTPException(status_code=400, detail="Пустое сообщение")
    db_message = Message(text=message.text)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

@app.get("/messages")
def get_messages(db: Session = Depends(get_db)):
    return db.query(Message).all()
