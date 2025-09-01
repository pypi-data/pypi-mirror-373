from dataclasses import dataclass

@dataclass
class DeFiEvent:
    network: str
    block_number: int
    tx_id: str
    log_index: int

    @property
    def name(self) -> str:
        return self.__class__.__name__

@dataclass
class CommonSwapEvent(DeFiEvent):
    pool_address: str
    swapper: str
    recipient: str
    tokenSold: str
    tokenBought: str
    amountSold: float
    amountBought: float

@dataclass
class CommonPoolPairWithdrawEvent(DeFiEvent):
    pool_address: str
    amount0: float
    amount1: float
    token0: str
    token1: str

@dataclass
class CommonPoolPairDepositEvent(DeFiEvent):
    pool_address: str
    amount0: float
    amount1: float
    token0: str
    token1: str

@dataclass
class TokenIssueEvent(DeFiEvent):
    token: str
    amount: float

@dataclass
class TokenRedeemEvent(DeFiEvent):
    token: str
    amount: float

@dataclass
class TokenTransferEvent(DeFiEvent):
    token: str
    sender: str
    receiver: str
    amount: float


@dataclass
class CommonLendingEvent(DeFiEvent):
    user: str
    token: str
    amount: float
