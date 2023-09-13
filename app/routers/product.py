from database import get_db
from typing import List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import schemas, models, oauth2, utils
from fastapi import Depends, status, HTTPException, APIRouter, UploadFile, File

router = APIRouter(
    prefix='/products',
    tags=['Products']
)

# Get products
@router.get('/', response_model=List[Union[schemas.ProductResponse, schemas.ProductResponseNoUser]])
async def get_products(user_id: Optional[int] = None,
                       limit: int = 20,
                       skip:int = 0,
                       db: Session = Depends(get_db),
                       current_user= Depends(oauth2.get_optional_current_user)
                       ):

    products = (
                db.query(models.Product)
                .filter(models.Product.available==True)
                .order_by(desc(models.Product.views))
                .limit(limit=limit)
                .offset(skip)
                .all()
                )
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No products not found")
    if current_user:
        response = [schemas.ProductResponse.from_orm(product) for product in products]
    else:
        response = [schemas.ProductResponseNoUser.from_orm(product) for product in products]
    return response

# Get product
@router.get('/{id}', response_model=Union[schemas.ProductResponse, schemas.ProductResponseNoUser])
async def get_product(id,
                       db: Session = Depends(get_db),
                       current_user = Depends(oauth2.get_optional_current_user)
                       ):
    product = db.query(models.Product).filter(and_(models.Product.id == id, models.Product.available==True)).first()

        
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No product not found")
    if current_user:
        response = schemas.ProductResponse.from_orm(product)
    else:
        response = schemas.ProductResponseNoUser.from_orm(product)
        
    if current_user:
        product.views+=1
        db.commit()
        db.refresh(product)
    return response


# Create product listing
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.ProductResponse)
async def create_product(product: schemas.ProductCreate,
                         db: Session = Depends(get_db),
                         current_user = Depends(oauth2.get_current_user)
                ):
    new_product = models.Product(
        user_id=current_user.id, **product.dict())  # Unpcak dictionary
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

# Update product listing
@router.put('/{id}', status_code=status.HTTP_201_CREATED, response_model=schemas.ProductResponse)
async def update_product(id: int,
                         updated_product: schemas.ProductCreate,
                         db: Session = Depends(get_db),
                         current_user = Depends(oauth2.get_current_user)
                   ):
    product_query = db.query(models.Product).filter(models.Product.id == id)
    product = product_query.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product doesnot exixts")
    if product.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access")
    product_query.update(updated_product.dict(), synchronize_session=False)
    db.commit()
    db.refresh(product)
    return product


# Delete product listing
@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(id: int,
                      db: Session = Depends(get_db),
                      current_user = Depends(oauth2.get_current_user)
                      ):

    product_query = db.query(models.Product).filter(
        (models.Product.id == id))
    product = product_query.first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if product.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access")

    product_query.delete(synchronize_session=False)
    db.commit()
