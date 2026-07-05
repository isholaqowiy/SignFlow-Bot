import os

def ensure_temp_directory():
    from config import TEMP_DIR
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

def clean_user_files(user_id: int):
    from config import TEMP_DIR
    if not os.path.exists(TEMP_DIR):
        return
    for filename in os.listdir(TEMP_DIR):
        if filename.startswith(f"sig_{user_id}") or filename.startswith(f"doc_{user_id}"):
            try:
                os.remove(os.path.join(TEMP_DIR, filename))
            except Exception:
                pass

