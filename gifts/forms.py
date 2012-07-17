from django import forms
from django.forms.extras.widgets import SelectDateWidget
from gifts.models import Ask
import datetime

class SearchForm(forms.Form):
    """Simple form to search contacts based on donations/asks"""

    # what about people who don't have these records
    show_non_donors = forms.BooleanField(required = False)
    show_never_asked = forms.BooleanField(required = False)

    # range of donation amounts
    amount_min = forms.DecimalField(max_digits = 12, decimal_places = 2, required = False)
    amount_max = forms.DecimalField(max_digits = 12, decimal_places = 2, required = False)

    # if you want to set the date field to have a dropdown with a 
    # range of donation dates: allow 2007 - current year
    # set the forms.DateField(widget = widget), where
    # year_range = range(2007, datetime.date.today().year + 1)
    # widget = SelectDateWidget(years = year_range)

    donate_date_min = forms.DateField(required = False)
    donate_date_max = forms.DateField(required = False)

    # range of ask dates
    ask_date_min = forms.DateField(required = False)
    ask_date_max = forms.DateField(required = False)

    # require contact information
    has_email = forms.BooleanField(required = False)
    has_address = forms.BooleanField(required = False)


class UploadCSVForm(forms.Form):
    csvfile  = forms.FileField()

class CombineContactForm(forms.Form):

    def __init__(self, *args, **kwargs):
        new_fields  = kwargs.pop('new_fields')
        new_choices = kwargs.pop('new_choices')
        super(CombineContactForm, self).__init__(*args, **kwargs)
        
        for k,v in zip(new_fields, new_choices):
            if k != "id":
                self.fields[k] = forms.ChoiceField(choices = v)
            else:
                self.fields[k] = forms.MultipleChoiceField(widget = forms.MultipleHiddenInput(), 
                                                           initial = zip(*v)[0])

class AskForm(forms.ModelForm):
    class Meta:
        model = Ask
        exclude = ("contacts")
