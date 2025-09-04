from typing import TypedDict, Dict

class Leverage(TypedDict):
    rawUsd: str
    type: str
    value: int

class CumFunding(TypedDict):
    allTime: str
    sinceChange: str
    sinceOpen: str

class Position(TypedDict):
    coin: str
    cumFunding: CumFunding
    entryPx: str
    leverage: Leverage
    liquidationPx: str
    marginUsed: str
    maxLeverage: int
    positionValue: str
    returnOnEquity: str
    szi: str
    unrealizedPnl: str

class AssetPosition(TypedDict):
    position: Position
    type: str

class CrossMarginSummary(TypedDict):
    accountValue: str
    totalMarginUsed: str
    totalNtlPos: str
    totalRawUsd: str

class MarginSummary(TypedDict):
    accountValue: str
    totalMarginUsed: str
    totalNtlPos: str
    totalRawUsd: str

class AccountBalance(TypedDict):
    assetPositions: list[AssetPosition]
    crossMaintenanceMarginUsed: str
    crossMarginSummary: CrossMarginSummary
    marginSummary: MarginSummary
    time: int
    withdrawable: str