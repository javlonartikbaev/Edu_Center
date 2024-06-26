from collections import defaultdict
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Max, Count
from django.db.models import Q
from django.db.models.functions import ExtractYear, TruncMonth
# Create your views here.
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect

from .forms import *


# Professor
@login_required
def get_professor(request):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')

    search = SearchForm(request.GET)
    if search.is_valid():
        search_professor_name = search.cleaned_data.get('search_input', '')
        if search_professor_name:
            found_professor = Teacher.objects.filter(Q(first_name__icontains=search_professor_name) |
                                                     Q(last_name__icontains=search_professor_name))
        else:
            found_professor = Teacher.objects.all()
        paginator = Paginator(found_professor, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        current_year = datetime.today().year
        data = {'search': search, 'professor': page_obj, 'current_year': current_year, 'user': request.user,
                }
    else:
        professor = Teacher.objects.all()
        paginator = Paginator(professor, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        current_year = datetime.today().year
        data = {'search': search, 'professor': page_obj, 'current_year': current_year, 'user': request.user}
    return render(request, 'professors/all-professors.html', data)


@login_required
def delete_professor(request, id_professor):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')

    professor = get_object_or_404(Teacher, id=id_professor)
    current_year = datetime.today().year
    if request.method == 'POST':
        professor.delete()
        return redirect('all_professors')
    data = {'professor': professor, 'current_year': current_year}
    return render(request, 'professors/delete-professor.html', data)


@login_required
def update_professor(request, id_professor):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    professor = get_object_or_404(Teacher, pk=id_professor)
    current_year = datetime.today().year
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=professor)
        if form.is_valid():
            form.save()
            return redirect('all_professors')
    else:
        form = TeacherForm(instance=professor)
    data = {"form": form, "current_year": current_year}
    return render(request, 'professors/edit-professor.html', data)


@login_required
def add_professor(request):
    if not request.user.is_superuser:
        branch = request.user.admin_branches.first()
        if not branch:
            messages.error(request, 'У вас нет прав доступа.')
            return redirect('main_page')
    professor_form = TeacherForm()
    if request.method == 'POST':
        professor_form = TeacherForm(request.POST, request.FILES)
        if professor_form.is_valid():
            professor = professor_form.save(commit=False)
            if not request.user.is_superuser:
                professor.branch = branch  # Назначаем филиал текущего пользователя
            professor.save()
            return redirect('all_professors')

    if request.user.is_superuser:
        template_name = 'professors/add-professor.html'
    else:
        template_name = 'teachers/teachers-profile.html'
    return render(request, template_name, {'professor_form': professor_form})


@login_required
def get_courses(request):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    search = SearchForm(request.GET)
    if search.is_valid():
        search_course_name = search.cleaned_data.get('search_input', '')
        if search_course_name:
            found_course = Course.objects.filter(name_course__icontains=search_course_name)
        else:
            found_course = Course.objects.all()
        paginator = Paginator(found_course, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        current_year = datetime.today().year
        data = {'search': search, 'courses': page_obj, 'current_year': current_year}
    else:
        course = Course.objects.all()
        paginator = Paginator(course, 10)

        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        current_year = datetime.today().year
        data = {'search': search, 'courses': page_obj, 'current_year': current_year}

    return render(request, 'courses/all-courses.html', data)


@login_required
def add_course(request):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    course_form = CourseForm()
    current_year = datetime.today().year
    if request.method == 'POST':
        course_form = CourseForm(request.POST, request.FILES)
        if course_form.is_valid():
            course = course_form.save(commit=False)
            course.save()
            return redirect('all_courses')
    else:
        course_form = CourseForm()
        data = {"course_form": course_form, 'current_year': current_year}
        return render(request, 'courses/add-course.html', data)


@login_required
def update_course(request, id_course):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    course = get_object_or_404(Course, pk=id_course)
    current_year = datetime.today().year
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('all_courses')
    else:
        form = CourseForm(instance=course)
    data = {"form": form, "current_year": current_year}
    return render(request, 'courses/edit-course.html', data)


@login_required
def delete_course(request, id_course):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    course = get_object_or_404(Course, pk=id_course)
    current_year = datetime.today().year
    if request.method == 'POST':
        course.delete()
        return redirect('all_courses')
    data = {"course": course, "current_year": current_year}
    return render(request, 'courses/delete-course.html', data)


@login_required
def all_status(request):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    status = Status.objects.all()
    current_year = datetime.today().year
    data = {'status': status, 'current_year': current_year}
    return render(request, 'status/all-status.html', data)


@login_required()
def add_status(request):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    status_form = StatusForm(request.POST)
    current_year = datetime.today().year
    if status_form.is_valid():
        status = status_form.save(commit=False)
        status.slug_status = status.name_status
        status.save()
        return redirect('all_status')
    status_form = StatusForm()
    data = {"status_form": status_form, 'current_year': current_year}
    return render(request, 'status/add-status.html', data)


@login_required()
def update_status(request, id_status):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    status = get_object_or_404(Status, pk=id_status)
    current_year = datetime.today().year
    if request.method == 'POST':
        form = StatusForm(request.POST, instance=status)
        if form.is_valid():
            status.slug_status = status.name_status
            form.save()
            return redirect('all_status')
    else:
        form = StatusForm(instance=status)
    data = {"form": form, "current_year": current_year}
    return render(request, 'status/update-status.html', data)


@login_required()
def delete_status(request, id_status):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    status = get_object_or_404(Status, pk=id_status)
    current_year = datetime.today().year
    if request.method == 'POST':
        status.delete()
        return redirect('all_status')
    data = {"status": status, "current_year": current_year}
    return render(request, 'status/delete-status.html', data)


@login_required()
def all_students(request):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    search = SearchForm(request.GET)
    if search.is_valid():
        search_student_name = search.cleaned_data.get('search_input', )
        if search_student_name:
            found_student = Student.objects.filter(Q(first_name_s__icontains=search_student_name) |
                                                   Q(last_name_s__icontains=search_student_name))
        else:
            found_student = Student.objects.all()
    else:
        found_student = Student.objects.all()

    filter_option = request.GET.get('filter')
    if filter_option == 'not_paid':
        found_student = found_student.filter(paid_check='Не оплатил')

    paginator = Paginator(found_student, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    current_year = datetime.today().year

    for student in page_obj:
        last_payment = Payment.objects.filter(student_id=student.id).aggregate(last_payment_date=Max('date_pay'))
        student.last_payment_date = last_payment['last_payment_date']

        if student.last_payment_date:
            next_month_date = student.last_payment_date + timedelta(days=30)
            if next_month_date <= datetime.today().date():
                student.paid_check = "Не оплатил"
            else:
                student.paid_check = "Оплатил"
        else:
            student.paid_check = "Не оплатил"
        student.save()

    data = {'search': search, 'student': page_obj, 'current_year': current_year}
    return render(request, 'students/all-students.html', data)


@login_required()
def add_students(request, group_id=None):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    current_year = datetime.today().year
    if request.method == "POST":
        student_form = StudentForm(request.POST)
        if student_form.is_valid():
            if group_id:
                group = Group.objects.get(id=group_id)

                student = student_form.save(commit=False)
                student.save()
                group.students_id.add(student)

                return redirect('all_groups')
            else:
                student = student_form.save(commit=False)
                student.save()
                return redirect('all_groups')
    else:
        student_form = StudentForm()

    groups = Group.objects.all()
    data = {
        "student_form": student_form,
        'current_year': current_year,
        'groups': groups,
        'selected_group_id': group_id
    }
    return render(request, 'groups/add_students_to_group.html', data)


@login_required()
def update_students(request, id_student):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    student = get_object_or_404(Student, pk=id_student)
    current_year = datetime.today().year
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('')
    else:
        form = StudentForm(instance=student)
    data = {"form": form, "current_year": current_year}
    return render(request, 'students/edit-student.html', data)


@login_required()
def delete_students(request, id_student):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    student = get_object_or_404(Student, pk=id_student)
    current_year = datetime.today().year
    if request.method == 'POST':
        student.delete()
        return redirect('all_students')
    data = {"student": student, "current_year": current_year}
    return render(request, 'students/delete-student.html', data)


@login_required()
def profile_students(request, id_student):
    student = get_object_or_404(Student, id=id_student)
    payments = Payment.objects.filter(student_id=student)

    selected_month = request.GET.get('month')

    if selected_month:
        selected_month = int(selected_month)
        attendance = Attendance.objects.filter(students_id=id_student, date_attendance__month=selected_month)
    else:
        attendance = Attendance.objects.filter(students_id=id_student)

    groups = Group.objects.filter(students_id=id_student)

    courses = Course.objects.filter(group__in=groups).distinct()

    current_year = datetime.today().year

    data = {
        'student': student,
        'payments': payments,
        'current_year': current_year,
        'attendance': attendance,
        'selected_month': selected_month,
        'courses': courses,
    }

    if request.user.is_superuser:
        template_name = 'students/student-profile.html'
    else:
        template_name = 'teachers-group/teachers-st-profile.html'

    return render(request, template_name, data)


@login_required()
def all_audience(request):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    audience = Audience.objects.all()
    current_year = datetime.today().year
    data = {'audience': audience, 'current_year': current_year}
    return render(request, 'audience/all-audience.html', data)


@login_required()
def add_audience(request):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    audience_form = AudienceForm(request.POST)
    audience = Audience.objects.all()
    current_year = datetime.today().year
    if audience_form.is_valid():
        audience = audience_form.save(commit=False)
        audience.slug_audience = audience.number_audience
        audience.save()
        return redirect('all_audience')
    audience_form = AudienceForm()
    data = {"audience_form": audience_form, 'current_year': current_year}
    return render(request, 'audience/add-audience.html', data)


@login_required()
def update_audience(request, id_audience):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    audience = get_object_or_404(Audience, pk=id_audience)
    current_year = datetime.today().year
    if request.method == 'POST':
        audience_form = AudienceForm(request.POST, instance=audience)
        audience = audience_form.save(commit=False)
        audience.slug_audience = audience.number_audience
        audience.save()
        return redirect('all_audience')
    else:
        audience_form = AudienceForm(instance=audience)
    data = {"audience_form": audience_form, 'current_year': current_year}
    return render(request, 'audience/edit-audience.html', data)


@login_required()
def delete_audience(request, id_audience):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    audience = get_object_or_404(Audience, pk=id_audience)
    current_year = datetime.today().year
    if request.method == 'POST':
        audience.delete()
        return redirect('all_audience')
    data = {'audience': audience, 'current_year': current_year}
    return render(request, 'audience/delete-audience.html', data)


@login_required()
def all_groups(request):
    current_year = datetime.today().year
    req_user = Teacher.objects.filter(
        user_id=request.user.id).first()

    if request.user.is_superuser:
        groups = Group.objects.all()
        data = {'groups': groups, 'current_year': current_year}
        return render(request, 'groups/all-groups.html', data)

    if req_user:
        professors = Teacher.objects.all()
        groups = Group.objects.filter(teacher_id=req_user.id)
        data = {'groups': groups, 'current_year': current_year, 'professors': professors}
        return render(request, 'teachers-group/teachers_group.html', data)

    data = {"current_year": current_year}
    return render(request, 'groups/all-groups.html', data)


@login_required()
def add_group(request):
    if request.method == 'POST':

        group_form = GroupForm(request.POST)
        if group_form.is_valid():
            group = group_form.save()
            return redirect('all_groups')
    else:
        group_form = GroupForm()

    current_year = datetime.today().year
    data = {"group_form": group_form, 'current_year': current_year, }
    return render(request, 'groups/add-groups.html', data)


@login_required()
def update_group(request, id_group):
    group = get_object_or_404(Group, pk=id_group)
    current_year = datetime.today().year

    if request.user.is_superuser:
        if request.method == 'POST':
            group_form = GroupForm(request.POST, instance=group)
            if group_form.is_valid():
                group_form.save()
                students_to_remove = request.POST.getlist('students_to_remove')
                if students_to_remove:
                    group.students_id.remove(*students_to_remove)
                return redirect('all_groups')
            else:
                messages.error(request, group_form.errors)
        else:
            group_form = GroupForm(instance=group)
    else:
        messages.error(request, 'У вас нет прав')
        return redirect('all_groups')

    data = {"group_form": group_form, 'current_year': current_year, 'messages': messages}
    return render(request, 'groups/edit-groups.html', data)


@login_required()
def delete_group(request, id_group):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    group = get_object_or_404(Group, pk=id_group)

    if request.method == 'POST':
        comment = request.POST.get('comment', '')
        status_instance = get_object_or_404(Status, id=2)

        archived_group = ArchivedGroup.objects.create(
            name_group=group.name_group,
            start_date=group.start_date,
            end_date=group.end_date,
            teacher_id=group.teacher_id,
            audience_id=group.audience_id,
            status_group=status_instance,
            branch=group.branch,
            course_id=group.course_id,
            comments=comment,
        )

        archived_group.students_id.set(group.students_id.all())
        group.students_id.clear()
        group.delete()

        return redirect('archived_students')

    comment_form = CommentForm()

    data = {"group": group, 'comment_form': comment_form, }
    return render(request, 'groups/delete-groups.html', data)


@login_required
def mark_attendance(request, group_id):
    group = get_object_or_404(Group, pk=group_id)

    if request.method == 'POST':
        date_attendance = request.POST.get('date_attendance')
        attendance_status = Attendance_Status.objects.get(name_attendance_status='Отсутствует')

        students = group.students_id.all()

        for student in students:
            attendance_value = request.POST.get(f'student_{student.id}', '')

            if attendance_value:
                Attendance.objects.create(
                    date_attendance=date_attendance,
                    attendance_status=attendance_status,
                    students_id=student,
                    groups_id=group,
                    branch=group.branch,
                )

        return redirect('all_groups')

    data = {
        'group': group,
    }

    if request.user.is_superuser:
        template_name = 'groups/attendance-group.html'
    else:
        template_name = 'teachers-group/teachers-mark-att.html'

    return render(request, template_name, data)


@login_required
def info_group(request, id_group):
    group = get_object_or_404(Group, pk=id_group)
    students = group.students_id.all()
    today = datetime.today().date()
    student_ids = students.values_list('id', flat=True)
    student_data = []
    for student in students:
        last_attendance = Attendance.objects.filter(students_id=student).order_by('-date_attendance').first()
        student_payments = Payment.objects.filter(student_id=student).order_by('-date_pay')

        student_data.append({
            'student': student,
            'attendance': last_attendance,
            'payments': student_payments

        })

    current_year = datetime.today().year
    data = {
        'group': group,
        'student_data': student_data,
        'current_year': current_year,
        'today': today,

    }

    if request.user.is_superuser:
        template_name = 'groups/info-group.html'
    else:
        template_name = 'teachers-group/teachers-group-info.html'

    return render(request, template_name, data)


@login_required()
def process_payment(request, student_id):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    student = get_object_or_404(Student, id=student_id)
    payments = Payment.objects.filter(student_id=student_id).order_by('-date_pay')
    courses = Course.objects.all()
    course_prices = {course.id: course.price_course for course in courses}

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.student_id = student
            payment.price = course_prices[int(form.cleaned_data['course_id'].id)]
            payment.save()

            student.paid_check = 'Оплатил'

            if not payments.exists():
                student.save()
            else:
                last_payment_date = payments.first().date_pay
                next_month_date = datetime.now().replace(day=1) + timedelta(days=32 - datetime.now().day)

                if last_payment_date == next_month_date:
                    student.paid_check = 'Не оплатил'
                    student.save()

            return redirect('profile_students', student.id)
    else:
        form = PaymentForm()

    data = {
        'student': student,
        'form': form,
        'payments': payments,
        'course_prices': course_prices
    }
    return render(request, 'students/payment.html', data)


@login_required()
def delete_selected_students(request):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    selected_students = request.POST.getlist('selected_students')
    comments = request.POST.get('comments', '')
    if selected_students:
        students_to_archive = Student.objects.filter(id__in=selected_students)
        for student in students_to_archive:
            archived_student = ArchivedStudent.objects.create(
                original_id=student.id,
                first_name_s=student.first_name_s,
                last_name_s=student.last_name_s,
                phone_number_s=student.phone_number_s,
                parents_phone_number=student.parents_phone_number,
                paid_check=student.paid_check,
                joined_date=student.joined_date,
                comments=comments,
                branch=student.branch
            )
            payments_to_archive = Payment.objects.filter(student_id=student)
            for payment in payments_to_archive:
                ArchivedPayment.objects.create(
                    student=archived_student,
                    method_pay=payment.method_pay,
                    date_pay=payment.date_pay,
                    price=payment.price,
                    branch=payment.branch
                )
                student.delete()
        return redirect('all_students')


@login_required()
def archived_students(request):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    archived_students = ArchivedStudent.objects.all()
    current_year = datetime.today().year
    data = {
        'archived_students': archived_students,
        'current_year': current_year
    }
    return render(request, 'students/archive-students.html', data)


@login_required()
def restore_student(request, student_id):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    archived_student = get_object_or_404(ArchivedStudent, original_id=student_id)

    Student.objects.create(
        first_name_s=archived_student.first_name_s,
        last_name_s=archived_student.last_name_s,
        phone_number_s=archived_student.phone_number_s,
        parents_phone_number=archived_student.parents_phone_number,
        paid_check=archived_student.paid_check,
        joined_date=archived_student.joined_date,
        branch=archived_student.branch
    )

    archived_student.delete()
    return redirect('archived_students')


@login_required()
def delete_archived_students_bulk(request):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    student_ids = request.POST.getlist('students_to_delete')
    for student_id in student_ids:
        archived_student = get_object_or_404(ArchivedStudent, original_id=student_id)
        archived_student.delete()
    return redirect('archived_students')


@login_required()
def main_page(request):
    paid_students = Student.objects.filter(paid_check='Оплатил').count()
    no_paid_students = Student.objects.filter(paid_check='Не оплатил').count()
    other_students = Student.objects.filter(paid_check=None).count()

    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect('all_groups')

    groups = Group.objects.all()
    group_data = []

    for group in groups:
        students_count = group.students_id.count()
        group_data.append({
            'group': group,
            'students_count': students_count,
            'course': group.course_id,
        })

    years = Student.objects.annotate(year=ExtractYear('joined_date')).values_list('year',
                                                                                  flat=True).distinct().order_by('year')

    current_year = request.GET.get('year', None)
    if current_year:
        students_per_month = Student.objects.filter(joined_date__year=current_year).annotate(
            month=TruncMonth('joined_date')).values('month').annotate(count=Count('id')).order_by('month')
    else:
        students_per_month = Student.objects.annotate(month=TruncMonth('joined_date')).values('month').annotate(
            count=Count('id')).order_by('month')

    month_data = defaultdict(lambda: 0)
    for item in students_per_month:
        month_data[item['month'].strftime('%B')] = item['count']

    all_months = [datetime.strptime(str(month), "%m").strftime("%B") for month in range(1, 13)]
    students_per_month_full = [(month, month_data[month]) for month in all_months]


    data = {
        'group_data': group_data,
        'total_groups': groups.count(),
        'total_students': Student.objects.count(),
        'paid_students': paid_students,
        'no_paid_students': no_paid_students,
        'other_students': other_students,
        'students_per_month': students_per_month_full,
        'years': years,
        'current_year': current_year,
    }

    return render(request, 'base.html', data)


@login_required()
def archived_groups(request):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    archived_groups = ArchivedGroup.objects.all()
    return render(request, 'groups/archived_group.html', {'archived_groups': archived_groups})


@login_required()
def delete_archived_group(request, id_archived_group):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    archived_group = get_object_or_404(ArchivedGroup, pk=id_archived_group)
    if request.method == 'POST':
        archived_group.delete()
        return redirect('archived_groups')


@login_required()
def restore_group(request, group_id):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    archived_group = get_object_or_404(ArchivedGroup, pk=group_id)
    status_instance = get_object_or_404(Status, id=2)

    instance_teacher = get_object_or_404(Teacher, id=archived_group.teacher_id.id)
    instance_audience = get_object_or_404(Audience, id=archived_group.audience_id.id)

    restored_group = Group.objects.create(
        name_group=archived_group.name_group,
        start_date=archived_group.start_date,
        end_date=archived_group.end_date,
        teacher_id=instance_teacher,
        audience_id=instance_audience,
        status_group=status_instance,
        branch=archived_group.branch,
        course_id=archived_group.course_id
    )

    restored_group.students_id.set(archived_group.students_id.all())

    archived_group.delete()

    return redirect('archived_students')


@login_required()
def delete_payment(request, payment_id):
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    payment = get_object_or_404(Payment, id=payment_id)
    student_id = payment.student_id.id

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)

        comment = request.POST.get('comment', '')
        ArchivedPayment.objects.create(
            student_id=payment.student_id,
            method_pay=payment.method_pay,
            date_pay=payment.date_pay,
            price=payment.price,
            branch=payment.branch,
            comments=comment,
            course_id=payment.course_id.id

        )
        payment.delete()
        return redirect('profile_students', id_student=student_id)
    comment_form = CommentForm()

    return render(request, 'students/delete_payment.html', {'payment': payment, 'comment_form': comment_form})


@login_required()
def archived_payments(request):
    archived_payments = ArchivedPayment.objects.all()
    context = {
        'archived_payments': archived_payments
    }
    return render(request, 'students/payment_archive.html', context)


@login_required()
def restore_payment(request, archived_payment_id):
    archived_payment = get_object_or_404(ArchivedPayment, id=archived_payment_id)

    Payment.objects.create(
        student_id=archived_payment.student_id,
        method_pay=archived_payment.method_pay,
        date_pay=archived_payment.date_pay,
        price=archived_payment.price,
        branch=archived_payment.branch,
        course_id=archived_payment.course
    )

    archived_payment.delete()

    return redirect('all_students')


def logout_view(request):
    logout(request)
    return redirect('login_page')


def login_page(request):
    req_user = Teacher.objects.filter(
        user_id=request.user.id).first()
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            messages.error(request, 'Invalid Username')
            return redirect('/login/')

        user = authenticate(username=username, password=password)

        if user is None:
            messages.error(request, "Invalid Password")
            return redirect('login_page')
        elif req_user:
            login(request, user)
            return redirect('all_groups')
        else:
            login(request, user)
            return redirect('main_page')

    return render(request, 'login/logIn.html')
