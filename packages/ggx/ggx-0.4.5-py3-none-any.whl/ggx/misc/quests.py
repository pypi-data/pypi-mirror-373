from ..client.game_client import GameClient
from loguru import logger




class Quests(GameClient):
    
    
    
    
    
    
    async def get_quests(
        self,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("dcl", {"CD": 1})
            if sync:
                response = await self.wait_for_response("dcl")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
        
    async def complete_message_quest(
        self,
        quest_id: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("qsc", {"QID": quest_id})
            if sync:
                response = await self.wait_for_response("qsc")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
     
     
        
        
    async def complete_donation_quest(
        self,
        quest_id: int,
        food: int = 0,
        wood: int = 0,
        stone: int = 0,
        gold: int = 0,
        oil: int = 0,
        coal: int = 0,
        iron: int = 0,
        glass: int = 0,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "qdr",
                {
                    "QID": quest_id,
                    "F": food,
                    "W": wood,
                    "S": stone,
                    "C1": gold,
                    "O": oil,
                    "C": coal,
                    "I": iron,
                    "G": glass,
                    "PWR": 0,
                    "PO": -1
                }
            )
            if sync:
                response = await self.wait_for_response("qdr")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
        
    async def tracking_recommended_quests(self) -> bool:
        
        try:
            await self.send_json_message("ctr", {"TQR": 0})
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
        
    async def complete_quest_condition(
        self,
        quest_id: int,
        condition: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "fcq",
                {
                    "QTID": quest_id,
                    "QC": condition
                }
            )
            if sync:
                response = await self.wait_for_response("fcq")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
 