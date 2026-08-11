from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
import jwt
from .. import models
from ..database import get_db
from .Security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


