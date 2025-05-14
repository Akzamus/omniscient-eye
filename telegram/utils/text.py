class Texts:
    class Bot:
        class Button:
            class Main:
                CHATS = '📊 Chats'
                USERS = '👥 Users'
                PER_USER = '🧑‍💼 Per user'
                HOME = '🏠 Main menu'

        class Message:
            START = '👋 Welcome! Please choose an option:'
            ACCESS_ERROR = 'You are not an admin!'
            HOME_PAGE = 'Back to main menu:'
            SELECTING_CHATS = 'Select chats:'
            CHAT_SELECTION_EMPTY_WARNING = '❗️Please select at least one chat.'
            SELECTING_USER_TYPES = 'Select user types:'
            USER_TYPE_SELECTION_EMPTY_WARNING = '❗️Please select at least one user type.'
            WRITING_USER_USERNAME = 'Please send the username you want to analyze:'
            INCORRECT_USERNAME_WARNING = '❗ Couldn’t resolve that username. Please send a valid one'
            USER_DATA_NOT_FOUND = '⚠️ No data found for user_id: {0}'
            SEPARATOR = '⋇⋆✦⋆⋇' * 6


RECOMMENDATION_NUMBER_TO_NAME = {
    1: 'no_join',
    2: 'risk_join',
    3: 'maybe_join',
    4: 'join',
    5: 'must_join'
}
