from fastapi import Depends, FastAPI, HTTPException, File, UploadFile, Response, status
from sqlalchemy.orm import Session

from bo.upload_bo import UploadBo

from sql import crud, models, schemas
from sql.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get('/')
def hello_world():
    return {'message': 'Hello, World!'}


@app.post('/api/docx2pdf', status_code=status.HTTP_200_OK)
async def docx2pdf(doc: UploadFile = File(...), image: UploadFile = File(...)):
    arquivo_doc = doc.file.read()
    arquivo_image = image.file.read()

    retorno = await UploadBo.convert_to(arquivo_doc, arquivo_image)

    return Response(content=retorno,
                    media_type="application/pdf",
                    headers={"Content-Disposition": "attachment; filename=arquivo.pdf"})


@app.post('/api/replace_string')
async def replace_string(tags: str, values: str, file: UploadFile = File(...)):
    arquivo = file.file.read()

    retorno = await UploadBo.replaceString(arquivo, tags, values)
    
    return Response(content=retorno,
                    media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    headers={"Content-Disposition": "attachment; filename=arquivo.docx"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0',port=8000, reload=True)