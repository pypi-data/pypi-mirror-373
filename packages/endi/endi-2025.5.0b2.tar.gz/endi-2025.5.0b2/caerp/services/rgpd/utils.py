from caerp.models.config import Config


def get_retention_days(request, data_type: str, default: int) -> int:
    return Config.get_value(
        f"rgpd_{data_type}s_retention_days", default=default, type_=int
    )
