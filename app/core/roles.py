from fastapi import Depends, HTTPException
from typing import List, Dict, Any
from core.security import get_current_active_user


