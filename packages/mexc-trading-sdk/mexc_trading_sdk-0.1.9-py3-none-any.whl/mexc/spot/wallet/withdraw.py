from typing_extensions import TypedDict
from mexc.core import timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ApiError

class WithdrawId(TypedDict):
  id: str

Response: type[WithdrawId | ApiError] = WithdrawId | ApiError # type: ignore
validate_response = validator(Response)

class Withdraw(AuthSpotMixin):
  async def withdraw(
    self, coin: str, *,
    amount: str, address: str,
    network: str | None = None,
    contract_address: str | None = None,
    memo: str | None = None,
    remark: str | None = None,
    timestamp: int | None = None, validate: bool | None = None,
  ) -> ApiError | WithdrawId:
    """Withdraw assets from your account.
    
    - `coin`: The coin to withdraw, e.g. `USDT`.
    - `amount`: The amount to withdraw.
    - `address`: The address to withdraw to.
    - `network`: The network to withdraw to, e.g. `TRX`. You can retrieve the network from the `deposit_addresses` endpoint, using the `netWork` field.
    - `contract_address`: The contract address to withdraw to. You can use it to make sure it's the token you expect.
    - `memo`: The memo to withdraw to. Only needed for some networks.
    - `remark`: Text to add to the withdrawal record.
    - `timestamp`: The timestamp for the request, in milliseconds (default: now).
    - `validate`: Whether to validate the response against the expected schema (default: True).

    > [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#withdraw-new)
    """
    params = {
      'coin': coin, 'timestamp': timestamp or ts.now(),
      'amount': amount, 'address': address,
    }
    if network is not None:
      params['netWork'] = network
    if contract_address is not None:
      params['contractAddress'] = contract_address
    if memo is not None:
      params['memo'] = memo
    if remark is not None:
      params['remark'] = remark
    r = await self.signed_request('POST', '/api/v3/capital/withdraw', params=params)
    return validate_response(r.text) if self.validate(validate) else r.json()
