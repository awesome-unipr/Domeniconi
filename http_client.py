import aiohttp
import asyncio

async def main():

    async with aiohttp.ClientSession() as session:
        
        async with session.get('http://localhost:8080/dms') as response:

            print("Status:", response.status)
            print("Content-type:", response.headers['content-type'])

            html = await response.text()
            print("Body:", html[:100])

asyncio.run(main())

