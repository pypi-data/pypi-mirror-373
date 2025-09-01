from typing import Dict, Any


class BaseSymbol:
    def __init__(self, base_symbol_info: Dict[str, Any]):
        self.id: int = base_symbol_info["id"]
        self.exchange: str = base_symbol_info["exchange"]
        self.key: str = base_symbol_info["key"]
        self.value: str = base_symbol_info["value"]
        self.type: str = base_symbol_info["type"]
        self.lot_size: int = base_symbol_info["lot_size"]
        self.strike_size: int = base_symbol_info["strike_size"]
