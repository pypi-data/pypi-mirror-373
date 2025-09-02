import asyncio
import datetime
import json

from pyasic import get_miner, settings


async def main():
    # ip = "10.9.191.95" # Online
    # ip = "10.9.199.178" # Idle
    # ip = "10.73.116.227" # New
    ip = "10.91.107.169" # L7
    try:

        miner = await get_miner(ip=ip)

        print(f"Miner: {miner}")

        miningMode = await miner.is_mining()
        sleepMode = await miner.is_sleep()
        errors = await miner.get_errors()
        minerData = await miner.get_data()

        print(f"Is mining: {miningMode}")
        print(f"Sleep mode: {sleepMode}")
        print(f"Errors: {errors}")
        print(f"MinerData: {minerData}")

        ### STOP

        # stop = await miner.stop_mining()
        # print(f"Stop mining: {stop}")

        ### RESUME

        # resume = await miner.resume_mining()
        # print(f"Resume mining: {resume}")

        ### REBOOT

        # reboot = await miner.reboot()
        # print(f"Reboot mining: {reboot}")

    except Exception as e:
        print(f"Error:: {e}")


if __name__ == "__main__":
    asyncio.run(main())
