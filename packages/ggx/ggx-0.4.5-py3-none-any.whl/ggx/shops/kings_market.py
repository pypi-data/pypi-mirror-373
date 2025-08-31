from ..client.game_client import GameClient
from loguru import logger





class KingsMarket(GameClient):
    
    
    
    async def start_protection(
        self,
        duration: int,      ### 0:7days, 1: 14 days, 2: 21days, 3: 60 days
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "mps",
                {
                    "CD": duration
                }
            )
            if sync:
                response = await self.wait_for_response("mps")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
    
    
    async def buy_production_slot(
        self,
        queue_type: int, ## 0 for baracks, 1 for workshop
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "ups",
                {
                    "LID": queue_type
                }
            )
            if sync:
                response = await self.wait_for_response("ups")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False



       
    async def buy_open_gates(
        self,
        kingdom: int,
        castle_id: int,
        duration: int,   ## 0 for 6h, 1 for 12h
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "mos",
                {
                    "CID": castle_id,
                    "KID": kingdom,
                    "CD": duration
                }
            ) 
            if sync:
                response = await self.wait_for_response("mos")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
        
    async def buy_feast(
        self,
        kingdom: int,
        castle_id: int,
        feast_type: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "bfs",
                {
                    "CID": castle_id,
                    "KID": kingdom,
                    "T": feast_type,
                    "PO": -1,
                    "PWR": 0
                }
            )
            if sync:
                response = await self.wait_for_response("bfs")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False