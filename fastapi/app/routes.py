from fastapi import APIRouter
from app.models import Item

router = APIRouter(prefix="/items", tags=["Items"])

# Sample GET
@router.get("/")
def read_items():
    return [{"id": 1, "name": "Item A"}, {"id": 2, "name": "Item B"}]

# Sample POST
@router.post("/")
def create_item(item: Item):
    return {"message": "Item received", "item": item}