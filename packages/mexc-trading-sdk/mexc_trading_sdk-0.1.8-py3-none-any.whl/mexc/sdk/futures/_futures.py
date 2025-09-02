from dataclasses import dataclass, field
from .user_data import UserData
from .user_streams import UserStreams

@dataclass
class Futures(UserData):
  user_streams: UserStreams = field(init=False)
  
  def __post_init__(self):
    self.user_streams = UserStreams(client=self.client)