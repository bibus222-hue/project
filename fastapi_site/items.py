from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app import crud, schemas, models
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/items", tags=["items"])

@router.post("/", response_model=schemas.Item, status_code=status.HTTP_201_CREATED)
def create_item(
    item: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Создать новый товар
    """
    return crud.create_user_item(db=db, item=item, user_id=current_user.id)

@router.get("/", response_model=List[schemas.Item])
def read_items(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Поиск по названию и описанию"),
    db: Session = Depends(get_db)
):
    """
    Получить список товаров
    """
    items = crud.get_items(db, skip=skip, limit=limit, search=search)
    return items

@router.get("/my-items", response_model=List[schemas.Item])
def read_user_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получить товары текущего пользователя
    """
    items = crud.get_user_items(db, user_id=current_user.id, skip=skip, limit=limit)
    return items

@router.get("/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    """
    Получить товар по ID
    """
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return db_item

@router.put("/{item_id}", response_model=schemas.Item)
def update_item(
    item_id: int,
    item_update: schemas.ItemUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Обновить товар
    """
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    if db_item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    return crud.update_item(db, item_id=item_id, item_update=item_update)

@router.delete("/{item_id}", response_model=schemas.Item)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Удалить товар
    """
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    if db_item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    return crud.delete_item(db, item_id=item_id)