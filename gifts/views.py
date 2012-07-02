import csv 
import django_tables2 as tables
from django_tables2 import RequestConfig
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from gifts.models import Contact, Donation, Ask
from django_tables2.utils import A
from django.contrib.auth.decorators import login_required
from gifts.forms import SearchForm, UploadCSVForm
from django.core.context_processors import csrf

class MyCheckBoxColumn(tables.CheckBoxColumn):
    header = tables.Column.header

class ContactTable(tables.Table):
    name = tables.LinkColumn("contact_record", args=[A("pk")])

    class Meta:
        model = Contact
        exclude = ('id', )
        attrs = {'class': 'paleblue'}

class SingleContactTable(ContactTable):
    class Meta:
        attrs = {'class': 'paleblue'}
        sequence = ('name', 'street')
        orderable = False

class DonationTable(tables.Table):
    id = tables.Column(visible = False)
    contact = tables.LinkColumn("contact_record", args=[A("contact_id")])

    def render_amount(self, value):
        return "%10.2f" % value

    class Meta:
        model = Donation
        attrs = {'class': 'paleblue'}

class SingleDonationTable(DonationTable):
    id = tables.Column(visible = False)
    contact = tables.Column(visible = False)

    class Meta:
        attrs = {'class': 'paleblue'}


class ShortDonationTable(tables.Table):
    date = tables.Column()
    contact = tables.LinkColumn("contact_record", args=[A("contact_id")])
    amount = tables.Column()

    def render_amount(self, value):
        return "%10.2f" % value

    class Meta:
        attrs = {'class': 'paleblue'}
        orderable = False


class AskTable(tables.Table):
    id = tables.Column(visible = False)
    contact = tables.Column(visible = False)

    class Meta:
        model = Ask
        attrs = {'class': 'paleblue'}

@login_required
def index(request):
    donations_table = ShortDonationTable(Donation.objects.order_by('-date')[:5])
    RequestConfig(request, paginate = False).configure(donations_table)
    return render(request, 'gifts/index.html', {'donation': donations_table})

@login_required
def contacts(request):
    contact_table = ContactTable(Contact.objects.all())
    RequestConfig(request, paginate = False).configure(contact_table)
    return render(request, 'gifts/contacts.html', {'contact': contact_table})

@login_required
def donations(request):
    donations_table = DonationTable(Donation.objects.all())
    RequestConfig(request, paginate = False).configure(donations_table)
    return render(request, 'gifts/donations.html', {'donation': donations_table})

@login_required
def contact_record(request, contact_id):
    contact_table = SingleContactTable(Contact.objects.filter(pk=contact_id))
    donation_table = SingleDonationTable(Donation.objects.filter(contact_id=contact_id))
    ask_table = AskTable(Ask.objects.filter(contact_id=contact_id))
    RequestConfig(request, paginate = None).configure(contact_table)
    return render(request, 'gifts/contact_detail.html', 
                  {'contact': contact_table,
                   'donation': donation_table,
                   'ask': ask_table})
@login_required
def asks(request):
    table = AskTable(Gift.objects.all())
    RequestConfig(request).configure(table)
    return render(request, 'gifts/asks.html', {'table': table})

@login_required
def search(request):
    # results start as an empty table of the correct type
    results = ContactTable([]) 
    if request.method == 'POST': # If the form has been submitted...
        form = SearchForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass

            # first get all the donations
            d = Donation.objects.all()
            d_all = d.values_list('contact', flat = True)

            # now figure out which donations match the critera

            if form.cleaned_data['amount_min'] is not None:
                d = d.filter(amount__gte=form.cleaned_data['amount_min'])

            if form.cleaned_data['amount_max'] is not None:
                d = d.filter(amount__lte=form.cleaned_data['amount_max'])

            if form.cleaned_data['donate_date_min'] is not None:
                d = d.filter(date__gte=form.cleaned_data['donate_date_min'])

            if form.cleaned_data['donate_date_max'] is not None:
                d = d.filter(date__lte=form.cleaned_data['donate_date_max'])

            # get these contact indicies
            d_ids = d.values_list('contact', flat = True)

            # first get all the asks
            a = Ask.objects.all()
            a_all = a.values_list('contact', flat = True)

            # figure out which asks match the critera

            if form.cleaned_data['ask_date_min'] is not None:
                a = a.filter(date__gte=form.cleaned_data['ask_date_min'])

            if form.cleaned_data['ask_date_max'] is not None:
                a = a.filter(date__lte=form.cleaned_data['ask_date_max'])

            # get these contact indicies
            a_ids = a.values_list('contact', flat = True)

            # now comes some rather annoying set manipulations
            # as we choose which set of contacts to start with
            # by default it is all of them
            query  = Contact.objects.all()

            # maybe start with those who have donated
            if form.cleaned_data['show_non_donors']:
                # exclude those who have already failed to match
                query = query.exclude(id__in = set(d_all)-set(d_ids))
            else:
                # limit us do just donors who did match
                query = query.filter(id__in = d_ids)

            # maybe start with those who have been asked
            if form.cleaned_data['show_never_asked']:
                # exclude those who have already failed to match
                query = query.exclude(id__in = set(a_all)-set(a_ids))
            else:
                # limit us do asks who did match
                query = query.filter(id__in = a_ids)

            # now we're ready to apply the contact infomation constraints
            
            if form.cleaned_data['has_email']:
                query = query.exclude(email__exact = '')

            if form.cleaned_data['has_address']:
                query = query.exclude(street__exact = '',
                                      city__exact = '',
                                      country__exact = '')


            # maybe we want a CSV file

            if "download" in request.POST:
                response = HttpResponse(mimetype='text/csv')
                response['Content-Disposition'] = 'attachment;filename="gifts_search.csv"'
                writer = csv.writer(response)
                contacts = Contact.objects.all()
                writer.writerow(["name","street", "city", "state", 
                                 "postcode", "country", "email"])
                for contact in query:
                    writer.writerow([contact.name, 
                                     contact.street,
                                     contact.city,
                                     contact.state,
                                     contact.postcode,
                                     contact.country,
                                     contact.email])
                return response

            # or maybe we just want to see the results
            else:
                results = ContactTable(query)


    else:
        form = SearchForm() # An unbound form
    

    RequestConfig(request, paginate = None).configure(results)
    c = {'form': form,
         'results': results}
    c.update(csrf(request))

    return render(request, 'gifts/search.html', c)

@login_required
def import_csv(request):
    if request.method == 'POST': # If the form has been submitted...
        print(request.FILES)
        form = UploadCSVForm(request.POST, request.FILES) # A form bound to the POST/File data
        if form.is_valid(): # All validation rules pass

            new_contacts = ContactTable([])
            new_donations = DonationTable([])

    else:
        form = UploadCSVForm() # An unbound form

        new_contacts = ContactTable([])
        new_donations = DonationTable([])

    c = {'form': form,
         'new_donations': new_donations,
         'new_contacts': new_contacts}
    c.update(csrf(request))

    return render(request, 'gifts/import.html', c)
