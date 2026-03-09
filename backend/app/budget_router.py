from fastapi import APIRouter, HTTPException, Header, Depends

from . import budget_crud
from .budget_models import (
    AuthRequest, AuthResponse,
    AccountCreate, AccountUpdate, AccountOut,
    PeriodCreate, PeriodOut,
    AdvanceAdd, BalanceSet, BalanceOut,
    IncomeCreate, IncomeOut,
    TransferCreate, TransferOut,
)

router = APIRouter(prefix="/api/budget", tags=["budget"])


# ── Auth dependency ───────────────────────────────────────────────────────────

async def _require_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Authorization header required")
    token   = authorization[7:]
    user_id = await budget_crud.validate_token(token)
    if not user_id:
        raise HTTPException(401, "Invalid or expired token")
    return user_id


def _check_access(token_user: str, path_user: str):
    if token_user != path_user:
        raise HTTPException(403, "Access denied")


# ── Auth ──────────────────────────────────────────────────────────────────────

@router.post("/auth", response_model=AuthResponse)
async def auth(data: AuthRequest):
    result = await budget_crud.authenticate(data.user_id, data.pin_hash)
    if not result:
        raise HTTPException(401, "Invalid credentials")
    return result


# ── Accounts ──────────────────────────────────────────────────────────────────

@router.get("/{user_id}/accounts", response_model=list[AccountOut])
async def list_accounts(user_id: str, current: str = Depends(_require_token)):
    _check_access(current, user_id)
    return await budget_crud.get_accounts(user_id)


@router.post("/{user_id}/accounts", response_model=AccountOut, status_code=201)
async def add_account(user_id: str, data: AccountCreate, current: str = Depends(_require_token)):
    _check_access(current, user_id)
    return await budget_crud.create_account(user_id, data)


@router.put("/{user_id}/accounts/{account_id}", response_model=AccountOut)
async def edit_account(
    user_id: str, account_id: str, data: AccountUpdate,
    current: str = Depends(_require_token),
):
    _check_access(current, user_id)
    result = await budget_crud.update_account(account_id, data)
    if not result:
        raise HTTPException(404, "Account not found")
    return result


@router.delete("/{user_id}/accounts/{account_id}")
async def remove_account(user_id: str, account_id: str, current: str = Depends(_require_token)):
    _check_access(current, user_id)
    if not await budget_crud.delete_account(account_id):
        raise HTTPException(404, "Account not found")
    return {"deleted": True}


# ── Periods ───────────────────────────────────────────────────────────────────

@router.get("/{user_id}/periods", response_model=list[PeriodOut])
async def list_periods(user_id: str, current: str = Depends(_require_token)):
    _check_access(current, user_id)
    return await budget_crud.get_periods(user_id)


@router.get("/{user_id}/periods/active", response_model=PeriodOut)
async def active_period(user_id: str, current: str = Depends(_require_token)):
    _check_access(current, user_id)
    result = await budget_crud.get_active_period(user_id)
    if not result:
        raise HTTPException(404, "No active period")
    return result


@router.post("/{user_id}/periods", response_model=PeriodOut, status_code=201)
async def new_period(user_id: str, data: PeriodCreate, current: str = Depends(_require_token)):
    _check_access(current, user_id)
    return await budget_crud.create_period(user_id, data.start_date)


@router.delete("/{user_id}/periods/{period_id}", response_model=PeriodOut | None)
async def remove_period(user_id: str, period_id: str, current: str = Depends(_require_token)):
    _check_access(current, user_id)
    result = await budget_crud.delete_period(user_id, period_id)
    if result is None:
        raise HTTPException(404, "Period not found")
    return result


# ── Balances ──────────────────────────────────────────────────────────────────

@router.get("/{user_id}/periods/{period_id}/balances", response_model=list[BalanceOut])
async def list_balances(user_id: str, period_id: str, current: str = Depends(_require_token)):
    _check_access(current, user_id)
    return await budget_crud.get_balances(user_id, period_id)


@router.post("/{user_id}/periods/{period_id}/balances", response_model=BalanceOut)
async def set_balance(
    user_id: str, period_id: str, data: BalanceSet,
    current: str = Depends(_require_token),
):
    _check_access(current, user_id)
    return await budget_crud.upsert_balance(user_id, period_id, data)


@router.post("/{user_id}/periods/{period_id}/advance", response_model=BalanceOut)
async def apply_advance(
    user_id: str, period_id: str, data: AdvanceAdd,
    current: str = Depends(_require_token),
):
    _check_access(current, user_id)
    return await budget_crud.add_advance(user_id, period_id, data)


# ── Income ────────────────────────────────────────────────────────────────────

@router.get("/{user_id}/periods/{period_id}/income", response_model=list[IncomeOut])
async def list_income(user_id: str, period_id: str, current: str = Depends(_require_token)):
    _check_access(current, user_id)
    return await budget_crud.get_income(user_id, period_id)


@router.post("/{user_id}/periods/{period_id}/income", response_model=IncomeOut, status_code=201)
async def add_income(
    user_id: str, period_id: str, data: IncomeCreate,
    current: str = Depends(_require_token),
):
    _check_access(current, user_id)
    return await budget_crud.create_income(user_id, period_id, data)


@router.delete("/{user_id}/income/{income_id}")
async def remove_income(user_id: str, income_id: str, current: str = Depends(_require_token)):
    _check_access(current, user_id)
    if not await budget_crud.delete_income(income_id):
        raise HTTPException(404, "Income not found")
    return {"deleted": True}


# ── Transfers ─────────────────────────────────────────────────────────────────

@router.get("/{user_id}/periods/{period_id}/transfers", response_model=list[TransferOut])
async def list_transfers(user_id: str, period_id: str, current: str = Depends(_require_token)):
    _check_access(current, user_id)
    return await budget_crud.get_transfers(user_id, period_id)


@router.post("/{user_id}/periods/{period_id}/transfers", response_model=TransferOut, status_code=201)
async def add_transfer(
    user_id: str, period_id: str, data: TransferCreate,
    current: str = Depends(_require_token),
):
    _check_access(current, user_id)
    return await budget_crud.create_transfer(user_id, period_id, data)


@router.delete("/{user_id}/transfers/{transfer_id}")
async def remove_transfer(user_id: str, transfer_id: str, current: str = Depends(_require_token)):
    _check_access(current, user_id)
    if not await budget_crud.delete_transfer(transfer_id):
        raise HTTPException(404, "Transfer not found")
    return {"deleted": True}
