from ..client.game_client import GameClient
from loguru import logger






class Alliance(GameClient):
    
    
    
    async def get_chat(self, sync: bool = True) -> dict | bool:
        
        try:
            await self.send_json_message("acl", {})
            if sync:
                response = await self.wait_for_response("acl")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
    
    
    async def write_on_chat(
        self,
        message: str,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "acm",
                {
                    "M": message
                }
            )
            if sync:
                response = await self.wait_for_response("acm")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
    
    
    
       
        
    async def help_alliance_member(
        self, 
        kingdom: int, 
        help_id: int, 
        sync: bool = True
    ) -> dict | bool:

        try:
            await self.send_json_message("ahc", {"LID": help_id, "KID": kingdom})
            if sync:
                response = await self.wait_for_response("ahc")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
    
    
    
       
    async def help_alliance_all(
        self, 
        kingdom: int, 
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("aha", {"KID": kingdom})
            if sync:
                response = await self.wait_for_response("aha")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False  
        
        
    async def invite_player(
        self,
        user_id: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "aip",
                {
                    "SV": user_id
                }
            )
            if sync:
                response = await self.wait_for_response("aip")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False 
        
        
        
    async def rank_player(
        self,
        account_id: int,
        rank: int,   ## 0-8 leader to member
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "arm",
                {
                    "PID": account_id,
                    "R": rank
                }  
            )
            if sync:
                response = await self.wait_for_response("arm")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False 
        
      
      
        
        
    async def mass_message(
        self,
        text: str,
        title: str = None,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "anl",
                {
                    "SJ": title,
                    "TXT": text
                }
            )
            if sync:
                response = await self.wait_for_response("anl")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False 
        
        
        
    async def leave_alliance(self, sync: bool = True) -> dict | bool:
        
        try:
            await self.send_json_message("aqi", {})
            if sync:
                response = await self.wait_for_response("aqi")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False 
        
        
        
    async def create_alliance(
        self,
        alliance_name: str,
        allinace_state: int,
        description: str,
        lang: str,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "afo",
                {
                    "PO":-1,
                    "PWR":0,
                    "IA": allinace_state,
                    "N": alliance_name,
                    "D": description,
                    "ALL": lang
                }
            )
            if sync:
                response = await self.wait_for_response("afo")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False 