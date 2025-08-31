from ..client.game_client import GameClient
from loguru import logger





class Social(GameClient):
    
    
    
    
    async def send_player_sms(
        self,
        player_name: str,
        sms_title: str,
        sms_text: str,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "sms",
                {
                    "RN": player_name,
                    "MH": sms_title,
                    "TXT": sms_text
                }
            )
            if sync:
                response = await self.wait_for_response("sms")
                return response
            return True

        except Exception as e:
            logger.error(e)
            
    
    
    async def read_messages(self, message_id: int, sync: bool = True):
        
        try:
            
            await self.send_json_message(
                "rms", {
                    "MID": message_id
                }
            )
            
            if sync:
                response = await self.wait_for_response("rms")
                return response
            return True
            
        except Exception as e:
            logger.error(e) 
            return False
    
    
    
    
    
    
    
            
    async def delete_message(self, message_id, sync = True):
        
        try:
            
            await self.send_json_message(
                "dms", {
                    "MID": message_id
                }
            )
            
            if sync:
                response = await self.wait_for_response("dms")
                return response
            logger.info(f'Message {message_id} removed!')
            return True
            
        except Exception as e:
            logger.error(e) 
            return False
        
    
    
    
    
    
    async def read_report(self, message_id: int, sync: bool = True):
        
        try:
            
            await self.send_json_message(
                "bsd", {
                    "MID": message_id
                }
            )
            
            if sync:
                response = await self.wait_for_response("bsd")
                return response
            
            return True
            
        except Exception as e:
            logger.error(e) 
            return False
        
        
    
    
    
    
    
    
    
        
        
    async def no_battle_handle(self, data):
        
        msg_data = data.get("MSG", [])
        for msg_detail in msg_data:
            if msg_detail[1] == 67:
                await self.delete_message(msg_detail[0])
    
            
    
    
    
    
    
    async def spy_report_handle(self, data):
        
        
        
        
        msg_data = data.get("MSG", [])
        for msg_detail in msg_data:
            if msg_detail[1] == 3:
                spy_check = str(msg_detail[2]).split('#', 1)[0]
                if spy_check.startswith("1+0"):
                    report = await self.read_report(msg_detail[0])
                    return report
                
                    

