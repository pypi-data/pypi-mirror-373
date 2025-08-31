from ..client.game_client import GameClient
from loguru import logger





class Support(GameClient):
    
    
    
    
    
    
    async def get_support_info(
        self,
        sx: int,
        sy: int,
        tx: int,
        ty: int,
        sync: bool = True 
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "sdi",
                {
                    "TX": tx,
                    "TY": ty,
                    "SX": sx,
                    "SY": sy
                }
            )
            if sync:
                response = await self.wait_for_response("sdi")
                return response
            return True

        except Exception as e:
            logger.error(e)
            return False
        
                
    
    
    
    
    
    async def send_support(
        self,
        units: list,
        sender_id: int,
        tx: int,
        ty: int,
        lord_id: int,
        camp_time: int = 12,
        horses_type: int = -1,
        feathers: int = 0,
        slowdown: int = 0,
        sync: bool = True 
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "cds",
                {
                    "SID": sender_id,
                    "TX": tx,
                    "TY": ty,
                    "LID": lord_id,
                    "WT": camp_time,
                    "HBW": horses_type,
                    "BPC": 0,
                    "PTT": feathers,
                    "SD": slowdown,
                    "A": units
                }
            )
            if sync:
                response = await self.wait_for_response("cds")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False