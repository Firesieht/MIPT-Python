from django.contrib import admin
from .models import StudioProxy, TeacherProxy, Day, StudioWorkReport, \
TimeTableTeacher, Visitors, ReportToVisitStudio, ReportCenterState, \
ReportStudentMapping, TableCellTeacher, CostAbonimentsCreateion, AbonimentSale, \
AbonimentSaleReport, AbonimentReportMapping
from session1.models import Studio

class AbonimentSellMappingInline(admin.TabularInline):
    model = AbonimentReportMapping
    extra = 0
    readonly_fields = ['studio', 'aboniments_info', 'total_sum', 'report']

class CostAbonimentsCreateionInline(admin.TabularInline):
    model = CostAbonimentsCreateion
    extra = 0

@admin.register(CostAbonimentsCreateion)
class CostAbonimentCreationAdmin(admin.ModelAdmin): 
    readonly_fields = ['month_type', 'year_type']

@admin.register(AbonimentSale)
class AbonimentSaleAdmin(admin.ModelAdmin): 
    readonly_fields = ['cost', 'report_studio', 'visitor']

@admin.register(AbonimentSaleReport)
class AbonimentSaleReportAdmin(admin.ModelAdmin): 
    inlines = [AbonimentSellMappingInline]
    readonly_fields = ['total_sum']

class StudioMappingInline(admin.TabularInline):
    model = ReportStudentMapping
    extra = 0
    readonly_fields = ['studio', 'visitors']


class ReportToVisitStudioInline(admin.TabularInline):
    model = ReportToVisitStudio
    extra = 0
    readonly_fields = ['date_created', 'working_report', 'visitor']


class TableCellInline(admin.TabularInline):
    model = TableCellTeacher
    extra = 0
    readonly_fields = ['days', 'timing', 'studio', 'timetable']


@admin.register(StudioWorkReport)
class StudioWorkReportAdmin(admin.ModelAdmin): 
    inlines = [ReportToVisitStudioInline, CostAbonimentsCreateionInline]

@admin.register(TimeTableTeacher)
class TimetableTeacherAdmin(admin.ModelAdmin): 
    inlines = [TableCellInline]

@admin.register(Visitors)
class VisitorsAdmin(admin.ModelAdmin): pass


@admin.register(ReportToVisitStudio)
class ReportToVisitStudioAdmin(admin.ModelAdmin): pass


@admin.register(ReportCenterState)
class ReportCenterState(admin.ModelAdmin):
    inlines = [StudioMappingInline]


@admin.register(StudioProxy)
class StudioAdmin(admin.ModelAdmin): 
    def get_queryset(self, request):
        return Studio.objects.all().exclude(name='Культурный центр')

admin.site.register([TeacherProxy, Day])
