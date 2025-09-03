from grpcAPI.protobuf import BytesValue, StringValue


def func1():
    pass


def func2(name: str) -> str:
    pass


def func3(name: StringValue, payload: BytesValue) -> StringValue:
    pass
