import asyncio
import aiohttp
from datetime import datetime, timedelta
import sys

privat_url = "https://api.privatbank.ua/p24api/exchange_rates?json&date="
currencies = ["USD", "EUR"]
max_days = 10


def get_last_days(days):
    today = datetime.now()
    return [
        (today - timedelta(days=i)).strftime('%d.%m.%Y')
        for i in range(days)
    ]


async def fetch_exchange_rate(session, date):
    url = privat_url + date
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                data = await response.json()
                result = {}
                for rate in data.get("exchangeRate", []):
                    if rate.get("currency") in currencies:
                        result[rate["currency"]] = {
                            "sale": rate.get("saleRate"),
                            "purchase": rate.get("purchaseRate")
                        }
                return {date: result}
            else:
                return {date: f"HTTP Error: {response.status}"}
    except aiohttp.ClientError as e:
        return {date: f"Error: {e}"}
    except asyncio.TimeoutError:
        return {date: "Час очікування вичерпано"}


async def get_rates_for_days(days):
    dates = get_last_days(days)
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_exchange_rate(session, date) for date in dates]
        results = await asyncio.gather(*tasks)
    return results


def main():
    if len(sys.argv) < 2:
        days = 1
    else:
        try:
            days = int(sys.argv[1])
            if not (1 <= days <= max_days):
                print(f"Кількість днів має бути від 1 до {max_days}")
                sys.exit(1)
        except ValueError:
            print("Аргумент має бути числом (наприклад: 3)")
            sys.exit(1)

    rates = asyncio.run(get_rates_for_days(days))
    print(rates)


if __name__ == "__main__":
    main()
