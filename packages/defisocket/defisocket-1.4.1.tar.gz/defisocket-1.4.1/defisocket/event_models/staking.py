from dataclasses import dataclass

from defisocket.event_models.base import DeFiEvent

@dataclass
class LidoWithdrawalRequestEvent(DeFiEvent):
    network: str
    block_number: int
    tx_id: str
    request_id: str
    requestor: str
    owner: str
    burned_token: str
    burned_amount: float

@dataclass
class LidoWithdrawalClaimedEvent(DeFiEvent):
    network: str
    block_number: int
    tx_id: str
    request_id: str
    owner: str
    receiver: str
    withdraw_token: str
    withdraw_amount: float
    burned_token: str

@dataclass
class LidoDepositEvent(DeFiEvent):
    network: str
    block_number: int
    tx_id: str
    sender: str
    referral: str
    minted_amount: float
    minted_token: str

@dataclass
class LidoL2DepositEvent(DeFiEvent):
    network: str
    block_number: int
    tx_id: str
    sender: str
    receiver: str
    minted_amount: float
    minted_token: str

@dataclass
class LidoL2WithdrawalRequestEvent(DeFiEvent):
    network: str
    block_number: int
    tx_id: str
    sender: str
    receiver: str
    burned_amount: float
    burned_token: str

@dataclass
class BinanceBurnEvent(DeFiEvent):
    network: str
    tx_id: str
    block_number: int
    user: str
    burned_token: str
    burned_amount: float

@dataclass
class BinanceWithdrawalRequestEvent(DeFiEvent):
    network: str
    tx_id: str
    block_number: int
    user: str
    withdraw_token: str
    withdraw_amount: float
    burned_token: str
    burned_amount: float

@dataclass
class BinanceDepositEvent(DeFiEvent):
    network: str
    tx_id: str
    block_number: int
    user: str
    referral: str
    deposit_token: str
    deposit_amount: float
    minted_token: str
    minted_amount: float

@dataclass
class CoinbaseTokenBurnEvent(DeFiEvent):
    network: str
    block_number: int
    tx_id: str
    user: str
    burned_amount: float
    burned_token: str

@dataclass
class CoinbaseTokenMintEvent(DeFiEvent):
    network: str
    block_number: int
    tx_id: str
    user: str
    receipient: str
    minted_amount: float
    minted_token: str

@dataclass
class TBTCWithdrawalRequestEvent(DeFiEvent):
    network: str
    block_number: int
    tx_id: str
    wallet_pubkey: str
    redeemer_output_script: str
    user: str
    burned_token: str
    burned_amount: float
    treasury_fee: float
    tx_max_fee: float

@dataclass
class TBTCWithdrawalEvent(DeFiEvent):
    network: str
    block_number: int
    tx_id: str
    source: str
    burned_token: str
    burned_amount: float

@dataclass
class TBTCDepositRequestEvent(DeFiEvent):
    network: str
    block_number: int
    tx_id: str
    funding_tx: str
    funding_output_index: int
    user: str
    vault: str
    minted_token: str
    minted_amount: float
    blinding_factor: float
    wallet_pubkey: str
    refund_pubkey: str
    refund_locktime: float

@dataclass
class TBTCDepositEvent(DeFiEvent):
    network: str
    block_number: int
    tx_id: str
    receiver: str
    minted_token: str
    minted_amount: float

@dataclass
class THUSDDepositEvent(DeFiEvent):
    network: str
    block_number: int
    tx_id: str
    user: str
    deposit_amount: float
    deposit_token: str
    collateral_token: str
    minted_amount: float

@dataclass
class THUSDWithdrawEvent(DeFiEvent):
    network: str
    block_number: int
    tx_id: str
    user: str
    withdraw_amount: float
    withdraw_token: str
    collateral_amount: float
    collateral_token: str
    burned_amount: float

@dataclass
class StaderWithdrawalRequestEvent(DeFiEvent):
    network: str
    tx_id: str
    block_number: int
    request_id: str
    requester: str
    recipient: str
    withdraw_amount: float
    withdraw_token: str
    burned_amount: float
    burned_token: str

@dataclass
class StaderEthXWithdrawalEvent(DeFiEvent):
    network: str
    tx_id: str
    block_number: int
    requester: str
    recipient: str
    withdraw_amount: float
    withdraw_token: str
    burned_token: str

@dataclass
class StaderEthXDepositEvent(DeFiEvent):
    network: str
    tx_id: str
    block_number: int
    requester: str
    owner: str
    deposit_token: str
    deposit_amount: float
    minted_token: str
    minted_amount: float
