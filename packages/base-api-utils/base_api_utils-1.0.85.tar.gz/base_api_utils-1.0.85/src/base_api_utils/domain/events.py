from enum import Enum

class DomainEvent(Enum):
    AUTH_ACCESS_RIGHT_ADDED = "auth_access_right_added"
    AUTH_ACCESS_RIGHT_REMOVED = "auth_access_right_removed"
    AUTH_USER_ADDED_TO_GROUP = "auth_user_added_to_group"
    AUTH_USER_REMOVED_FROM_GROUP = "auth_user_removed_from_group"
    AUTH_USER_ADDED_TO_SPONSOR_AND_SUMMIT = "auth_user_added_to_sponsor_and_summit"
    AUTH_USER_REMOVED_FROM_SPONSOR_AND_SUMMIT = "auth_user_removed_from_sponsor_and_summit"
    AUTH_USER_REMOVED_FROM_SUMMIT = "auth_user_removed_from_summit"
