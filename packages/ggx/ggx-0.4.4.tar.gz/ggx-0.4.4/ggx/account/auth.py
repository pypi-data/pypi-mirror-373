from ..client.game_client import GameClient
from loguru import logger







class Auth(GameClient):



    async def check_username_availability(
        self,
        name: str,
        sync: bool = True
    ) -> dict | bool:

        try:
            await self.send_json_message("vpn", {"PN": name})
            if sync:
                response = await self.wait_for_response("vpn")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False


    async def check_user_exists(
        self,
        name: str,
        sync: bool = True
    ) -> dict | bool:

        try:
            await self.send_json_message("vln", {"NOM": name})
            if sync:
                response = await self.wait_for_response("vln")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False
        

    async def register(
        self, 
        username: str, 
        email: str, 
        password: str,
        token: str, 
        sync: bool = True
    ) -> dict | bool:

        try:
            await self.send_json_message(
                "lre",
                {
                    "DID": 0,
                    "CONM": 175,
                    "RTM": 24,
                    "campainPId": -1,
                    "campainCr": -1,
                    "campainLP": -1,
                    "adID": -1,
                    "timeZone": 14,
                    "username": username,
                    "email": email,
                    "password": password,
                    "accountId": "1674256959939529708",
                    "ggsLanguageCode": "en",
                    "referrer": "https://empire.goodgamestudios.com",
                    "distributorId": 0,
                    "connectionTime": 175,
                    "roundTripTime": 24,
                    "campaignVars": ";https://empire.goodgamestudios.com;;;;;;-1;-1;;1674256959939529708;380635;;;;;",
                    "campaignVars_adid": "-1",
                    "campaignVars_lp": "-1",
                    "campaignVars_creative": "-1",
                    "campaignVars_partnerId": "-1",
                    "campaignVars_websiteId": "380635",
                    "timezone": 14,
                    "PN": username,
                    "PW": password,
                    "REF": "https://empire.goodgamestudios.com",
                    "LANG": "en",
                    "AID": "1674256959939529708",
                    "GCI": "",
                    "SID": 9,
                    "PLFID": 1,
                    "NID": 1,
                    "IC": "",
                    "RCT": token
                },
            )
            if sync:
                response = await self.wait_for_response("lre")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False
        

    async def login_with_token(
        self, 
        name: str, 
        password: str, 
        token: str, 
        sync: bool = True
    ) -> dict | bool:

        try:
            await self.send_json_message(
                "lli",
                {
                    "CONM": 175,
                    "RTM": 24,
                    "ID": 0,
                    "PL": 1,
                    "NOM": name,
                    "PW": password,
                    "LT": None,
                    "LANG": "fr",
                    "DID": "0",
                    "AID": "1674256959939529708",
                    "KID": "",
                    "REF": "https://empire.goodgamestudios.com",
                    "GCI": "",
                    "SID": 9,
                    "PLFID": 1,
                    "RCT": token,
                },
            )
            if sync:
                response = await self.wait_for_response("lli")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False