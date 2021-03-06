# -*- coding: utf-8 -*-#

import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required as perm_req_std
from django.db.models import F
from django.shortcuts import render
from django.utils import translation
from django_tables2 import RequestConfig

from guardian.decorators import permission_required

from crm.models import SalesPerson, Deal, Todo, Customer, Product
from crm.tables import SalesPersonTable, DealsTable, ToDosTable, CustomersTable, ProductTable
from crm.mixin import SomeUtilsMixin, add_lang

__author__ = 'AMA'


@login_required
@permission_required('crm.read_salesperson', accept_global_perms=True)
@add_lang
def tableSalesPerson(request):
    queryset = SalesPerson.objects.annotate(email=F('user__email'))
    table = SalesPersonTable(queryset)
    RequestConfig(request).configure(table)
    filter = 'NONFILTER'
    return render(request, 'crm/common_table_list.html', {'table': table, 'filter': filter})


@login_required
@perm_req_std('crm.read_product')
@add_lang
def tableProducts(request):
    queryset = Product.objects.all()
    table = ProductTable(queryset)
    RequestConfig(request).configure(table)
    filter = 'NONFILTER'
    return render(request, 'crm/common_table_list.html', {'table': table, 'filter': filter})


@login_required
@permission_required('crm.read_deal', accept_global_perms=True)
@add_lang
def tableFilterDeals(request, classFilter=None, duration=None):
    '''
    Функция комбинированного показа фильтров и результата фильтрования чрезе таблицы
    Может не содержать фитьтров вообще, тогда classFilter=None . Duration определяет предфильтрацию перед фильтрами.
    '''
    now_date = datetime.date.today()  # Текущая дата (без времени)

    queryset = Deal.objects.all()
    # add some fields from different models
    queryset = queryset.annotate(deal_data=F('dealstatus__deal_data'))
    queryset = queryset.annotate(deal_time=F('dealstatus__deal_time'))
    queryset = queryset.annotate(deal_status=F('dealstatus__status'))

    # Delete deals duplicates
    for query in queryset:
        queryset_deal = queryset.filter(pk=query.pk).order_by('-deal_data', '-deal_time')
        if len(queryset_deal) > 1:
            for query in queryset_deal[1:]:
                queryset = queryset.exclude(pk=query.pk, deal_data=query.deal_data, deal_time=query.deal_time)

    # Add some filters
    if classFilter:
        if duration == 'day':
            queryset = queryset.filter(deal_data__year=now_date.year)
            queryset = queryset.filter(deal_data__month=now_date.month)
            queryset = queryset.filter(deal_data__day=now_date.day)
        elif duration == 'month':
            queryset = queryset.filter(deal_data__year=now_date.year)
            queryset = queryset.filter(deal_data__month=now_date.month)
        elif duration == 'year':
            queryset = queryset.filter(deal_data__year=now_date.year)

        filter = classFilter(request.GET, queryset=queryset)
        queryset = filter.qs
    else:
        filter = 'NONFILTER'

    queryset = SomeUtilsMixin.doHumanReadble_STATUS_CHOICES(0, queryset)
    table = DealsTable(queryset)
    RequestConfig(request).configure(table)

    return render(request, 'crm/common_table_list.html', {'table': table, 'filter': filter})


@login_required
@perm_req_std('crm.read_todo')
@add_lang
def tableFilterToDos(request, classFilter=None, duration=None):
    '''
    Функция комбинированного показа фильтров и результата фильтрования чрезе таблицы
    Может не содержать фитьтров вообще, тогда classFilter=None . Duration определяет предфильтрацию перед фильтрами.
    '''
    now_date = datetime.date.today()  # Текущая дата (без времени)
    queryset = Todo.objects.all()

    # Add some filters
    if classFilter:
        if duration == 'day':
            queryset = queryset.filter(todo_data__year=now_date.year)
            queryset = queryset.filter(todo_data__month=now_date.month)
            queryset = queryset.filter(todo_data__day=now_date.day)
        elif duration == 'month':
            queryset = queryset.filter(todo_data__year=now_date.year)
            queryset = queryset.filter(todo_data__month=now_date.month)
        elif duration == 'year':
            queryset = queryset.filter(todo_data__year=now_date.year)

        filter = classFilter(request.GET, queryset=queryset)
        queryset = filter.qs
    else:
        filter = 'NONFILTER'

    table = ToDosTable(queryset)
    RequestConfig(request).configure(table)

    return render(request, 'crm/common_table_list.html', {'table': table, 'filter': filter})


@perm_req_std('crm.read_customer')
@add_lang
def tableFilterCustomer(request, classFilter=None, duration=None):
    '''
    Функция комбинированного показа фильтров и результата фильтрования чрезе таблицы
    Может не содержать фитьтров вообще, тогда classFilter=None . Duration определяет предфильтрацию перед фильтрами.
    '''

    queryset = Customer.objects.all()
    filter = 'NONFILTER'

    table = CustomersTable(queryset)
    RequestConfig(request).configure(table)

    return render(request, 'crm/common_table_list.html', {'table': table, 'filter': filter})
