from django.db import models
from django.urls import reverse


class Report(models.Model):
    package_number = models.CharField(max_length=10)
    date_code = models.SmallIntegerField()
    cycle = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%i_report_%i' % (self.package_number, self.date_code)

    def get_absolute_url(self):
        return reverse('report_detail', args=[self.date_code])

class Category(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', args=[self.name])

class Visit(models.Model):
    INSTRUMENT_CHOICES = (
        ('1', 'NIRCam'),
        ('2', 'NIRSpec'),
        ('3', 'MIRI'),
        ('4', 'NIRISS')
    )

    report = models.ForeignKey(
        Report,
        on_delete=models.PROTECT,
        related_name='visits'
    )
    visit_id = models.CharField(max_length=10, default='')
    pcs_mode = models.CharField(max_length=10, default='')
    visit_type = models.CharField(max_length=30, default='')
    scheduled_start_time = models.DateTimeField(null=True)
    duration = models.DateTimeField(null=True)
    science_instrument_and_mode = models.CharField(max_length=50, default='')
    instrument = models.CharField(
        choices=INSTRUMENT_CHOICES,
        max_length=1,
        default=''
    )
    mode = models.CharField(max_length=50, default='')
    target_name = models.CharField(max_length=30, default='')
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='visits',
        null=True
    )
    keywords = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.visit_id