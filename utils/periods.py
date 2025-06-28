from datetime import datetime, timedelta

PERIODS = {
    "Ultima semana": 7,
    "Ultimo mes": 30,
    "Ultimo año": 365,
    "Todo el tiempo": None
}

def get_period_range(period_name):
    today = datetime.now()
    days = PERIODS.get(period_name, None)

    if days is None:
        return None, None

    start_date = today - timedelta(days=days)
    end_date = today

    return start_date.strftime("%d-%m-%Y"), end_date.strftime("%d-%m-%Y")