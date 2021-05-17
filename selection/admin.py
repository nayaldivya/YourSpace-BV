from django.contrib import admin
from .models import *


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'student_name',
        'father_name',
        'smart_card_id',
        'course',
        'year_of_study',
        'dob',
        'room',
        'room_allotted']
    actions = ["delete_selected"]

    def delete_selected(self, request, queryset):
        for element in queryset:
            element.delete()

    delete_selected.short_description = "Delete selected elements"


# class ElementAdmin(admin.ModelAdmin):
#     class Meta:
#         actions = ["delete_selected"]
#
#         def delete_selected(self, request, queryset):
#             for element in queryset:
#                 element.delete()
#
#         delete_selected.short_description = "Delete selected elements"


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['no', 'name', 'room_type', 'vacant', 'hostel']
    actions = ["delete_selected"]

    def delete_selected(self, request, queryset):
        for element in queryset:
            element.delete()

    delete_selected.short_description = "Delete selected elements"



@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_year_of_study']

    def get_year_of_study(self, obj):
        return "\n".join([p.code for p in obj.year_of_study.all()])


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'room_type']

@admin.register(Year_of_study)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code']


@admin.register(User)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['is_warden','username']


@admin.register(Warden)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'username']
    actions = ["delete_selected"]

    def username(self, obj):
        return obj.user.username

    def delete_selected(self, request, queryset):
        for element in queryset:
            element.delete()

    delete_selected.short_description = "Delete selected elements"
