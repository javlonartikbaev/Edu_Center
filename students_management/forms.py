from django import forms

from .models import *


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['first_name', 'last_name', 'phone_number', 'img_teacher', 'course']
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
        fields = ['name_course', 'price_course', 'duration', 'img_course', ]
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
        fields = '__all__'


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['method_pay','date_pay', 'price', 'student_id', 'branch', 'course_id']
        widgets = {
            'date_pay' : forms.DateInput(attrs={'type': 'date'}),
        }
class AudienceForm(forms.ModelForm):
    class Meta:
        model = Audience
        fields = ['number_audience', 'capacity']


class GroupForm(forms.ModelForm):
    students_id = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Студенты"
    )

    class Meta:
        model = Group
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['date_attendance', 'attendance_status']
