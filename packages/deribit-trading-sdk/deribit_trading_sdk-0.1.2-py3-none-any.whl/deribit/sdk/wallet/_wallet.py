from dataclasses import dataclass
from .withdrawal_history import WithdrawalHistory
from .deposit_history import DepositHistory

@dataclass
class Wallet(WithdrawalHistory, DepositHistory):
  ...