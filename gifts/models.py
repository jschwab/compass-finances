from django.db import models

RELATIONSHIP_CHOICES = (
    ('FRIEND', 'Friend'),
    ('FAMLIY', 'Family'),
    ('ALUMNUS', 'Alumnus/Alumna'),
    ('UNDERGRAD', 'Undergrad'),
    ('GRADSTUDENT', 'Grad Student'),
)


class Contact(models.Model):

    # essential info
    name = models.CharField(max_length = 255)

    # contact info
    street = models.CharField(max_length = 255, blank = True)
    city = models.CharField(max_length = 127, blank = True)
    state = models.CharField(max_length = 127, blank = True)
    postcode = models.CharField(max_length = 63, blank = True)
    country = models.CharField(max_length = 63, blank = True)
    email = models.EmailField(max_length = 254, blank = True)

    # interesting info
    relationship = models.CharField(max_length = 15, blank = True,
                                    choices = RELATIONSHIP_CHOICES)
    point_person = models.CharField(max_length = 127, blank = True)
    comment = models.CharField(max_length = 2047, blank = True)

    def __unicode__(self):
        return self.name

class Donation(models.Model):

    # essential info
    contact = models.ForeignKey('Contact')
    date = models.DateField()
    amount = models.DecimalField(max_digits = 12, decimal_places = 2)

    # matching information
    matching_funds = models.BooleanField(default = False)
    matching_source = models.CharField(max_length = 255, blank = True)

    # donor-provided info
    publish = models.BooleanField(default = False)    
    comments = models.CharField(max_length = 2047, blank = True)
    referrer = models.CharField(max_length = 255, blank = True)

    # administrative info
    confirmation_number = models.IntegerField(blank=True,null=True)
    fund_number = models.CharField(max_length = 31, null = True, blank = True)

    def __unicode__(self):
        return "${0:} - {1:}".format(self.amount, self.date)

class Ask(models.Model):

    contact = models.ForeignKey('Contact')
    date = models.DateField()
    campaign = models.CharField(max_length = 255, blank = True)
    notes = models.CharField(max_length = 2047, blank = True)
    
    def __unicode__(self):
        return self.campaign
