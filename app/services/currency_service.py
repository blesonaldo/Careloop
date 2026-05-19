EXCHANGE_RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "NGN": 1600.0
}

def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    from_rate = EXCHANGE_RATES.get(from_currency.upper())
    to_rate = EXCHANGE_RATES.get(to_currency.upper())

    if not from_rate or not to_rate:
        return amount

    usd_amount = amount / from_rate
    converted = usd_amount * to_rate

    return round(converted, 2)
