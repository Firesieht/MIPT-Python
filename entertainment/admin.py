from django.contrib import admin
from .models import ProstranstvoProxy, EventProxy, MoneyEventProxy, EventTypeProxy, LocationProxy
from session1.models import Location, EventMoneyRelation


class LocationInline(admin.TabularInline):
    model = ProstranstvoProxy.location_set.through
    extra = 0


class MoneyEventRelationInline(admin.TabularInline):
    model = EventMoneyRelation
    extra = 0


@admin.register(ProstranstvoProxy)
class AdminProstranstvo(admin.ModelAdmin):
    inlines = [LocationInline]
    pass


@admin.register(EventProxy)
class EventProxyAdmin(admin.ModelAdmin):
    pass

admin.site.register([EventTypeProxy, LocationProxy])

@admin.register(MoneyEventProxy)
class MoneyEventProxyAdmin(admin.ModelAdmin):
    inlines = [MoneyEventRelationInline]