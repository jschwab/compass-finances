from gifts.models import Contact, Donation, Ask
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect


def combine_selected_contacts(modeladmin, request, queryset):
    selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
    ct = ContentType.objects.get_for_model(queryset.model)
    return HttpResponseRedirect("/gifts/combine/?ct=%s&ids=%s" % (ct.pk, ",".join(selected)))

class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state']
    ordering = ['name']
    actions = [combine_selected_contacts]


class DonationAdmin(admin.ModelAdmin):
    list_display = ['date', 'amount', 'contact']
    ordering = ['date']


class AskAdmin(admin.ModelAdmin):
    list_display = ['date', 'campaign']
    ordering = ['date']


admin.site.register(Contact, ContactAdmin)
admin.site.register(Donation, DonationAdmin)
admin.site.register(Ask, AskAdmin)
