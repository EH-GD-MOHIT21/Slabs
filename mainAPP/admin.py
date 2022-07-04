from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

# Register your models here.

from .models import Playground,Problem,TextCase

admin.site.register(Playground)
admin.site.register(TextCase)

class ModifiedProblem(SummernoteModelAdmin):
    summernote_fields = ('statement',)

admin.site.register(Problem, ModifiedProblem)