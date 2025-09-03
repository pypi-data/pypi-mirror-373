from __future__ import annotations


class EventTypes:
    LOGGED_IN = "logged_in"
    LOGGED_ERROR = "logged_error"
    LOGGED_OUT = "logged_out"
    
    CHAT_PRESENCE = "chat_presence"
    CHAT_SETTING = "chat_setting"
    
    MESSAGE = "message"
    MESSAGE_DELETE = "message_delete"
    MESSAGE_HISTORY_SYNC = "message_history_sync"
    MESSAGE_READ = "message_read"
    MESSAGE_STAR = "message_star"
    
    CONTACT = "contact"
    
    USER_PUSH_NAME = "user_push_name"
    USER_PICTURE = "user_picture"
    USER_PRESENCE = "user_presence"
    USER_STATUS = "user_status"
    
    CALL_OFFER = "call_offer"
    CALL_ACCEPT = "call_accept"
    CALL_TERMINATE = "call_terminate"