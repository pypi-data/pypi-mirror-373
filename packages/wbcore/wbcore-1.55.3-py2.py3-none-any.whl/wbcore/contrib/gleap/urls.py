from django.urls import path

from wbcore.contrib.gleap.views import GleapAPITokenAPIView, GleapUserIdentityAPIView

urlpatterns = [
    path("user_identity/", GleapUserIdentityAPIView.as_view(), name="user_identity"),
    path("api_token/", GleapAPITokenAPIView.as_view(), name="api_token"),
]
