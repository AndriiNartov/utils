from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, FormView, ListView, UpdateView

from .forms import LetterCreateForm, LetterDeleteByDateForm, LetterUpdateForm
from .models import Letter
from .services import set_status_for_letter


class LetterCreateView(CreateView):
    model = Letter
    template_name = 'post/letter_create.html'
    form_class = LetterCreateForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_letter = form.save(commit=False)
            new_letter.status_date = form.data['sending_date']
            new_letter.save()
            return HttpResponseRedirect(reverse_lazy('letter_all'))
        return render(request, 'post/letter_create.html')


class LetterUpdateView(UpdateView):
    model = Letter
    template_name = 'post/letter_update.html'
    form_class = LetterUpdateForm

    def post(self, request, *args, **kwargs):
        letter = self.get_object()
        form = LetterUpdateForm(request.POST, instance=letter)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy('letter_all'))
        return render(request, 'post/letter_update.html', {'form': form})


class LetterListView(ListView):
    model = Letter
    template_name = 'post/letter_list.html'
    context_object_name = 'letters'
    paginate_by = 10

    def get_queryset(self):
        set_status_for_letter()
        return Letter.objects.all().order_by('sending_date')


class LetterDeleteMenuView(LetterListView):
    template_name = 'post/letter_delete_menu.html'


class LetterSingleDeleteView(DeleteView):
    model = Letter
    success_url = reverse_lazy('letter_delete_menu')


class LetterDeleteByDateView(FormView):
    template_name = 'post/letter_delete_by_date.html'
    form_class = LetterDeleteByDateForm
    success_url = reverse_lazy('letter_all')

    def post(self, request, *args, **kwargs):
        form = LetterDeleteByDateForm(request.POST)
        if form.is_valid():
            chosen_date = form.data['date']
            records_older_then_chosen_date = Letter.objects.filter(sending_date__lt=chosen_date)
            for record in records_older_then_chosen_date:
                print(record)
                record.delete()
            return HttpResponseRedirect(reverse_lazy('letter_all'))


