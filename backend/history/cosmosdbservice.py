import uuid
from datetime import datetime
from azure.cosmos.aio import CosmosClient
from azure.cosmos import exceptions
  
class CosmosConversationClient():
    
    def __init__(self, cosmosdb_endpoint: str, credential: any, database_name: str, container_name: str, users_container_name: str, invitations_container_name: str, enable_message_feedback: bool = False):
        self.cosmosdb_endpoint = cosmosdb_endpoint
        self.credential = credential
        self.database_name = database_name
        self.container_name = container_name
        self.users_container_name = users_container_name
        self.invitations_container_name = invitations_container_name
        self.enable_message_feedback = enable_message_feedback
        try:
            self.cosmosdb_client = CosmosClient(self.cosmosdb_endpoint, credential=credential)
        except exceptions.CosmosHttpResponseError as e:
            if e.status_code == 401:
                raise ValueError("Invalid credentials") from e
            else:
                raise ValueError("Invalid CosmosDB endpoint") from e

        try:
            self.database_client = self.cosmosdb_client.get_database_client(database_name)
        except exceptions.CosmosResourceNotFoundError:
            raise ValueError("Invalid CosmosDB database name") 
        
        try:
            self.container_client = self.database_client.get_container_client(container_name)
        except exceptions.CosmosResourceNotFoundError:
            raise ValueError("Invalid CosmosDB container name") 
        
        try:
            self.user_container_client = self.database_client.get_container_client(users_container_name)
        except exceptions.CosmosResourceNotFoundError:
            raise ValueError("Invalid CosmosDB user container name") 
        
        try:
            self.invitations_container_client = self.database_client.get_container_client(invitations_container_name)
        except exceptions.CosmosResourceNotFoundError:
            raise ValueError("Invalid CosmosDB invitations container name") 
        

    async def ensure(self):
        if not self.cosmosdb_client or not self.database_client or not self.container_client:
            return False, "CosmosDB client not initialized correctly"
        try:
            database_info = await self.database_client.read()
        except:
            return False, f"CosmosDB database {self.database_name} on account {self.cosmosdb_endpoint} not found"
        
        try:
            container_info = await self.container_client.read()
        except:
            return False, f"CosmosDB container {self.container_name} not found"
        
        try:
            user_container_info = await self.user_container_client.read()
        except:
            return False, f"CosmosDB container {self.users_container_name} not found"
        
        try:
            invitation_container_info = await self.invitations_container_client.read()
        except:
            return False, f"CosmosDB container {self.invitations_container_client} not found"
            
        return True, "CosmosDB client initialized successfully"

    async def create_conversation(self, user_id, user_email = '', title = ''):
        conversation = {
            'id': str(uuid.uuid4()),  
            'type': 'conversation',
            'createdAt': datetime.utcnow().isoformat(),  
            'updatedAt': datetime.utcnow().isoformat(),  
            'userId': user_id,
            'userEmail': user_email,
            'title': title
        }
        ## TODO: add some error handling based on the output of the upsert_item call
        resp = await self.container_client.upsert_item(conversation)  
        if resp:
            return resp
        else:
            return False
    
    async def upsert_conversation(self, conversation):
        resp = await self.container_client.upsert_item(conversation)
        if resp:
            return resp
        else:
            return False

    async def delete_conversation(self, user_id, conversation_id):
        conversation = await self.container_client.read_item(item=conversation_id, partition_key=user_id)        
        if conversation:
            resp = await self.container_client.delete_item(item=conversation_id, partition_key=user_id)
            return resp
        else:
            return True

        
    async def delete_messages(self, conversation_id, user_id):
        ## get a list of all the messages in the conversation
        messages = await self.get_messages(user_id, conversation_id)
        response_list = []
        if messages:
            for message in messages:
                resp = await self.container_client.delete_item(item=message['id'], partition_key=user_id)
                response_list.append(resp)
            return response_list


    async def get_conversations(self, user_id, limit, sort_order = 'DESC', offset = 0):
        parameters = [
            {
                'name': '@userId',
                'value': user_id
            }
        ]
        query = f"SELECT * FROM c where c.userId = @userId and c.type='conversation' order by c.updatedAt {sort_order}"
        if limit is not None:
            query += f" offset {offset} limit {limit}" 
        
        conversations = []
        async for item in self.container_client.query_items(query=query, parameters=parameters):
            conversations.append(item)
        
        return conversations

    async def get_conversation(self, user_id, conversation_id):
        parameters = [
            {
                'name': '@conversationId',
                'value': conversation_id
            },
            {
                'name': '@userId',
                'value': user_id
            }
        ]
        query = f"SELECT * FROM c where c.id = @conversationId and c.type='conversation' and c.userId = @userId"
        conversations = []
        async for item in self.container_client.query_items(query=query, parameters=parameters):
            conversations.append(item)

        ## if no conversations are found, return None
        if len(conversations) == 0:
            return None
        else:
            return conversations[0]
 
    async def create_message(self, uuid, conversation_id, user_id, input_message: dict, user_email = ""):
        message = {
            'id': uuid,
            'type': 'message',
            'userId' : user_id,
            "userEmail": user_email,
            'createdAt': datetime.utcnow().isoformat(),
            'updatedAt': datetime.utcnow().isoformat(),
            'conversationId' : conversation_id,
            'role': input_message['role'],
            'content': input_message['content']
        }

        if self.enable_message_feedback:
            message['feedback'] = ''
        
        resp = await self.container_client.upsert_item(message)  
        if resp:
            ## update the parent conversations's updatedAt field with the current message's createdAt datetime value
            conversation = await self.get_conversation(user_id, conversation_id)
            if not conversation:
                return "Conversation not found"
            conversation['updatedAt'] = message['createdAt']
            await self.upsert_conversation(conversation)
            return resp
        else:
            return False
    
    async def update_message_feedback(self, user_id, message_id, feedback):
        message = await self.container_client.read_item(item=message_id, partition_key=user_id)
        if message:
            message['feedback'] = feedback
            resp = await self.container_client.upsert_item(message)
            return resp
        else:
            return False

    async def get_messages(self, user_id, conversation_id):
        parameters = [
            {
                'name': '@conversationId',
                'value': conversation_id
            },
            {
                'name': '@userId',
                'value': user_id
            }
        ]
        query = f"SELECT * FROM c WHERE c.conversationId = @conversationId AND c.type='message' AND c.userId = @userId ORDER BY c.timestamp ASC"
        messages = []
        async for item in self.container_client.query_items(query=query, parameters=parameters):
            messages.append(item)

        return messages
        
    async def get_user_details(self, user_id):
        query = "SELECT * FROM c WHERE c.userId = @userId"
        parameters = [
            {
                "name": "@userId",
                "value": user_id
            }
        ]

        async for item in self.user_container_client.query_items(
            query=query,
            parameters=parameters,
            partition_key=user_id
        ):
            return item  # Return first matching result

        return None  # No user found

    async def create_or_update_user(self, uuid, user_id, user_name, role):
        """Create or update user information in Cosmos DB"""
        try:
            user_container = self.user_container_client
            user_item = {
                "id": uuid,
                "userId": user_id,
                "name": user_name,
                "role": role,
                "createdAt": datetime.utcnow().isoformat(),
            }

            try:
                existing_user = await user_container.read_item(item=user_id, partition_key=user_id)
                # Update only if name changed
                if existing_user.get("name") != user_name:
                    existing_user["name"] = user_name
                    await user_container.replace_item(item=user_id, body=existing_user)
                return existing_user
            except exceptions.CosmosResourceNotFoundError:
                # User does not exist, create new
                created_user = await user_container.create_item(body=user_item)
                return created_user
        except Exception as e:
            print(e)
            return None
        
    async def check_invitation(self, user_email: str, user_invitation_code: str):
        query = "SELECT * FROM c WHERE c.email = @userEmail"
        parameters = [
            {
                "name": "@userEmail",
                "value": user_email
            }
        ]

        try:
            async for item in self.invitations_container_client.query_items(
                query=query,
                parameters=parameters,
                partition_key=user_email
            ):
                # Check if invitation code matches
                if item.get("invitationCode") == user_invitation_code:
                    # Update the invitation to reflect it has been checked
                    item["hasCheckedInvitation"] = True
                    item["lastCheckedAt"] = datetime.utcnow().isoformat()

                    # Upsert the modified item back into the container
                    await self.invitations_container_client.replace_item(item=item["id"], body=item)

                    return {
                        "valid": True,
                        "invited_user": item
                    }

            # If no invitation found
            return {
                "valid": False,
                "reason": "Invitation not found"
            }
        except Exception as e:
            print(f"Error checking invitation for {user_email}: {e}")
            return {
                "valid": False,
                "reason": "Error occurred while checking invitation"
            }
