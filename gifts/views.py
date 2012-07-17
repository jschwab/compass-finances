import csv
import datetime
import django_tables2 as tables
from django_tables2 import RequestConfig
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from gifts.models import Contact, Donation, Ask
from django_tables2.utils import A
from django.contrib.auth.decorators import login_required
from gifts.forms import SearchForm, UploadCSVForm, CombineContactForm, AskForm
from django.core.context_processors import csrf
from django.forms.models import model_to_dict
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
    campaign = tables.LinkColumn("ask_record", args=[A("pk")])

    class Meta:
        model = Ask
        sequence = ('campaign',)
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
    ask_table = AskTable(Ask.objects.filter(contacts=contact_id))
    RequestConfig(request, paginate = False).configure(contact_table)
    RequestConfig(request, paginate = False).configure(donation_table)
    RequestConfig(request, paginate = False).configure(ask_table)
    return render(request, 'gifts/contact_detail.html', 
                  {'contact': contact_table,
                   'donation': donation_table,
                   'ask': ask_table})

@login_required
def ask_record(request, ask_id):
    ask_table = AskTable(Ask.objects.filter(pk = ask_id))
    contact_table = SingleContactTable(Contact.objects.filter(ask__pk=ask_id))
    RequestConfig(request, paginate = False).configure(contact_table)
    RequestConfig(request, paginate = False).configure(ask_table)
    return render(request, 'gifts/ask_detail.html', 
                  {'contact': contact_table,
                   'ask': ask_table})
                   
@login_required
def asks(request):
    ask_table = AskTable(Ask.objects.all())
    RequestConfig(request, paginate = False).configure(ask_table)
    return render(request, 'gifts/asks.html', {'ask_table': ask_table})

@login_required
def search(request):
    # results start as an empty table of the correct type
    results = ContactTable([]) 
    if request.method == 'POST': # If the form has been submitted...
        form = SearchForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass

            query  = Contact.objects.all()

            if form.cleaned_data['has_email']:
                query = query.exclude(email__exact = '')

            if form.cleaned_data['has_address']:
                query = query.exclude(street__exact = '',
                                      city__exact = '',
                                      country__exact = '')

            # now figure out which donations match the critera

            if not form.cleaned_data['show_non_donors']:
                query = query.exclude(donation__isnull = True)

            # decide how to do the date range
            has_amt_min = form.cleaned_data['amount_min'] is not None
            has_amt_max = form.cleaned_data['amount_max'] is not None

            if has_amt_min and not has_amt_max:
                query = query.filter(donation__amount__gte = 
                                     form.cleaned_data['amount_min'])

            if has_amt_max and not has_amt_min:
                query = query.filter(donation__amount__lte = 
                                     form.cleaned_data['amount_max'])

            if has_amt_min and has_amt_max:
                query = query.filter(donation__amount__range = 
                                     (form.cleaned_data['amount_min'],
                                      form.cleaned_data['amount_max']))

            # do the donation date range

            if form.cleaned_data['donate_date_min'] is not None:
                query = query.filter(donation__date__gte = 
                                     form.cleaned_data['donate_date_min'])

            if form.cleaned_data['donate_date_max'] is not None:
                query = query.exclude(donation__date__gt = 
                                     form.cleaned_data['donate_date_max'])

            # figure out which asks match the critera

            if not form.cleaned_data['show_never_asked']:
                query = query.exclude(ask__isnull = True)

            if form.cleaned_data['ask_date_min'] is not None:
                query = query.filter(ask__date__gte = 
                                     form.cleaned_data['ask_date_min'])

            if form.cleaned_data['ask_date_max'] is not None:
                query = query.exclude(ask__date__gt = 
                                     form.cleaned_data['ask_date_max'])
            
            query = query.distinct()

            # maybe we want a CSV file

            if "download" in request.POST:
                response = HttpResponse(mimetype='text/csv')
                response['Content-Disposition'] = 'attachment;filename="gifts_search.csv"'
                writer = csv.writer(response)
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

            elif "newask" in request.POST and query:
                newask = Ask(date = datetime.date.today())
                newask.save()
                for contact in query:
                    newask.contacts.add(contact)
                newask.save()
                return HttpResponseRedirect("/gifts/newask/%s" % (newask.id))

            # or maybe we just want to see the results
            else:
                results = ContactTable(query)


    else:
        form = SearchForm() # An unbound form
    

    RequestConfig(request, paginate = False).configure(results)
    c = {'form': form,
         'results': results}
    c.update(csrf(request))

    return render(request, 'gifts/search.html', c)

@login_required
def newask(request, ask_id):

    a = Ask.objects.get(pk = ask_id)

    if request.method == 'POST':
        form = AskForm(request.POST, instance=a)
        form.save()
        return HttpResponseRedirect("/gifts/asks/")
    else:
        form = AskForm(instance=a)
        c = {'form': form}
        c.update(csrf(request))
        return render(request, 'gifts/newask.html', c)

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

@login_required
def combine(request):

    if request.method == "POST":

        if len(request.POST.getlist('id')) < 2:
            return HttpResponseRedirect("/gifts/contacts/")
        
        # first get the set of contacts that we're going to merge
        grouped_contacts = Contact.objects.filter(id__in = request.POST.getlist('id'))

        # fields and ids
        field_list = list(f.name for f in Contact._meta.fields)[1:]
        ids = list(grouped_contacts.values_list('id', flat = True))


        # make a new contact out of the selected values
        merged_contact_dict = {}
        for field in field_list:
            values = grouped_contacts.values_list(field, flat = True)
            merged_contact_dict[field] = values[ids.index(int(request.POST[field]))]
        
        merged_contact = Contact(**merged_contact_dict)
        merged_contact.save()
        id = merged_contact.id

        # reassign donations and asks to this new contact and then delete the old one

        for contact in grouped_contacts:
            contact.donation_set.all().update(contact = id)
            for ask in contact.ask_set.all():
                merged_contact.ask_set.add(ask)
            contact.delete()


        
        return HttpResponseRedirect("/gifts/contacts/%s/" % id)

    if request.method == "GET" and 'ids' in request.GET:
        
        # turn the GET into a query set
        ids = [int(x) for x in request.GET['ids'].split(",")]
        qs = Contact.objects.filter(id__in = ids)

        field_list = list(f.name for f in Contact._meta.fields)

        qsv = qs.values_list(*field_list)
        ids = qs.values_list('id', flat = True)

        new_choices = [zip(ids, x) for x in zip(*qsv)]

        # render a page with buttons

        form = CombineContactForm(new_fields = field_list, 
                                  new_choices = new_choices)

        c = {'table': ContactTable(qs), 'form' : form}

    else:
        c = {'table': ContactTable([]), 'form' : ()}
    

    c.update(csrf(request))
    return render(request, 'gifts/combine.html', c)



