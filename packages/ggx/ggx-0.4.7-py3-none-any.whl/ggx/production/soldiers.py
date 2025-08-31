from ..client.game_client import GameClient
from loguru import logger






class Soldiers(GameClient):
    
    
    
    async def get_recruitment_queue(self, sync: bool = True) -> dict | bool:
        
        try:
            
            await self.send_json_message("spl", {"LID":0})
            if sync:
                response = await self.wait_for_response("spl")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
     
        
    async def recruit_soldiers(
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
                    "LID": 0,
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
            return False
        
        
        
        
    async def cancel_recruitment(
        self,
        slot_type: str,
        slot: int,
        sync: bool = True
        ) -> dict | bool:
        
        try:
            await self.send_json_message("mcu", {"LID":0, "S": slot, "ST": slot_type})
            if sync:
                response = await self.wait_for_response("mcu")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
        
    async def recruitment_alliance_help(self, sync: bool = True) -> dict | bool:
        
        try:
            await self.send_json_message("ahr", {"ID":0, "T":6})
            if sync:
                response = await self.wait_for_response("ahr")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
        
    async def get_units_inventory(
        self,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("gui", {})
            if sync:
                response = await self.wait_for_response("gui")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False        
        
        
    
    async def delete_units(
        self,
        wod_id: int,
        amount: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "dup",
                {
                    "WID": wod_id,
                    "A": amount,
                    "S": 0
                }
            )
            if sync:
                response = await self.wait_for_response("dup")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False   
        
        
        
    async def wait_receive_units(
        self,
        kingdom: int,
        castle_id: int,
        wod_id: int,
        amount: int,
        timeout: int = 5,
    ) -> dict | bool:

        try:
            response = await self.wait_for_response(
                "rue",
                {"AID": castle_id, "SID": kingdom, "WID": wod_id, "RUA": amount},
                timeout=timeout,
            )
            return response
        except Exception as e:
            logger.error(e)
            return False
 