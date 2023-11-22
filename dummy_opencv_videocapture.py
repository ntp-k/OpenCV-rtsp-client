class DummyVideoCapture:
    def __init__(self) -> None:
        pass

    def read(self) -> tuple:
        return None, None

    def grab(self) -> bool:
        return True

    def retrieve(self) -> tuple:
        return None, None

    def release(self) -> None:
        pass

# EOF
