from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.database import get_db
from ..import schemas, models, utils, oauth

router = APIRouter(
    prefix="/users",
    tags=["Users"]
    )


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[schemas.User])
def get_users(db: Session = Depends(get_db), current_user: models.User = Depends(oauth.get_current_user)):
    users = db.query(models.User).all()
    return users    

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.User)
def get_user(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth.get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} not found"
        )

    return user 

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth.get_current_user)):
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} not found"
        )

    user_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT) 

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.User)
def update_user(id: int, user: schemas.UserCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth.get_current_user)):
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    
    user_query = db.query(models.User).filter(models.User.id == id)
    existing_user = user_query.first()

    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} not found"
        )

    user_query.update(user.model_dump(), synchronize_session=False)
    db.commit()

    return user_query.first()