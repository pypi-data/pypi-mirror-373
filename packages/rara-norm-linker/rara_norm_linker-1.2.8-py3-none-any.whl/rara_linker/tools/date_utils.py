from datetime import datetime

def format_date(original_date: str) -> str:
    try:
        date_obj = datetime.strptime(original_date, "%Y-%m-%d")
        new_date = date_obj.strftime("%d.%m.%Y")

    except:
        new_date = original_date
    return new_date
