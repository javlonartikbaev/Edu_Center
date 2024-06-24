from django import forms

from .models import *


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['first_name', 'last_name', 'phone_number', 'img_teacher', 'course', 'branch', 'user']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'img_teacher': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
        }


class SearchForm(forms.Form):
    search_input = forms.CharField(
        max_length=100,
        label=False,
        required=False,
        widget=forms.TextInput(attrs={'class': 'search-int form-control'}))


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name_course', 'price_course', 'duration', 'img_course', 'branch']
        widgets = {
            'name_course': forms.TextInput(attrs={'class': 'form-control'}),
            'price_course': forms.TextInput(attrs={'class': 'form-control'}),
            'duration': forms.TextInput(attrs={'class': 'form-control'}),
            'img_course': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),

        }


class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['name_status', ]
        widgets = {
            'name_status': forms.TextInput(attrs={'class': 'form-control'}),

        }


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ['paid_check', 'joined_date']
        widgets = {
            'first_name_s': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name_s': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number_s': forms.TextInput(attrs={'class': 'form-control'}),
            'parents_phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.Select(attrs={'class': 'form-control'}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['method_pay', 'date_pay', 'course_id', 'branch']
        widgets = {
            'date_pay': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'course_id': forms.Select(attrs={'class': 'form-control', }),
            'branch': forms.Select(attrs={'class': 'form-control'}),
            'method_pay': forms.Select(attrs={'class': 'form-control'}),
        }


class AudienceForm(forms.ModelForm):
    class Meta:
        model = Audience
        fields = ['number_audience', 'capacity', 'branch']


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name_group', 'start_date', 'end_date', 'teacher_id', 'audience_id', 'status_group',
                  'branch', 'course_id']
        widgets = {
            'name_group': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'teacher_id': forms.Select(attrs={'class': 'form-control'}),
            'audience_id': forms.Select(attrs={'class': 'form-control'}),
            'status_group': forms.Select(attrs={'class': 'form-control'}),
            'branch': forms.Select(attrs={'class': 'form-control'}),
            'course_id': forms.Select(attrs={'class': 'form-control'}),
        }


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['date_attendance', 'attendance_status']



class CommentForm(forms.Form):
    comment = forms.CharField(
        label='Комментарий',
        widget=forms.Textarea(attrs={'rows': 4, 'class': "form-control", 'placeholder': 'Причина удаления ...'}),
        required=False
    )


