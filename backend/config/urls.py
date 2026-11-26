from django.contrib import admin
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from desk.views import TicketViewSet,CategoryViewSet
router=DefaultRouter()
router.register('tickets',TicketViewSet,basename='ticket')
router.register('categories',CategoryViewSet)
urlpatterns=[path('admin/',admin.site.urls),path('api/',include(router.urls)),path('api-auth/',include('rest_framework.urls'))]
