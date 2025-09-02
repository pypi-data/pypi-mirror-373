from django.urls import path
from . import models, views
from netbox.views.generic import ObjectChangeLogView

urlpatterns = (
    #Static Routes
    path('static-routes/', views.StaticRouteListView.as_view(), name='staticroute_list'),
    path('static-routes/add/', views.StaticRouteEditView.as_view(), name='staticroute_add'),
    path('static-routes/import/', views.StaticRouteImportView.as_view(), name='staticroute_import'),
    path('static-routes/<int:pk>/', views.StaticRouteView.as_view(), name='staticroute'),
    path('static-routes/<int:pk>/edit/', views.StaticRouteEditView.as_view(), name='staticroute_edit'),
    path('static-routes/<int:pk>/delete/', views.StaticRouteDeleteView.as_view(), name='staticroute_delete'),
    path('static-routes/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='staticroute_changelog', kwargs={
        'model': models.StaticRoute
    }),
    #Communities
    path('community/', views.CommunityListView.as_view(), name='community_list'),
    path('community/add/', views.CommunityEditView.as_view(), name='community_add'),
    path('community/<int:pk>/', views.CommunityView.as_view(), name='community'),
    path('community/<int:pk>/edit/', views.CommunityEditView.as_view(), name='community_edit'),
    path('community/<int:pk>/delete/', views.CommunityDeleteView.as_view(), name='community_delete'),
    path('community/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='community_changelog', kwargs={
        'model': models.Community
    }),
)
