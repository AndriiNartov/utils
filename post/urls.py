from django.urls import path

from .views import \
    LetterCreateView,\
    LetterListView,\
    LetterUpdateView, \
    LetterDeleteMenuView, \
    LetterSingleDeleteView, \
    LetterDeleteByDateView


urlpatterns = [
    path('', LetterListView.as_view(), name='letter_all'),
    path('create/', LetterCreateView.as_view(), name='letter_create'),
    path('update/<int:pk>/', LetterUpdateView.as_view(), name='letter_update'),
    path('delete_list/', LetterDeleteMenuView.as_view(), name='letter_delete_menu'),
    path('delete/<int:pk>/', LetterSingleDeleteView.as_view(), name='letter_delete_one'),
    path('delete/', LetterDeleteByDateView.as_view(), name='letter_delete_by_date'),
]