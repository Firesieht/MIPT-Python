from django.contrib import admin
from .models import ExhibitAuthorMapping, ExhibitProxy, OrganizationProxy, ExhibitionProxy, OrderToCreateExhibition, OrderExhibitionFromAuthors, OrderExhibitionToExhibit, OrderToReturn


class ExhibitAuthorMappingInline(admin.TabularInline):
    model = ExhibitAuthorMapping
    extra = 0
    readonly_fields = ['owner', 'order_to_create', 'order_to_get', 'order_to_provide', 'order_to_return']


@admin.register(OrganizationProxy)
class OrganizationAdmin(admin.ModelAdmin):
    pass

@admin.register(ExhibitionProxy)
class ExhibitionAdmin(admin.ModelAdmin):
    pass

@admin.register(OrderToCreateExhibition)
class OrderToCreateExhibitionAdmin(admin.ModelAdmin):
    inlines = [ExhibitAuthorMappingInline]

@admin.register(OrderExhibitionFromAuthors)
class OrderExhibitionFromAuthorsAdmin(admin.ModelAdmin):
    inlines = [ExhibitAuthorMappingInline]

@admin.register(OrderExhibitionToExhibit)
class OrderExhibitionToExhibitAdmin(admin.ModelAdmin):
    inlines = [ExhibitAuthorMappingInline]

@admin.register(OrderToReturn)
class OrderToReturnAdmin(admin.ModelAdmin):
    inlines = [ExhibitAuthorMappingInline]


admin.site.register(ExhibitProxy)
