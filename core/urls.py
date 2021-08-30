from django.urls import path
from django.conf.urls import url
from . import views
from django.contrib.auth.views import LoginView,LogoutView

app_name='core'

urlpatterns = [
    path('', views.index, name='home'),
    url(r'^signup/$', views.signup, name='signup'),
    path('login/',  LoginView.as_view(template_name='core/login.html'), name="login"),
    path('logout/', LogoutView.as_view(template_name= 'core/logged_out.html'),{'next_page': '/'}, name='logout'),

    
    path('addFriend/<friendId>/', views.addFriend, name='addFriend'),

    path('groupCreate/', views.GroupFormView, name='groupCreate'),
    path('friends/', views.friendsPage, name='friendsPage'),
    path('groups/', views.groupsPage, name='groupsPage'),
    path('addMember/<pk>', views.addMember, name='addMember'),
    path('eventCreate/', views.eventCreate, name='eventCreate'),
    
    path('debts/', views.debts, name='debtsPage'),
    path('settlements/', views.settlements, name='settlementsPage'),
    path('settle/<pk>', views.settle, name='settle'),
    path('groupInfo/<pk>',views.groupInfo, name='groupInfo')
]