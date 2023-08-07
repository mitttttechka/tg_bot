import db
import user

def handle_response(chat) -> str:
    user_id = chat.id
    text = chat.text

    person = user.User(user_id)
    if len(person.user_name) == 0:
        person.create_new_user()
        return "Hi! What's your name?"

    return "Answer"

