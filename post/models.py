from django.db import models


class Truck(models.Model):
    plate_number = models.CharField(max_length=15, unique=True, verbose_name='Plate number')

    def __str__(self):
        return self.plate_number

    def __repr__(self):
        return self.plate_number


class Letter(models.Model):
    ON_THE_WAY = 'OW'
    HAS_TO_BE_DELIVERED_TODAY = 'DT'
    RECIPIENT_IS_NOT_AVAILABLE = 'NA'
    SUCCESSFULLY_DELIVERED = 'SD'
    DO_NOT_TRACK = 'NT'
    STATUSES = [
        (ON_THE_WAY, 'В пути'),
        (HAS_TO_BE_DELIVERED_TODAY, 'Передан на доставку'),
        (RECIPIENT_IS_NOT_AVAILABLE, 'Авизо'),
        (SUCCESSFULLY_DELIVERED, 'Доставлено'),
        (DO_NOT_TRACK, 'Не бьётся'),
    ]
    track_number = models.CharField(
        max_length=30, default='b/n', verbose_name='Track number'
    )
    truck = models.ForeignKey(
        Truck, on_delete=models.SET_NULL, null=True, related_name='letters', verbose_name='Truck number'
    )
    sending_date = models.DateField(verbose_name='Date of sending')
    status_date = models.DateField(default=sending_date, verbose_name='Date of last status changing')
    comment = models.CharField(max_length=50, null=True, blank=True, verbose_name='Comment')
    status = models.CharField(max_length=30, choices=STATUSES, default=ON_THE_WAY, verbose_name='Status')

    def save(self, *args, **kwargs):
        if not self.track_number:
            self.track_number = 'b/n'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.track_number

    def __repr__(self):
        return self.track_number
