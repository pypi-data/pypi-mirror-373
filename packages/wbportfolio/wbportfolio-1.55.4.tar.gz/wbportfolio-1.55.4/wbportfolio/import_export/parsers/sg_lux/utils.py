import re
from typing import Any, Dict

from wbportfolio.models import Product, Register, Trade


def get_portfolio_id(x):
    product = Product.objects.get(id=x)
    portfolio = product.primary_portfolio
    return portfolio.id


def parse_transaction_reference(trans_ref: str) -> tuple[str, str, bool]:
    pattern = r"([0-9]{7})([0-9]{8})([CD]{1})"
    transaction_id, outlet_id, credit_debit = re.findall(pattern, trans_ref)[0]
    return transaction_id, outlet_id, credit_debit == "C"


def assemble_transaction_reference(data: Dict[str, Any]) -> str:
    transaction_ref = data["external_id_alternative"]
    register_reference = data["register__register_reference"]
    if data.get("TRANSFER_REGISTER", None):
        register_reference = data["TRANSFER_REGISTER"]

    outlet = Register.objects.get(register_reference=register_reference).outlet_reference
    credit_debit = "C" if data["shares"] > 0 else "D"

    return f"{int(transaction_ref):07}{int(outlet):08}{credit_debit}"


def create_transaction_reference(customer_trade: "Trade") -> str:
    transaction_id = customer_trade.external_id_alternative
    outlet_id = customer_trade.register.clearing_reference
    credit_debit = "C" if customer_trade.initial_shares > 0 else "D"

    return f"{transaction_id:07}{outlet_id:08}{credit_debit}"
