from pydantic import BaseModel


class Symbol(BaseModel):
    # ccy1/ccy2
    ccy1: str
    ccy2: str

    def to_str(Symbol) -> str:
        return f"{Symbol.ccy1}/{Symbol.ccy2}"
