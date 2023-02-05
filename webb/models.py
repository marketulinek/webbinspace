from django.db import models
from django.urls import reverse
from django.utils import timezone
from .utils import calculate_time_progress


class Report(models.Model):
    file_name = models.CharField(max_length=30, default='')
    package_number = models.CharField(max_length=10, unique=True)
    date_code = models.SmallIntegerField()
    cycle = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name

    def get_absolute_url(self):
        return reverse('report_detail', args=[self.package_number])

    def get_path_to_file(self):
        return f'source_data/cycle_{self.cycle}/{self.file_name}.txt'


class Category(models.Model):
    name = models.CharField(max_length=30, unique=True)

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
    visit_id = models.CharField(max_length=10, null=True, unique=True)
    pcs_mode = models.CharField(max_length=10, default='')
    visit_type = models.CharField(max_length=30, default='')
    scheduled_start_time = models.DateTimeField(null=True)
    duration = models.DurationField(null=True)
    science_instrument_and_mode = models.CharField(max_length=50, default='')
    instrument = models.CharField(
        choices=INSTRUMENT_CHOICES,
        max_length=1,
        null=True
    )
    target_name = models.CharField(max_length=30, default='')
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='visits',
        null=True
    )
    keywords = models.CharField(max_length=100, default='')
    valid = models.BooleanField(default=True)

    def __str__(self):
        return self.visit_id

    def invalidate(self):
        self.valid = False

    @property
    def is_underway(self):
        """Returns info if the visit (target) is currently being observed or not."""
        return self.scheduled_start_time <= timezone.now() \
            and calculate_time_progress(self.scheduled_start_time, self.duration) < 100
