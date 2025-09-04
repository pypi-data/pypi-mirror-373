# type: ignore

from .PushDataV3ApiWrapper_pb2 import PushDataV3ApiWrapper

def parse_proto(data: str | bytes):
  result = PushDataV3ApiWrapper()
  result.ParseFromString(data) # type: ignore
  return result