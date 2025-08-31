from ..client.game_client import GameClient
from loguru import logger





class Tools(GameClient):
    
    
    async def get_production_queue(
        self, 
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("spl", {"LID": 1})
            if sync:
                response = await self.wait_for_response("spl")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            
            
            
    async def produce_tools(
        self,
        castle_id: int,
        wod_id: int,
        amount: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "bup",
                {
                    "LID": 1,
                    "WID": wod_id,
                    "AMT": amount,
                    "PO": -1,
                    "PWR": 0,
                    "SK": 73,
                    "SID": 0,
                    "AID": castle_id
                }
            )
            if sync:
                response = await self.wait_for_response("bup")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            
            
    async def cancel_production(
        self, 
        slot_type: str, 
        slot: int, 
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("mcu", {"LID": 1, "S": slot, "ST": slot_type})
            if sync:
                response = await self.wait_for_response("mcu")
                return response
            return True
        
        except Exception as e:
            logger.error(e)