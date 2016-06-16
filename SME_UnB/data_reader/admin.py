from django.contrib import admin
from .models import Transductor, TransductorManager, Measurements


class TransductorInLine(admin.StackedInline):
    model = Transductor
    extra = 1

class TransductorManagerAdmin(admin.ModelAdmin):
    fieldset = [
        (None, {'fields': ['description']}),
    ]
    inlines = [TransductorInLine]

admin.site.register(TransductorManager, TransductorManagerAdmin)
