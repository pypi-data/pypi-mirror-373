from django.db import models

from ..valar.models.core import VModel, VTree


class Case(VModel):
    a1 = models.FloatField(default=0, verbose_name='余额')
    a2 = models.FloatField(default=0, verbose_name='已用信用额度')
    a3 = models.FloatField(default=0, verbose_name='年还款额')
    a4 = models.FloatField(default=0, verbose_name='年收入/年还款')
    a5 = models.FloatField(default=0, verbose_name='负债')
    a6 = models.FloatField(default=0, verbose_name='利率*期数')
    a7 = models.FloatField(default=0, verbose_name='分期付款/年收入')
    a8 = models.FloatField(default=0, verbose_name='贷款人均负债')
    a9 = models.FloatField(default=0, verbose_name='匿名特征加总')
    a10 = models.FloatField(default=0, verbose_name='有效不良记录数')


class Forcast(VModel):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=100, verbose_name='类别')
    test = models.FloatField(default=0, verbose_name='测试集')
    train = models.FloatField(default=0, verbose_name='训练集')
    varify = models.FloatField(default=0, verbose_name='验证集')
    value = models.FloatField(default=0, verbose_name='预测结果')


class Vala(VModel):
    text_field = models.TextField(null=True, verbose_name='text')
    boolean_field = models.BooleanField(null=True, verbose_name='boolean')
    integer_field = models.IntegerField(null=True, verbose_name='integer')
    float_field = models.FloatField(null=True, verbose_name='float')
    date_field = models.DateField(null=True, verbose_name='date')
    datetime_field = models.DateTimeField(null=True, verbose_name='datetime')
    time_field = models.TimeField(null=True, verbose_name='time')
    json_field = models.JSONField(null=True, verbose_name='json')
    file = models.FileField(null=True, verbose_name='File')


class M2O(VModel):
    vala = models.ForeignKey(to=Vala, null=True, on_delete=models.CASCADE, verbose_name='vala')
    name = models.CharField(max_length=100, null=True, verbose_name='name')


class O2O(VModel):
    vala = models.OneToOneField(to=Vala, null=True, on_delete=models.CASCADE, verbose_name='vala')
    name = models.CharField(max_length=100, null=True, verbose_name='name')


class M2M(VTree):
    valas = models.ManyToManyField(to=Vala, verbose_name='valas')
    name = models.CharField(max_length=100, null=True, verbose_name='name')


class Tree(VTree):
    text = models.TextField(null=True, verbose_name='text')

    class Meta:
        verbose_name = '树形测试'
