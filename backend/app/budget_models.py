import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal

_DATE_RE = re.compile(r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$')


AccountType = Literal["debit", "credit", "savings", "cash", "foreign", "invest", "deposit", "card", "other"]


# ── Auth ──────────────────────────────────────────────────────────────────────

class AuthRequest(BaseModel):
    user_id:  str
    pin_hash: str


class AuthResponse(BaseModel):
    token:   str
    user_id: str
    name:    str


# ── Accounts ──────────────────────────────────────────────────────────────────

class AccountCreate(BaseModel):
    name:       str
    type:       AccountType = "card"
    sort_order: int = 0


class AccountUpdate(BaseModel):
    name:       Optional[str]         = None
    type:       Optional[AccountType] = None
    sort_order: Optional[int]         = None
    is_active:  Optional[bool]        = None


class AccountOut(BaseModel):
    id:         str
    user_id:    str
    name:       str
    type:       str
    sort_order: int
    is_active:  bool


# ── Periods ───────────────────────────────────────────────────────────────────

class PeriodCreate(BaseModel):
    start_date: str  # YYYY-MM-DD

    @field_validator('start_date')
    @classmethod
    def validate_start_date(cls, v: str) -> str:
        if not _DATE_RE.match(v):
            raise ValueError('Date must be in YYYY-MM-DD format')
        return v


class PeriodOut(BaseModel):
    id:         str
    user_id:    str
    start_date: str
    end_date:   Optional[str] = None
    is_active:  bool


# ── Balances ──────────────────────────────────────────────────────────────────

class BalanceSet(BaseModel):
    account_id:      str
    balance_start:   float = 0.0
    balance_current: float = 0.0


class BalanceOut(BaseModel):
    id:              str
    account_id:      str
    period_id:       str
    balance_start:   float
    balance_current: float
    updated_at:      str


class AdvanceAdd(BaseModel):
    account_id: str
    amount:     float = Field(..., gt=0)


# ── Income ────────────────────────────────────────────────────────────────────

class IncomeCreate(BaseModel):
    amount:   float = Field(..., gt=0)
    date:     str   # YYYY-MM-DD
    category: str = "Прочее"
    note:     str = ""

    @field_validator('date')
    @classmethod
    def validate_date(cls, v: str) -> str:
        if not _DATE_RE.match(v):
            raise ValueError('Date must be in YYYY-MM-DD format')
        return v


class IncomeOut(BaseModel):
    id:        str
    user_id:   str
    period_id: str
    amount:    float
    date:      str
    category:  str
    note:      str


# ── Transfers ─────────────────────────────────────────────────────────────────

class TransferCreate(BaseModel):
    from_account_id: str
    to_account_id:   str
    amount:          float = Field(..., gt=0)


class TransferOut(BaseModel):
    id:              str
    user_id:         str
    period_id:       str
    from_account_id: str
    to_account_id:   str
    amount:          float
    date:            str
