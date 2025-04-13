from idotmatrix import ConnectionManager
import asyncio

async def get_address():
    conn = ConnectionManager()
    return await conn.scan()

def main():
    res = asyncio.run(get_address())
    print(f"The address of your bot is {res[0]}")

if __name__ == "__main__":
    main()