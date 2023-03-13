from django.contrib import admin
from django.urls import include, path

handler404 = 'core.views.page_not_found'


urlpatterns = [
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('about/', include('about.urls', namespace='about')),
    path('admin/', admin.site.urls),
    path('', include('posts.urls', namespace='posts'))]
