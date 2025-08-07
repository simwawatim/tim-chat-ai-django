from chatai.views import (
    chat_history,
    login,
    register,
    user_details,
    gemini_chat,

)
from core.urls import path
urlpatterns = [
    path('chat/history/', chat_history, name='chat_history'),
    path('api/user/', user_details, name='user_details'),
    path('chat/', gemini_chat, name='gemini_chat'),
    path("register/", register, name="register"),
    path("login/", login, name="login"),
]
