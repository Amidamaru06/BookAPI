from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from .. import models, schemas

from..database import get_db

router = APIRouter(prefix="/books", tags=["books"])