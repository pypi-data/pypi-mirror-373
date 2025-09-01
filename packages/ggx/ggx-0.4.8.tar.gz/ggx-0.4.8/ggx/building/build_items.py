from ..client.game_client import GameClient
from loguru import logger







class BuildItems(GameClient):
    
    
    
    
    
    async def equip_build_item(
        self,
        kingdom_id: int,
        castle_id: int,
        building_id: int,
        slot_id: int,
        item_id: int,
        sync: bool = True
    ) -> dict | bool:
        
        
        try:
            await self.send_json_message(
                "rpc",
                {
                    "OID": building_id,
                    "CID": item_id,
                    "SID": slot_id,
                    "M": 0,
                    "KID": kingdom_id,
                    "AID": castle_id
                }
            )
            if sync:
                response = await self.wait_for_response("rpc")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
    
    
    
    
    
    
    
    
    