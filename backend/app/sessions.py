sessions = {}

def start_session(user_id):
    sessions[user_id] = {"step": "product"}

def get_session(user_id):
    return sessions.get(user_id)

def clear_session(user_id):
    sessions.pop(user_id, None)