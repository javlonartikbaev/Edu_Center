from django.contrib import admin

from students_management.models import *

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# Create your models here.
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'id','first_name_s', 'last_name_s', 'phone_number_s', 'paid_check', 'parents_phone_number', 'joined_date')


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('method_pay', 'date_pay', 'price', 'student_id')


class CourseAdmin(admin.ModelAdmin):
    list_display = ('name_course', 'price_course', 'duration', 'slug_course')


class AudienceAdmin(admin.ModelAdmin):
    list_display = ('number_audience', 'capacity', 'slug_audience')


class StatusAdmin(admin.ModelAdmin):
    list_display = ('name_status', 'slug_status')


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone_number', 'img_teacher', 'course')


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name_group', 'start_date', 'end_date', 'teacher_id', 'audience_id',
                    'status_group')
    filter_horizontal = ('students_id',)


class AttendanceStatusAdmin(admin.ModelAdmin):
    list_display = ('name_attendance_status',)


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('students_id', 'groups_id', 'date_attendance', 'attendance_status')


class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone_number', 'admin')


class ArchivedStudentAdmin(admin.ModelAdmin):
    list_display = (
        'first_name_s', 'last_name_s', 'phone_number_s', 'paid_check', 'parents_phone_number', 'joined_date',
        'archived_date', 'comments', 'branch')
    search_fields = ('first_name_s', 'last_name_s', 'phone_number_s', 'parents_phone_number')
    list_filter = ('branch', 'comments', 'archived_date')
    ordering = ('-archived_date',)


class ArchivedPaymentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'method_pay', 'date_pay', 'price', 'archived_date', 'comments', 'branch')
    search_fields = ('student', 'method_pay', 'price')
    list_filter = ('branch', 'method_pay', 'archived_date')
    ordering = ('-archived_date',)


class ArchivedGroupAdmin(admin.ModelAdmin):
    list_display = (
        'name_group', 'start_date', 'end_date', 'teacher_id', 'audience_id', 'status_group', 'branch', 'course_id',
        'archived_date')
    search_fields = ('name_group', 'teacher_id__first_name', 'teacher_id__last_name')
    list_filter = ('branch', 'status_group', 'archived_date')
    ordering = ('-archived_date',)



admin.site.register(ArchivedStudent, ArchivedStudentAdmin)
admin.site.register(ArchivedPayment, ArchivedPaymentAdmin)
admin.site.register(ArchivedGroup, ArchivedGroupAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Audience, AudienceAdmin)
admin.site.register(Status, StatusAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Attendance_Status, AttendanceStatusAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Branch, BranchAdmin)
