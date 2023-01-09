from django.contrib import admin
from .models import GradeSheet

# Register your models here.
@admin.register(GradeSheet)
class GradeSheetAdmin(admin.ModelAdmin):
    list_display = ("reg_no", "name", "session", "department", "institute")