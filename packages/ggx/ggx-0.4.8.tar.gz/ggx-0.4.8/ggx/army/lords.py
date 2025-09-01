from ..client.game_client import GameClient
from loguru import logger
import random





class Lords(GameClient):
    
    
    async def get_lords(self, sync: bool = True) -> dict | bool:
        
        
        try:
            
            await self.send_json_message("gli", {})
            
            if sync:
                response = await self.wait_for_response("gli")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False
        


    async def list_lords_id(
        self,
        lord_list: list,
    ) -> list:
        
        if not isinstance(lord_list, list):
            lord_list = []
        
        lords_data = await self.get_lords()
        all_lords = lords_data.get("C", [])
        
        for lord_obj in all_lords:
            lord_id = lord_obj.get("ID")
            eq_list = lord_obj.get("EQ")
            if len(eq_list) >= 5:
                lord_list.append(lord_id)


        
        
    async def select_lord(
        self,
        user_lords: list
    ) -> int:
        
        
        if not isinstance(user_lords, list):
            logger.error("Add lords list!")
            return 
        

        
        details_response = await self.send_rpc("gcl", {})
        account_id = details_response["PID"]
        moves_response = await self.send_rpc("gam", {})
        movements = [movement for movement in moves_response["M"] if movement["M"]["OID"] == account_id and movement.get("UM") is not None]
        used_lords = [movement["UM"]["L"].get("ID") for movement in movements]
        available_lords = list(set(user_lords) ^ set(used_lords))
        if available_lords:
            choosed_lord = random.choice(available_lords)
            return choosed_lord

        else:
            logger.warning("All lords are used!")
            return