from dataclasses import dataclass
from typing import Literal, Optional

@dataclass
class Substream:
    client_name: str
    name: str
    networks: list[str]
    extra_args: Optional[dict] = None

@dataclass
class AaveV3AllEvents(Substream):
    @staticmethod
    def create(networks: list[str], eth_market_type: str = 'Core') -> 'AaveV3AllEvents':
        return AaveV3AllEvents(
            client_name='aave',
            name='aave_v3_all_events',
            networks=networks,
            extra_args={'eth_market_type': eth_market_type}
        )

@dataclass
class UniswapV3PoolAllEvents(Substream):
    @staticmethod
    def create(networks: list[str], symbol0: str, symbol1: str, fee: Literal[100, 500, 3000, 10_000]) -> 'UniswapV3PoolAllEvents':
        return UniswapV3PoolAllEvents(
            client_name='uniswap',
            name='uniswap_v3_pool_all_events',
            networks=networks,
            extra_args={
                'symbol0': symbol0,
                'symbol1': symbol1,
                'fee': fee
            }
        )

@dataclass
class UniswapV3LiquidityEvents(Substream):
    @staticmethod
    def create(networks: list[str], symbol0: str, symbol1: str, fee: Literal[100, 500, 3000, 10_000]) -> 'UniswapV3PoolAllEvents':
        return UniswapV3PoolAllEvents(
            client_name='uniswap',
            name='uniswap_v3_pool_liquidity_events',
            networks=networks,
            extra_args={
                'symbol0': symbol0,
                'symbol1': symbol1,
                'fee': fee
            }
        )

@dataclass
class UniswapV3NFTPMEvents(Substream):
    @staticmethod
    def create(networks: list[str]) -> 'UniswapV3NFTPMEvents':
        return UniswapV3NFTPMEvents(
            client_name='uniswap',
            name='uniswap_v3_nftpm_all_events',
            networks=networks,
            extra_args={}
        )

@dataclass
class ERC20AllEvents(Substream):
    @staticmethod
    def create(networks: list[str], tokens: list[str], exclude_zero_transfers: bool = True) -> 'ERC20AllEvents':
        return ERC20AllEvents(
            client_name='erc20',
            name='erc20_all_events',
            networks=networks,
            extra_args={
                'tokens': tokens,
                'exclude_zero_transfers': exclude_zero_transfers,
            }
        )

@dataclass
class ERC20WalletTransferEvents(Substream):
    @staticmethod
    def create(networks: list[str], tokens: list[str], wallets: list[str], exclude_zero_transfers: bool = True) -> 'ERC20WalletTransferEvents':
        return ERC20WalletTransferEvents(
            client_name='erc20',
            name='erc20_wallet_transfer_events',
            networks=networks,
            extra_args={
                'tokens': tokens,
                'wallets': wallets,
                'exclude_zero_transfers': exclude_zero_transfers,
            }
        )

@dataclass
class BinanceStakingAllEvents(Substream):
    @staticmethod
    def create(networks: list[str]) -> 'BinanceStakingAllEvents':
        return BinanceStakingAllEvents(
            client_name='binance_staking',
            name='binance_staking_all_events',
            networks=networks,
            extra_args={}
        )

@dataclass
class CoinbaseStakingAllEvents(Substream):
    @staticmethod
    def create(networks: list[str], token: Literal['CBETH', 'CBBTC']) -> 'CoinbaseStakingAllEvents':
        return CoinbaseStakingAllEvents(
            client_name='coinbase_staking',
            name='coinbase_staking_all_events',
            networks=networks,
            extra_args={
                'token': token
            }
        )

@dataclass
class LidoAllEvents(Substream):
    @staticmethod
    def create(networks: list[str]) -> 'LidoAllEvents':
        return LidoAllEvents(
            client_name='lido',
            name='lido_all_events',
            networks=networks,
            extra_args={}
        )

@dataclass
class StaderEthXAllEvents(Substream):
    @staticmethod
    def create(networks: list[str]) -> 'StaderEthXAllEvents':
        return StaderEthXAllEvents(
            client_name='stader',
            name='stader_ethx_all_events',
            networks=networks,
            extra_args={}
        )

@dataclass
class ThresholdTBTCAllEvents(Substream):
    @staticmethod
    def create(networks: list[str]) -> 'ThresholdTBTCAllEvents':
        return ThresholdTBTCAllEvents(
            client_name='threshold',
            name='threshold_tbtc_all_events',
            networks=networks,
            extra_args={}
        )
