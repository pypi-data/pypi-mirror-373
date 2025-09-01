from ..client.game_client import GameClient
from loguru import logger





class Refinery(GameClient):
    
    
    
    async def refinery_get_queue(
        self,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("crin", {})
            if sync:
                response = await self.wait_for_response("crin")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
    
    
    
    async def produce_materials(
        self,
        kingdom: int,
        castle_id: int,
        building_id: int,
        item_id: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "crst",
                {
                    "KID": kingdom,
                    "AID": castle_id,
                    "OID": building_id,
                    "PWR": 0,
                    "CRID": item_id
                    
                }
            )
            if sync:
                response = await self.wait_for_response("crst")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
            
            
            
    async def cancel_materials_production(
        self,
        kingdom: int,
        castle_id: int,
        building_id: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "crca",
                {
                    "KID": kingdom,
                    "AID": castle_id,
                    "OID": building_id,
                    "S": 0,
                    "ST": "queue"
                    
                }
            )
            if sync:
                response = await self.wait_for_response("crca")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False