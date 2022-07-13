from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

# Register your models here.

from .models import Playground,Problem,TextCase,Challenge

admin.site.register(Playground)
admin.site.register(TextCase)
admin.site.register(Challenge)


class ModifiedProblem(SummernoteModelAdmin):
    summernote_fields = ('statement',)

admin.site.register(Problem, ModifiedProblem)