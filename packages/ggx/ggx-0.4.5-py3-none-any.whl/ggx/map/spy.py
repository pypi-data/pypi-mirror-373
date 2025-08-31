from ..client.game_client import GameClient
from loguru import logger







class Spy(GameClient):
    
    
    
    
    async def send_spy(
        self,
        kingdom: int,
        source_id: int,
        tx: int,
        ty: int,
        spies_nr: int,
        precision: int,
        horses_type: int = -1,
        slowdown: int = 0,
        feathers: int = 0,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "csm",
                {
                    "SID": source_id,
                    "TX": tx,
                    "TY": ty,
                    "SC": spies_nr,
                    "ST": 0,
                    "SE": precision,
                    "HBW": horses_type,
                    "KID": kingdom,
                    "PTT": feathers,
                    "SD": slowdown
                }
            )
            if sync:
                response = await self.wait_for_response("csm")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
        
    async def send_sabotage(
        self,
        kingdom: int,
        source_id: int,
        tx: int,
        ty: int,
        spies_nr: int,
        burn_pecent: int = 50,
        horses_type: int = 0,
        feathers: int = 0,
        slowdown: int = 0,
        sync: bool = True   
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "csm",
                {
                    "SID": source_id,
                    "TX": tx,
                    "TY": ty,
                    "SC": spies_nr,
                    "ST": 2,
                    "SE": burn_pecent,
                    "HBW": horses_type,
                    "KID": kingdom,
                    "PTT": feathers,
                    "SD": slowdown
                }
            )
            if sync:
                response = await self.wait_for_response("csm")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False