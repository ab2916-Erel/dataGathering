import pymongo
from bson.objectid import ObjectId

class UserEventManager:
    def __init__(self, db_url, db_name):
        self.client = pymongo.MongoClient(db_url)
        self.db = self.client[db_name]

    def add_user(self, username, password):
        user_data = {
            "username": username,
            "password": password,
            "events": [],
            "backup_events": []
        }
        self.db.users.insert_one(user_data)

    def delete_user(self, username):
        self.db.users.delete_one({"username": username})

    def user_exists(self, username):
        return self.db.users.count_documents({"username": username}) > 0

    def check_password(self, username, password):
        user = self.db.users.find_one({"username": username})
        if user and user["password"] == password:
            return True
        return False

    def get_user_event_count(self, username):
        user = self.db.users.find_one({"username": username})
        if user:
            return len(user["events"])
        return 0

    def get_user_event_details(self, username):
        user = self.db.users.find_one({"username": username})
        if user:
            return user.get("events", [])
        return []

    def add_event_to_user(self, username, data_type, details, date):
        event_id = str(ObjectId())
        event_data = {"id": event_id, "data_type": data_type, "details": details, "date": date}
        self.db.users.update_one(
            {"username": username},
            {"$push": {"events": event_data}}
        )
        return event_id

    def get_event_id_by_date(self, username, target_date):
        user = self.db.users.find_one({"username": username, "events": {"$elemMatch": {"date": target_date}}})
        if user:
            matching_event = next((event["id"] for event in user["events"] if event.get("date") == target_date), None)
            return matching_event
        return None

    def get_event_details_by_id(self, username, event_id):
        user = self.db.users.find_one({"username": username, "events.id": event_id})
        if user:
            matching_event = next((event for event in user["events"] if event.get("id") == event_id), None)
            return matching_event
        return None

    def delete_event_of_user(self, username, event_id):
        query = {"username": username}
        update = {"$pull": {"events": {"id": event_id}}}
        self.db.users.update_one(query, update)

    def update_event_details(self, username, event_id, data_type, new_details, new_date):
        query = {"username": username, "events.id": event_id}
        update = {
            "$set": {
                "events.$.data_type": data_type,
                "events.$.details": new_details,
                "events.$.date": new_date
            }
        }
        self.db.users.update_one(query, update)

    def get_user_backup_event_count(self, username):
        user = self.db.users.find_one({"username": username})
        if user:
            return len(user.get("backup_events", []))
        return 0

    def get_user_backup_event_details(self, username):
        user = self.db.users.find_one({"username": username})
        if user:
            return user.get("backup_events", [])
        return []

    def add_backup_event_to_user(self, username, data_type, details, date):
        event_id = str(ObjectId())
        event_data = {"id": event_id, "data_type": data_type, "details": details, "date": date}
        self.db.users.update_one(
            {"username": username},
            {"$push": {"backup_events": event_data}}
        )
        return event_id

    def get_backup_event_id_by_date(self, username, target_date):
        user = self.db.users.find_one({"username": username, "backup_events": {"$elemMatch": {"date": target_date}}})
        if user:
            matching_event = next((event["id"] for event in user["backup_events"] if event.get("date") == target_date),
                                  None)
            return matching_event
        return None

    def get_backup_event_details_by_id(self, username, event_id):
        user = self.db.users.find_one({"username": username, "backup_events.id": event_id})
        if user:
            matching_event = next((event for event in user["backup_events"] if event.get("id") == event_id), None)
            return matching_event
        return None

    def delete_backup_event_of_user(self, username, event_id):
        query = {"username": username}
        update = {"$pull": {"backup_events": {"id": event_id}}}
        self.db.users.update_one(query, update)

    def update_backup_event_details(self, username, event_id, data_type, new_details, new_date):
        query = {"username": username, "backup_events.id": event_id}
        update = {
            "$set": {
                "backup_events.$.data_type": data_type,
                "backup_events.$.details": new_details,
                "backup_events.$.date": new_date
            }
        }
        self.db.users.update_one(query, update)

