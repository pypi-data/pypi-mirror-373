import re
from typing import Callable, Self

from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters, \
	ChatJoinRequestHandler

from bojango.action.dispatcher import ActionManager
from bojango.action.screen import ActionScreen
from bojango.core.utils import pop_user_data_kwargs


class Router:
	"""Класс маршрутизации для обработки команд и callback запросов."""

	# Ограничения телеграмма в длину callback_data 64 символа, также берем qid, при формировании кнопок ?qid=25042272,
	# в итоге максимальная длина callback действия 51, и 1 на запас
	MAX_QUERY_LENGTH: int = 50
	_instance: Self | None = None

	def __new__(cls, action_manager: ActionManager | None = None) -> Self:
		if cls._instance is None:
			if action_manager is None:
				raise ValueError('ActionManager должен быть передан при первом создании Router.')
			cls._instance = super().__new__(cls)
			cls._instance._action_manager = action_manager
			cls._instance._commands = {}
			cls._instance._callbacks = {}
			cls._instance._message_handlers = []
			cls._instance._audio_handler = None
			cls._instance._voice_handler = None
			cls._instance._video_note_handler = None
			cls._instance._file_handler = None
			cls._instance._video_handler = None
			cls._instance._image_handler = None
			cls._instance._join_request_handler = None
			cls._instance._any_handler = None
		return cls._instance

	def register_command(self, command: str, handler: Callable) -> None:
		"""Регистрирует команду для обработки.

    :param command: Название команды.
    :param handler: Обработчик команды.
    """
		self._commands[command] = handler
		self._action_manager.register_action(command, handler)

	def register_callback(self, query: str, handler: Callable) -> None:
		"""Регистрирует callback для обработки.

    :param query: Шаблон callback.
    :param handler: Обработчик callback.
    """
		self._callbacks[query] = handler
		self._action_manager.register_action(query, handler)

	def register_message(self, handler: Callable, pattern: str = '.*') -> None:
		"""Регистрирует обработчик сообщений."""
		self._message_handlers.append((pattern, handler))

	def register_audio_handler(self, handler: Callable) -> None:
		"""
		Регистрирует обработчик аудоифайлов.

		:param handler: Функция-обработчик аудиофайлов.
		"""
		self._audio_handler = handler

	def register_voice_handler(self, handler: Callable) -> None:
		"""
		Регистрирует обработчик голосовых сообщений.

		:param handler: Функция-обработчик голосовых сообщений.
		"""
		self._voice_handler = handler

	def register_video_note_handler(self, handler: Callable) -> None:
		"""
		Регистрирует обработчик видео-заметок.

		:param handler: Функция-обработчик видео-заметок.
		"""
		self._video_note_handler = handler

	def register_file_handler(self, handler: Callable) -> None:
		"""
		Регистрирует обработчик файлов.

		:param handler: Функция-обработчик файлов.
		"""
		self._file_handler = handler

	def register_video_handler(self, handler: Callable) -> None:
		"""
		Регистрирует обработчик видео.

		:param handler: Функция-обработчик видео.
		"""
		self._video_handler = handler

	def register_image_handler(self, handler: Callable) -> None:
		"""
		Регистрирует обработчик сообщений с изображениями

		:param handler: Функция-обработчик изображений
		"""
		self._image_handler = handler

	def register_join_request_handler(self, handler: Callable) -> None:
		"""
		Регистрирует обработчик входов в канал или чат

		:param handler: Функция-обработчик входов в канал или чат
		"""
		self._join_request_handler = handler

	def register_any_handler(self, handler: Callable) -> None:
		"""
		Регистрирует обработчик любого медиа

		:param handler: Функция-обработчик любого медиа
		"""
		self._any_handler = handler

	def attach_to_application(self, application: Application) -> None:
		"""Привязывает маршруты к Telegram Application.

    :param application: Экземпляр Telegram Application.
    """
		for command, handler in self._commands.items():
			application.add_handler(CommandHandler(command, handler))

		for query, handler in self._callbacks.items():
			application.add_handler(CallbackQueryHandler(handler, pattern=f'^{re.escape(query)}(?:\\?|$)'))

		for pattern, handler in self._message_handlers:
			application.add_handler(MessageHandler(filters.TEXT & filters.Regex(pattern), handler))

		if self._audio_handler:
			application.add_handler(MessageHandler(filters.AUDIO, self._audio_handler))

		if self._voice_handler:
			application.add_handler(MessageHandler(filters.VOICE, self._voice_handler))

		if self._video_note_handler:
			application.add_handler(MessageHandler(filters.VIDEO_NOTE, self._video_note_handler))

		if self._video_handler:
			application.add_handler(MessageHandler(filters.VIDEO, self._video_handler))

		if self._image_handler:
			application.add_handler(MessageHandler(filters.PHOTO, self._image_handler))

		if self._file_handler:
			application.add_handler(MessageHandler(filters.ATTACHMENT, self._file_handler))

		if self._join_request_handler:
			application.add_handler(ChatJoinRequestHandler(self._join_request_handler))

		if self._any_handler:
			ANY_MEDIA = filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.ATTACHMENT | filters.AUDIO | filters.VOICE | filters.VIDEO_NOTE
			ANY_TEXT_OR_CAPTION = filters.TEXT | filters.CAPTION

			application.add_handler(MessageHandler(ANY_TEXT_OR_CAPTION | ANY_MEDIA, self._any_handler))

	def get_routes(self) -> dict[str, Callable]:
		"""Возвращает все зарегистрированные маршруты.

    :return: Словарь маршрутов.
    """
		return {**self._commands, **self._callbacks}


