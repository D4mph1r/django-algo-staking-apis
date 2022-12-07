from beaker import sandbox
from algosdk.abi import ABIType
from pyteal import abi
from nftDjango.settings import ALGOD_ADDRESS, ALGOD_TOKEN

LOCKTIME = {
    "7890000": 25000000,
    "15780000": 50000000,
    "23650000": 75000000,
    "31540000": 100000000,
}


class stakings:
    def __init__(self, appId, owner, id, timeToUnlock, stakingTime, tokensStaked, tokensStakedWithBonus, lockTime, txId):
        self.appId = appId
        self.owner = owner
        self.id = id
        self.timeToUnlock = timeToUnlock
        self.stakingTime = stakingTime
        self.tokensStaked = tokensStaked
        self.tokensStakedWithBonus = tokensStakedWithBonus
        self.lockTime = lockTime
        self.txId = txId

    def to_dict(self):
        return {"appId": self.appId, "owner": self.owner, "id": self.id, "timeToUnlock": self.timeToUnlock, "stakingTime": self.stakingTime, "tokensStaked": self.tokensStaked, "tokensStakedWithBonus": self.tokensStakedWithBonus, "lockTime": self.lockTime, "txId": self.txId}


class StakingInfo(abi.NamedTuple):
    owner: abi.Field[abi.Address]
    id: abi.Field[abi.Uint64]
    timeToUnlock: abi.Field[abi.Uint64]
    stakingTime: abi.Field[abi.Uint64]
    tokensStaked: abi.Field[abi.Uint64]
    tokensStakedWithBonus: abi.Field[abi.Uint64]
    lockTime: abi.Field[abi.Uint64]


staking_codec = ABIType.from_string(str(StakingInfo().type_spec()))


def getAlgodClient():
    algod_client = sandbox.get_algod_client(ALGOD_ADDRESS, ALGOD_TOKEN)
    return algod_client
