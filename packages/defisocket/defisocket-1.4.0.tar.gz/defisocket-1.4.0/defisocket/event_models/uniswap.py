from dataclasses import dataclass

from defisocket.event_models.base import CommonPoolPairDepositEvent, CommonPoolPairWithdrawEvent, CommonSwapEvent, DeFiEvent


@dataclass
class UniswapV3PoolSwapEvent(CommonSwapEvent):
    sqrt_based_price: float
    liquidity: int
    tick: int

@dataclass
class UniswapV3PoolWithdrawEvent(CommonPoolPairDepositEvent):
    owner: str
    tick_lower: int
    tick_upper: int
    price_lower: float
    price_upper: float
    pass

@dataclass
class UniswapV3PoolDepositEvent(CommonPoolPairDepositEvent):
    owner: str
    sender: str
    tick_lower: int
    tick_upper: int
    price_lower: float
    price_upper: float

@dataclass
class UniswapV3PoolCollectEvent(CommonPoolPairWithdrawEvent):
    owner: str
    recipient: str
    tick_lower: int
    tick_upper: int
    price_lower: float
    price_upper: float

@dataclass
class UniswapV3NFTPMIncreaseLiquidityEvent(DeFiEvent):
    token_id: int
    liquidity: int
    amount0: int
    amount1: int

@dataclass
class UniswapV3NFTPMDecreaseLiquidityEvent(DeFiEvent):
    token_id: int
    liquidity: int
    amount0: int
    amount1: int

@dataclass
class UniswapV3NFTPMCollectEvent(DeFiEvent):
    token_id: int
    recipient: int
    amount0: int
    amount1: int

@dataclass
class UniswapV3NFTPMTransferEvent(DeFiEvent):
    token_id: int
    sender: str
    receiver: str
