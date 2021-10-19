import requests
from django import forms
from django.template.loader import get_template
from string import digits
from datetime import datetime

from utils.settings import COMPANY_SEARCH_API_DETAIL_URL, COMPANY_SEARCH_API_DETAIL_QUERY_PARAM
from .models import DebitNote, Currency
import os


def create_debit_note_number(issue_date, request):
    new_note_month = issue_date.month
    new_note_year = issue_date.year
    notes_by_new_note_month = DebitNote.objects\
        .filter(
            issue_date__month=new_note_month,
            issue_date__year=new_note_year,
            company_creator=request.user.company
        )
    if not notes_by_new_note_month.exists():
        new_note_number = f'1/{new_note_month}/{new_note_year}'
        return new_note_number
    last_note_number = notes_by_new_note_month.last().number
    last_note_serial_number = last_note_number.split('/')[0]
    new_note_count = int(last_note_serial_number) + 1
    new_note_number = f'{new_note_count}/{new_note_month}/{new_note_year}'
    return new_note_number


def assign_fields_for_new_note(new_note, new_position, request):
    issue_date = new_note.issue_date
    new_note.number = create_debit_note_number(issue_date, request)
    new_note.creator = request.user
    new_note.company_creator = request.user.company
    new_note.currency = new_position.currency.name
    new_note.save()
    new_note.positions.add(new_position)


# def create_note_in_pdf(template_src, debit_note_pk):
#     debit_note = DebitNote.objects.get(pk=debit_note_pk)
#     template = get_template(template_src)
#     html_content = template.render({'note': debit_note})
#     new_pdf_file_name = f"{debit_note.number.replace('/', '_')}.pdf"
#     pdf_content = pydf.generate_pdf(html_content)
#
#     from io import BytesIO
#     bytes_ = BytesIO(pdf_content)
#     bytes_name = new_pdf_file_name
#
#     with open(f'{new_pdf_file_name}', 'wb') as f:
#         f.write(pdf_content)
#     return new_pdf_file_name
def create_temp_company_directory(company_name):
    if not 'tmp' in os.listdir():
        os.mkdir('tmp')
    company_name_for_directory = company_name.lower().replace(' ', '_')
    if not company_name_for_directory in os.listdir('tmp/'):
        os.mkdir(f'tmp/{company_name_for_directory}')
    return company_name_for_directory


def create_filenames_for_pdf_and_html(note_number):
    pdf_filename = f"{note_number.replace('/', '_')}.pdf"
    html_filename = f"{note_number.replace('/', '_')}.html"
    return pdf_filename, html_filename


def create_pdf_and_html_files(debit_note, template_src, directory_name):
    pdf_filename, html_filename = create_filenames_for_pdf_and_html(debit_note.number)
    new_pdf_file = open(f'tmp/{directory_name}/{pdf_filename}', 'wb')
    new_pdf_file.close()
    template = get_template(template_src)
    html_content = template.render({'note': debit_note})
    with open(f'tmp/{directory_name}/{html_filename}', 'wb') as html:
        html.write(html_content.encode())
    return pdf_filename, html_filename


def convert_html_to_pdf(template_src, debit_note_pk, request):
    company_name = request.user.company.name
    company_name_for_dir = create_temp_company_directory(company_name)
    debit_note = DebitNote.objects.get(pk=debit_note_pk)
    new_pdf_file_name, new_html_file_name = create_pdf_and_html_files(debit_note, template_src, company_name_for_dir)
    path_to_html = f'tmp/{company_name_for_dir}/{new_html_file_name}'
    path_to_pdf = f'tmp/{company_name_for_dir}/{new_pdf_file_name}'
    os.system(f'wkhtmltopdf {path_to_html} {path_to_pdf}')
    return path_to_pdf


class CompanyDetailsFromAPIRequest:
    date_format = '%Y-%m-%d'
    __date_str = datetime.strftime(datetime.now().date(), date_format)

    def __init__(self, tax_id):
        if not isinstance(tax_id, str):
            raise TypeError('Налоговый номер должен быть строкой')
        for _ in tax_id:
            if not _ in digits:
                raise TypeError('Налоговый номер должен состоять только из цифр')
        self.tax_id = tax_id
        self.url = f'{COMPANY_SEARCH_API_DETAIL_URL}{self.tax_id}{COMPANY_SEARCH_API_DETAIL_QUERY_PARAM}{self.get_current_date_string}'
        self.details = {
            'company': {
                'name': None,
                'tax_id': None
            },
            'address': {
                'zip_code': None,
                'city_name': None,
                'street_name': None,
                'house_number': None
            }
        }

    @property
    def get_current_date_string(self):
        return self.__date_str

    def __make_request(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            return response
        else:
            raise ConnectionError('Ошибка запроса к API серверу. Проверьте параметры запроса.')

    @property
    def json_response(self):
        response = self.__make_request()
        return response.json()

    @staticmethod
    def __parse_full_address(full_address):
        full_address_list = full_address.split(',')
        street_and_house_list = full_address_list[0].strip().split(' ')
        zip_code_and_city_name_list = full_address_list[1].strip().split(' ')
        address_details = {
            'zip_code': zip_code_and_city_name_list[0],
            'city_name': zip_code_and_city_name_list[1],
            'street_name': street_and_house_list[0],
            'house_number': street_and_house_list[1]
        }
        return address_details

    @staticmethod
    def __check_available_address(response):
        if response['result']['subject']['workingAddress']:
            return response['result']['subject']['workingAddress']
        else:
            return response['result']['subject']['residenceAddress']

    @property
    def company_details(self):
        response = self.json_response
        self.details['company']['name'] = response['result']['subject']['name']
        self.details['company']['tax_id'] = response['result']['subject']['nip']
        full_address = CompanyDetailsFromAPIRequest.__check_available_address(response)
        address_details = CompanyDetailsFromAPIRequest.__parse_full_address(full_address)
        self.details['address']['zip_code'] = address_details['zip_code']
        self.details['address']['city_name'] = address_details['city_name']
        self.details['address']['street_name'] = address_details['street_name']
        self.details['address']['house_number'] = address_details['house_number']
        return self.details

    def prepare_initial_data_for_company_and_address_forms(self):
        new_purchaser = self.company_details
        company_form_initial = [
            ('name', new_purchaser['company']['name']),
            ('tax_id', new_purchaser['company']['tax_id'])
        ]
        address_form_initial = [
            ('zip_code', new_purchaser['address']['zip_code']),
            ('city_name', new_purchaser['address']['city_name']),
            ('street_name', new_purchaser['address']['street_name']),
            ('house_number', new_purchaser['address']['house_number'])
        ]
        return company_form_initial, address_form_initial


def set_correct_queryset_for_currency(form_instance, request):

    """Check if form_instance is form or formset and change queryset for currency field from default to
        queryset by necessary company_creator(MainCompany model instance). Using in view, where we work with
        PositionCreateForm and PositionInlineFormset."""

    if isinstance(form_instance, forms.BaseInlineFormSet):
        form_instance.initial_forms[0].fields['currency'].queryset = Currency.objects.filter(
            company_creator=request.user.company)
    if isinstance(form_instance, forms.BaseForm):
        form_instance.fields['currency'].queryset = Currency.objects.filter(
            company_creator=request.user.company)
