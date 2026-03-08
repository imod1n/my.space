from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class Category(str, Enum):
    communal    = "Коммунальные"
    electricity = "Электричество"
    internet    = "Интернет"
    tv          = "Телевидение"
    trash       = "Мусор"
    membership  = "Членские"
    snow        = "Уборка снега"
    other       = "Прочее"

class ObjectName(str, Enum):
    flat1       = "Квартира 1"
    flat2       = "Квартира 2"
    country     = "Загородный дом"
    beach       = "Пляжный домик"


class PaymentCreate(BaseModel):
    category:    Category
    object_name: ObjectName
    amount:      float = Field(..., gt=0)
    date:        str   = Field(..., description="Дата платежа YYYY-MM-DD")
    period:      str   = Field(..., description="Расчётный месяц YYYY-MM")
    note:        Optional[str] = ""


class PaymentUpdate(BaseModel):
    category:    Optional[Category]    = None
    object_name: Optional[ObjectName]  = None
    amount:      Optional[float]       = Field(None, gt=0)
    date:        Optional[str]         = None
    period:      Optional[str]         = None
    note:        Optional[str]         = None


class PaymentOut(BaseModel):
    id:          str
    category:    str
    object_name: str
    amount:      float
    date:        str
    period:      str
    note:        str = ""
