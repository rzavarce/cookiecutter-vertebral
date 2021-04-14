""" Authentification Model """

import string
import random

from core.models.mongodb import MongoModel


def generate_token(length):
    """
    choose from all char of letter in uppercase or lowercase and
    punctuation signals

    -----------------
    Args:
        length (int): Token length
    Returns:
        token (str): Token generated
    """
    sources = string.ascii_letters + string.digits
    # sources = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(sources) for i in range(length))


class Auth(MongoModel):
    """User Auth model."""

    def __init__(self, clientdb):
        super().__init__()
        self.clientdb = clientdb
        self.collaction = self.clientdb[self.__class__.__name__.lower()]

    async def check_credentials(self, key: str, resource: str,
                                token_length: int):
        """
        Check credentials in database and return a token generated or None if
        credentials not found

        -----------------
        Args:
            key (str): Key request parameter
            resource (str): Resource request parameter
            token_length (int): Token length config parameter
        Returns:
            token (str): Token generated
        """
        q = await self.collaction.find_one({'key': key, 'resource': resource})
        if q is not None:
            self.client = q["client_id"]
            return generate_token(token_length)
        return q


'''
class Token(MongoModel):
    """Token Auth model."""

    def __init__(self, clientdb):
        super().__init__()
        self.clientdb = clientdb
        self.collaction = self.clientdb[self.__class__.__name__.lower()]

    @staticmethod
    def generate_token(length=100):
        """
        choose from all char of letter in uppercase or lowercase and
        punctuation signals
        """
        sources = string.ascii_letters + string.digits
        # sources = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(sources) for i in range(length))

    async def upsert_token(self, client_id: int):
        """
        Upsert Token in Database
        """
        token = self.generate_token()
        if await self.find_token(client_id) is None:
            doc = {"client_id": client_id, "token": token,
                   "create_at": datetime.utcnow(),
                   "update_at": datetime.utcnow()}
            result = await self.insert_token(doc)
        else:
            result = await self.update_token(client_id, token)

        return token

    async def find_token(self, client_id: int):
        """
        Find Token in Database
        """
        result = await self.collaction.find_one({'client_id': client_id})
        return result

    async def verify_token(self, token_id: int, token_time: int):
        """
        Find Token in Database
        """
        now = datetime.utcnow()
        delta = timedelta(minutes=token_time)
        time_query = now-delta
        print()
        print(time_query)
        print()
        result = await self.collaction.find_one({'token': token_id,
                                                 'update_at': {
                                                     '$gte': time_query}
                                                 })
        return result

    async def insert_token(self, document: dict):
        """
        Insert Token in Database
        """
        result = await self.collaction.insert_one(document)
        return document

    async def update_token(self, client_id, token):
        """
        Update Token in Database
        """
        result = await self.collaction.update_one({
            'client_id': client_id},
            {'$set': {"token": token, "update_at": datetime.utcnow()}})
        return result
'''