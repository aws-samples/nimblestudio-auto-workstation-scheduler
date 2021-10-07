from typing import List
from utils.client_utils import get_identity_client

class IdentityHelper():

    def __init__(self):
        self.identity_client = get_identity_client()

    def describe_identity_user(self, identity_store_id : str, user_id : str) -> dict:
        return self.identity_client.describe_user(
            IdentityStoreId=identity_store_id,
            UserId=user_id
        )

    def list_identity_users(self, identity_store: str, user_name: str, next_token : str or None) -> dict:
        # List cannot be called without a filter: https://github.com/boto/boto3/issues/2681
        filters =   [
                        {
                            'AttributePath': 'UserName',
                            'AttributeValue': user_name
                        },
                    ]
        if next_token == None:
            return self.identity_client.list_users(
                            IdentityStoreId=identity_store,
                            Filters=filters
                        )
        return self.identity_client.list_users(
                            IdentityStoreId=identity_store,
                            Filters=filters,
                            NextToken=next_token
                        )

    def search_identity_stores_for_user_name(self, user_name : str, identity_store_ids : List[str]) -> str or None:
        users = list()
        for id in identity_store_ids:
            try:
                response = self.list_identity_users(id, user_name, None)
                for user in response['Users']:
                    users.append(user)
                while 'NextToken' in response.keys():
                    response = self.list_identity_users(id, user_name, response['NextToken'])
                    for user in response['Users']:
                        users.append(user)
            except Exception as e:
                print(e)
        
        for user in users:
            if user['UserName'] == user_name:
                return user['UserId']
        return None