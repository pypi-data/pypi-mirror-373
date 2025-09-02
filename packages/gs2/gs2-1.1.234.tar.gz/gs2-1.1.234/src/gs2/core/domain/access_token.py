class AccessToken:

    user_id: str
    token: str
    expire: int

    def __init__(
            self,
            user_id: str,
            token: str,
            expire: int,
    ):
        self.user_id = user_id
        self.token = token
        self.expire = expire
