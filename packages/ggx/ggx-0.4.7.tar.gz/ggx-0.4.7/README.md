# GGX
The most advanced API library for interacting with GoodGame Empire.


## Description

An API client library for GoodGame Empire (GGE), enabling automated
connection, gameplay actions, and system scripting. Built for Python 3.12+,
ggx is currently in alpha stage—ideal for early adopters exploring automation
within GoodGame Empire.


## Install

```bash
pip install ggx
```

## Example

```
from ggx import GGXS
import asyncio


class Example(GGXS):

    def __init__(self, url, server_header, username, password):
        super().__init__(url, server_header, username, password)
        ## var example
        self.example = None


    ## add your jobs here!
    async def run_jobs(self):
        ## get castles detailes
        await self.get_detailed_castles()

## example contain Romanian server!
async def main():
    app = Example("wss://ep-live-ro1-game.goodgamestudios.com/", "EmpireEx_15", "My username", "my password")
    await app.connect()
     
asyncio.run(main())
```


## Warning

 - This project is still under development and can cause errors or bugs!
 - Just for education purpose only!
 - I'm not responsible for any action which will be taken by GGE Studios against your account!
 - For any contribution, contact me!
