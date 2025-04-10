from fastapi import APIRouter, HTTPException


router = APIRouter()


@router.get('/router/user')
def get_user_data():
    return "dummy routing test"

