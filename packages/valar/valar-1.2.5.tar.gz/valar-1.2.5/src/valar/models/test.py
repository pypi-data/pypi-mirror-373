from django.db import models
from .core import VModel, VTree


class Valar(VModel):
    text_field = models.TextField(null=True, verbose_name='Text Field')
    boolean_field = models.BooleanField(null=True, verbose_name='Boolean Field')
    integer_field = models.IntegerField(null=True, verbose_name='Integer Field')
    float_field = models.FloatField(null=True, verbose_name='Float Field')
    date_field = models.DateField(null=True, verbose_name='Date Field')
    datetime_field = models.DateTimeField(null=True, verbose_name='Datetime Field')
    time_field = models.TimeField(null=True, verbose_name='Time Field')
    json_field = models.JSONField(null=True, verbose_name='Json Field')
    file = models.FileField(null=True, verbose_name='File Field')


class Vmo(VModel):
    valar = models.ForeignKey(to=Valar, null=True, on_delete=models.CASCADE, verbose_name='Valar')
    name = models.CharField(max_length=100, null=True, verbose_name='Name')


class Voo(VModel):
    valar = models.OneToOneField(to=Valar, null=True, on_delete=models.CASCADE, verbose_name='Valar')
    name = models.CharField(max_length=100, null=True, verbose_name='Name')


class Vmm(VTree):
    valars = models.ManyToManyField(to=Valar, verbose_name='valars')
    name = models.CharField(max_length=100, null=True, verbose_name='name')
