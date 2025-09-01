from dataclasses import dataclass

from defisocket.event_models.base import CommonLendingEvent, DeFiEvent

@dataclass
class AaveV3DepositEvent(CommonLendingEvent):
    on_behalf_of: str
    referral_code: int

@dataclass
class AaveV3WithdrawEvent(CommonLendingEvent):
    recipient: str

@dataclass
class AaveV3BorrowEvent(CommonLendingEvent):
    on_behalf_of: str
    interest_rate_mode: int
    borrow_rate: float
    referral_code: int

@dataclass
class AaveV3RepayEvent(CommonLendingEvent):
    repayer: str
    use_a_tokens: bool

@dataclass
class AaveV3FlashLoanEvent(CommonLendingEvent):
    target: str
    interest_rate_mode: int
    premium: int
    referral_code: int

@dataclass
class AaveV3LiquidationCallEvent(DeFiEvent):
    owner: str
    liquidator: str
    debt_token: str
    collateral_token: str
    debt_to_cover: int
    liquidated_collateral_amount: int
    receive_a_token: bool

