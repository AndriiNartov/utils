from django.urls import path

from .views import PurchaserCompanyListView, PurchaserCompanyDetailView, \
    download_note_in_pdf, DebitNoteListView, IssuerCompanyCreateView, IssuerCompanyUpdateView, IssuerCompanyListView, \
    IssuerCompanyDetailView, BankAccountCreateView, DebitNoteDetailView, DebitNoteSettingsView, DebitNoteDeleteView, \
    DebitNoteCreateView, DebitNoteUpdateView, PurchaserCompanyCreateView, PurchaserCompanyUpdateView, \
    DebitNoteShowHTMLForPrintView, PurchaserCompanyDeleteView, IssuerCompanyDeleteView, BankAccountUpdateView, \
    BankAccountDeleteView, create_purchaser_companies_json_response

urlpatterns = [
    path('', DebitNoteListView.as_view(), name='note_all'),
    path('settings/', DebitNoteSettingsView.as_view(), name='note_settings'),
    path('create/', DebitNoteCreateView.as_view(), name='create_note'),
    path('preview/<int:pk>/', DebitNoteDetailView.as_view(), name='preview'),
    path('preview/<int:pk>/pdf/', download_note_in_pdf, name='download_note_pdf'),
    path('preview/<int:pk>/print/', DebitNoteShowHTMLForPrintView.as_view(), name='show_note_for_print'),
    path('update/<int:pk>/', DebitNoteUpdateView.as_view(), name='update_note'),
    path('delete/<int:pk>/', DebitNoteDeleteView.as_view(), name='delete_note'),
    path('purchaser/create/', PurchaserCompanyCreateView.as_view(), name='purchaser_create'),
    path('purchaser/update/<int:pk>/', PurchaserCompanyUpdateView.as_view(), name='purchaser_update'),
    path('purchaser/all/', PurchaserCompanyListView.as_view(), name='purchaser_all'),
    path('purchaser/detail/<int:pk>/', PurchaserCompanyDetailView.as_view(), name='purchaser_detail'),
    path('purchaser/delete/<int:pk>/', PurchaserCompanyDeleteView.as_view(), name='purchaser_delete'),
    path('issuer/create/', IssuerCompanyCreateView.as_view(), name='issuer_create'),
    path('issuer/update/<int:pk>/', IssuerCompanyUpdateView.as_view(), name='issuer_update'),
    path('issuer/all/', IssuerCompanyListView.as_view(), name='issuer_all'),
    path('issuer/detail/<int:pk>/', IssuerCompanyDetailView.as_view(), name='issuer_detail'),
    path('issuer/detail/<int:pk>/bank_account_create/', BankAccountCreateView.as_view(), name='issuer_bank_account_create'),
    path('issuer/detail/<int:pk>/bank_account_update/<int:account_pk>/', BankAccountUpdateView.as_view(), name='issuer_bank_account_update'),
    path('issuer/detail/<int:pk>/bank_account_delete/<int:account_pk>/', BankAccountDeleteView.as_view(), name='issuer_bank_account_delete'),
    path('issuer/delete/<int:pk>/', IssuerCompanyDeleteView.as_view(), name='issuer_delete'),

    path('note/create/ajax/', create_purchaser_companies_json_response, name='note_create_ajax'),
]
