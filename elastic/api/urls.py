from django.urls import path

from elastic.api.views import GoogleView, AppleView

urlpatterns = [
    path('auth/google/verify/', GoogleView.as_view()),
    path('auth/apple/verify/', AppleView.as_view())
]
