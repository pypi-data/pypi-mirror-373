try:
    from dt.excel import Addin  # type: ignore
except ImportError:

    class DummyAddin:
        def __init__(self, name: str, description: str) -> None:
            self.name = name
            self.description = description

        def expose(self, **kwargs):
            def decorator(func):
                return func

            return decorator

        def run(self):
            pass

    Addin = DummyAddin
