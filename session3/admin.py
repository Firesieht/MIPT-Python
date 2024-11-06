from django.contrib import admin
from .models import Sale, Ticket, TicketAvailable, TicketRow, Report, ReportRow, BareSell


class ReportRowInline(admin.TabularInline):
    model = ReportRow
    extra = 0
    readonly_fields = ['event', 'amount', 'cost', 'report', 'description']


class BareSellInline(admin.TabularInline):
    model = BareSell
    extra = 0


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    inlines = [ReportRowInline]


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0
    readonly_fields = ['cost']


class TicketRowInline(admin.TabularInline):
    model = TicketRow
    extra = 0
    readonly_fields = ['row_number', 'available_numbers', 'location', 'sale']


class TicketAvailableInline(admin.TabularInline):
    model = TicketAvailable
    extra = 0
    


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    inlines = [TicketInline, TicketRowInline, BareSellInline]
