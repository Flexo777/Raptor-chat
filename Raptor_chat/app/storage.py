from datetime import datetime
from dataclasses import dataclass

@dataclass
class User:
    id: int
    username: str
    email: str
    online: bool = False

class DatabaseManager:
    def __init__(self):
        self.users = []
        self.messages = []
    
    def add_user(self, username, email, password):
        user = User(
            id=len(self.users) + 1,
            username=username,
            email=email,
            online=True
        )
        self.users.append(user)
        return user
    
    def get_user(self, user_id):
        return next((u for u in self.users if u.id == user_id), None)
    
    def get_online_users(self):
        return [u for u in self.users if u.online]

class LogNode:
    def __init__(self, message):
        self.message = message
        self.next = None

class LogLinkedList:
    def __init__(self):
        self.head = None

    def add_log(self, message):
        new_node = LogNode(message)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def get_logs(self):
        logs = []
        current = self.head
        while current:
            logs.append(current.message)
            current = current.next
        return logs

class LogManager:
    def __init__(self):
        self.logs = LogLinkedList()
    
    def add_log(self, message):
        self.logs.add_log(message)
    
    def get_logs(self):
        return self.logs.get_logs()