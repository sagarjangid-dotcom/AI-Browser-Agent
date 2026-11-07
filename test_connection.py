import asyncio
from playwright._impl._transport import PipeTransport
from playwright._impl._driver import compute_driver_executable

async def main():
    print("Checking driver connection...", flush=True)
    transport = PipeTransport()
    print("Transport object created!", flush=True)

asyncio.run(main())
