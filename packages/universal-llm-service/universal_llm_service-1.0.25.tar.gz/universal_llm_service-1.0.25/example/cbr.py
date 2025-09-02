import asyncio

from llm.cbr.cbr import CBRRate


async def main() -> None:
    cbr = CBRRate()
    usd_rate = await cbr.get_usd_rate()
    print(usd_rate)


if __name__ == '__main__':
    asyncio.run(main())
