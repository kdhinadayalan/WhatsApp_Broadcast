from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'contacts', views.ContactViewSet)
router.register(r'groups', views.ContactGroupViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
