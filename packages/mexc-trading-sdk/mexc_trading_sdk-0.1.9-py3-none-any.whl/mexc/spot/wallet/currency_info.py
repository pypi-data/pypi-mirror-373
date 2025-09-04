from typing_extensions import TypedDict, NotRequired
from mexc.core import timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ApiError

class Network(TypedDict):
  depositEnable: bool
  withdrawEnable: bool
  withdrawFee: str
  withdrawMax: str
  withdrawMin: str
  sameAddress: bool
  contract: NotRequired[str | None]
  withdrawTips: NotRequired[str | None]
  depositTips: NotRequired[str | None]
  netWork: str

class Currency(TypedDict):
  coin: str
  name: str
  networkList: list[Network]

Response: type[list[Currency] | ApiError] = list[Currency] | ApiError # type: ignore
validate_response = validator(Response)

class CurrencyInfo(AuthSpotMixin):
  async def currency_info(
    self, *, timestamp: int | None = None,
    validate: bool | None = None,
  ) -> ApiError | list[Currency]:
    """Query currency information, of all supported currencies.
    
    - `timestamp`: The timestamp for the request, in milliseconds (default: now).
    - `validate`: Whether to validate the response against the expected schema (default: True).

    > [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-the-currency-information)
    """
    params = {'timestamp': timestamp or ts.now()}
    r = await self.signed_request('GET', '/api/v3/capital/config/getall', params=params)
    return validate_response(r.text) if self.validate(validate) else r.json()