from dataclasses import dataclass

from .get_deposits import GetDeposits
from .get_withdrawals import GetWithdrawals
from .withdraw import Withdraw
from .get_current_deposit_address import GetCurrentDepositAddress

@dataclass(frozen=True)
class Wallet(
  GetDeposits,
  GetWithdrawals,
  Withdraw,
  GetCurrentDepositAddress,
):
  ...