class DialogServiceError(Exception):
    """Базовый класс для всех ошибок сервиса DialogService."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class MessageLimitExceededError(DialogServiceError):
    """Ошибка, превышено максимальное количество сообщений."""
    def __init__(self):
        super().__init__(f"Превышено максимальное количество сообщений в одном диалоге.")


class UserNotInChatError(DialogServiceError):
    """Ошибка, если пользователь, указанный в сообщениях, отсутствует в переданном списке пользователей."""
    def __init__(self, telegram_user_id: int):
        super().__init__(f"Пользователь с идентификатором {telegram_user_id} отсутствует в списке переданных пользователей.")
        self.telegram_user_id = telegram_user_id


class ChatAlreadyExistsError(DialogServiceError):
    """Ошибка, если чат с таким thread_id уже существует."""
    def __init__(self, thread_id: str):
        super().__init__(f"Чат с идентификатором потока {thread_id} уже существует.")
        self.thread_id = thread_id


class DatabaseError(DialogServiceError):
    """Ошибка, связанная с базой данных."""
    def __init__(self, original_exception: Exception):
        super().__init__("Произошла ошибка при взаимодействии с базой данных.")
        self.original_exception = original_exception


class ChatNotFound(DialogServiceError):
    def __init__(self, dialog_slug: str):
        super().__init__(f"Чат с идентификатором {dialog_slug} не найден.")
        self.chat_id = dialog_slug


class ReviewAlreadyExistsError(DialogServiceError):
    def __init__(self, dialog_slug: str):
        super().__init__(f"Голосование для чата с идентификатором {dialog_slug} уже существует.")
        self.chat_id = dialog_slug

