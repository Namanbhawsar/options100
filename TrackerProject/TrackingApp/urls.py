from django.urls import path

from . import views

urlpatterns = [
    path('', views.loginUser,name='LoginUser'),

    path('logout/', views.logoutUser, name= 'LogoutUser'),
    path('nifty/logout/', views.logoutUser, name= 'LogoutUser'),
    path('banknifty/logout/', views.logoutUser, name= 'LogoutUser'),

    path('nifty/',views.showNiftyPage,name = 'Nifty'),
    path('banknifty/',views.showBankNiftyPage,name = 'Nifty'),

    path('fetchnifty/',views.fetchNiftyValues,name="FetchNifty"),
    path('fetchbanknifty/',views.fetchBankNiftyValues,name="FetchNifty"),

    path('fetchbankniftygraph/',views.showBankNiftyGraph,name="BankNiftyGraph"),

    path('download/<str:index>',views.download_file,name="Download"),
]
