from django.contrib import admin
from django.urls import include, path, reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.conf import settings
from django.conf.urls.static import static

from blog.views import UserCreateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('pages/', include('pages.urls')),
    path('', include('django.contrib.auth.urls')),
    path('auth/registration/', UserCreateView.as_view(), name='registration'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.internal_server_error'
