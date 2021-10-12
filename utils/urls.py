from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('debit_note/', include('debit_note.urls')),
]
