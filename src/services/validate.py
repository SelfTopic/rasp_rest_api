from ..config import config 

class ValidateRequestService:

    def __init__(self) -> None: 
        pass 

    def is_valid_token(self, token: str) -> bool:
        return token == config.secret_key
    
    def is_valid_day(self, day: str) -> bool:
        return day in ["today", "tommorow"]