def _wrap_handler(handler: Callable) -> Callable:
	"""Обёртка для обработки async_generator и передачи аргументов."""

	async def wrapped_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs) -> None:
		"""
		Обработчик, принимающий аргументы.

		:param update: Объект обновления Telegram.
		:param context: Контекст.
		:param args: Дополнительные аргументы.
		"""
		kwargs = {**kwargs, **pop_user_data_kwargs(update.callback_query, context.user_data)}
		# try
		result = handler(update, context, **kwargs)

		if hasattr(result, '__aiter__'):
			async for screen in result:
				if isinstance(screen, ActionScreen):
					await screen.render(update, context)
				else:
					raise ValueError('Обработчик должен возвращать ActionScreen.')
		else:
			await result

	return wrapped_handler


def command(name: str) -> Callable:
	"""Декоратор для регистрации команды.

  :param name: Название команды.
  :return: Обёрнутый обработчик.
  """

	def decorator(handler: Callable) -> Callable:
		router = Router()
		router.register_command(name, _wrap_handler(handler))
		return handler

	return decorator


def callback(query: str) -> Callable:
	"""Декоратор для регистрации callback.

  :param query: Шаблон callback.
  :return: Обёрнутый обработчик.
  """

	if len(query) > Router.MAX_QUERY_LENGTH:
		raise ValueError(f'Callback name "{query}" is too long ({len(query)} chars). '
										 f'Max length: {Router.MAX_QUERY_LENGTH}.')

	def decorator(handler: Callable) -> Callable:
		router = Router()
		router.register_callback(query, _wrap_handler(handler))
		return handler

	return decorator


def message(pattern: str = ".*") -> Callable:
	"""
	Декоратор для регистрации хендлера текстовых сообщений.

	:param pattern: Регулярное выражение для фильтрации сообщений.
	"""

	def decorator(handler: Callable) -> Callable:
		router = Router()
		router.register_message(handler, pattern)
		return handler

	return decorator


def image() -> Callable:
	"""
	Декоратор для регистрации обработчика сообщений с изображениями
	"""

	def decorator(handler: Callable) -> Callable:
		router = Router()
		router.register_image_handler(handler)
		return handler
	
	return decorator

def audio() -> Callable:
	"""
	Декоратор для регистрации обработчика аудиофайлов.
	"""

	def decorator(handler: Callable) -> Callable:
		router = Router()
		router.register_audio_handler(handler)
		return handler

	return decorator


def voice() -> Callable:
	"""
	Декоратор для регистрации обработчика голосовых сообщений.
	"""

	def decorator(handler: Callable) -> Callable:
		router = Router()
		router.register_voice_handler(handler)
		return handler

	return decorator


def video_note() -> Callable:
	"""
	Декоратор для регистрации обработчика видео-заметок.
	"""

	def decorator(handler: Callable) -> Callable:
		router = Router()
		router.register_video_note_handler(handler)
		return handler

	return decorator


def file() -> Callable:
	"""
	Декоратор для регистрации обработчика голосовых сообщений.
	"""

	def decorator(handler: Callable) -> Callable:
		router = Router()
		router.register_file_handler(handler)
		return handler

	return decorator


def video() -> Callable:
	"""
	Декоратор для регистрации обработчика голосовых сообщений.
	"""

	def decorator(handler: Callable) -> Callable:
		router = Router()
		router.register_video_handler(handler)
		return handler

	return decorator


def join_request() -> Callable:
	"""
	Декоратор для регистрации обработчика голосовых сообщений.
	"""

	def decorator(handler: Callable) -> Callable:
		router = Router()
		router.register_join_request_handler(handler)
		return handler

	return decorator


def any_message() -> Callable:
	"""
	Декоратор для регистрации обработчика голосовых сообщений.
	"""

	def decorator(handler: Callable) -> Callable:
		router = Router()
		router.register_any_handler(handler)
		return handler

	return decorator