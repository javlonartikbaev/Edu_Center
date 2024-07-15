from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.db.models import Q

from .models import *


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['first_name', 'last_name', 'phone_number', 'img_teacher', 'course', 'user']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'img_teacher': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        main_office_id = kwargs.pop('main_office_id', None)
        branch_office_id = kwargs.pop('branch_office_id', None)
        super(TeacherForm, self).__init__(*args, **kwargs)

        if main_office_id:
            self.fields['user'].queryset = CustomUser.objects.filter(Q(main_office_id=main_office_id)
                                                                     | Q(
                branch_office_id__main_office_id=main_office_id))
            self.fields['course'].queryset = Course.objects.filter(Q(main_office_id_id=main_office_id))
        elif branch_office_id:
            self.fields['user'].queryset = CustomUser.objects.filter(Q(branch_office_id=branch_office_id)
                                                                     | Q(main_office_id=branch_office_id))
            self.fields['course'].queryset = Course.objects.filter(Q(branch=branch_office_id)
                                                                   )
        else:
            self.fields['user'].queryset = CustomUser.objects.none()
            self.fields['course'].queryset = Course.objects.none()


class TeacherUpdateForm(forms.ModelForm):
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
        exclude = ['paid_check', 'joined_date', 'branch', 'main_office_id']
        widgets = {
            'first_name_s': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name_s': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number_s': forms.TextInput(attrs={'class': 'form-control'}),
            'parents_phone_number': forms.TextInput(attrs={'class': 'form-control'}),

        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['method_pay', 'date_pay', ]
        widgets = {
            'date_pay': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            # 'course_id': forms.Select(attrs={'class': 'form-control', }),

            'method_pay': forms.Select(attrs={'class': 'form-control'}),
        }


class AudienceForm(forms.ModelForm):
    class Meta:
        model = Audience
        fields = ['number_audience', 'capacity', ]


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name_group', 'start_date', 'end_date', 'start_time', 'end_time', 'lesson_days', 'teacher_id',
                  'audience_id', 'status_group', 'course_id']
        widgets = {
            'name_group': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'lesson_days': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'teacher_id': forms.Select(attrs={'class': 'form-control'}),
            'audience_id': forms.Select(attrs={'class': 'form-control'}),
            'status_group': forms.Select(attrs={'class': 'form-control'}),
            'course_id': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        main_office_id = kwargs.pop('main_office_id', None)
        branch_office_id = kwargs.pop('branch_office_id', None)
        super(GroupForm, self).__init__(*args, **kwargs)

        if main_office_id:
            self.fields['course_id'].queryset = Course.objects.filter(main_office_id=main_office_id)
            self.fields['teacher_id'].queryset = Teacher.objects.filter(main_office_id=main_office_id)
            self.fields['audience_id'].queryset = Audience.objects.filter(main_office_id=main_office_id)
        elif branch_office_id:
            self.fields['course_id'].queryset = Course.objects.filter(branch=branch_office_id)
            self.fields['teacher_id'].queryset = Teacher.objects.filter(branch=branch_office_id)
            self.fields['audience_id'].queryset = Audience.objects.filter(branch=branch_office_id)
        else:
            self.fields['course_id'].queryset = Course.objects.none()
            self.fields['teacher_id'].queryset = Teacher.objects.none()
            self.fields['audience_id'].queryset = Audience.objects.none()


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


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "password", "password1", "role")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = "__all__"
