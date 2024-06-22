from datetime import timedelta

from django.core.paginator import Paginator
from django.db.models import Max
from django.db.models import Q
# Create your views here.
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect

from .forms import *


# Professor
def get_professor(request):
    search = SearchForm(request.GET)
    if search.is_valid():
        search_professor_name = search.cleaned_data.get('search_input', )
        if search_professor_name:
            found_professor = Teacher.objects.filter(Q(first_name__icontains=search_professor_name) |
                                                     Q(last_name__icontains=search_professor_name))
        else:
            found_professor = Teacher.objects.all()

        paginator = Paginator(found_professor, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        current_year = datetime.today().year
        data = {'search': search, 'professor': page_obj, 'current_year': current_year}
    else:
        professor = Teacher.objects.all()
        paginator = Paginator(professor, 10)

        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        current_year = datetime.today().year
        data = {'search': search, 'professor': page_obj, 'current_year': current_year}

    return render(request, 'professors/all-professors.html', data)


def delete_professor(request, id_professor):
    professor = get_object_or_404(Teacher, id=id_professor)
    current_year = datetime.today().year
    if request.method == 'POST':
        professor.delete()
        return redirect('all_professors')
    data = {'professor': professor, 'current_year': current_year}
    return render(request, 'professors/delete-professor.html', data)


def update_professor(request, id_professor):
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


def add_professor(request):
    professor_form = TeacherForm()
    if request.method == 'POST':
        professor_form = TeacherForm(request.POST, request.FILES)
        if professor_form.is_valid():
            professor = professor_form.save(commit=False)
            professor.save()
            return redirect('all_professors')
    return render(request, 'professors/add-professor.html', {'professor_form': professor_form})


# end Professor


# Course

def get_courses(request):
    search = SearchForm(request.GET)
    if search.is_valid():
        search_course_name = search.cleaned_data.get('search_input', )
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


def add_course(request):
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


def update_course(request, id_course):
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


def delete_course(request, id_course):
    course = get_object_or_404(Course, pk=id_course)
    current_year = datetime.today().year
    if request.method == 'POST':
        course.delete()
        return redirect('all_courses')
    data = {"course": course, "current_year": current_year}
    return render(request, 'courses/delete-course.html', data)


def all_status(request):
    status = Status.objects.all()
    current_year = datetime.today().year
    data = {'status': status, 'current_year': current_year}
    return render(request, 'status/all-status.html', data)


def add_status(request):
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


def update_status(request, id_status):
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


def delete_status(request, id_status):
    status = get_object_or_404(Status, pk=id_status)
    current_year = datetime.today().year
    if request.method == 'POST':
        status.delete()
        return redirect('all_status')
    data = {"status": status, "current_year": current_year}
    return render(request, 'status/delete-status.html', data)


def all_students(request):
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


def add_students(request, group_id=None):
    current_year = datetime.today().year
    if request.method == "POST":
        student_form = StudentForm(request.POST)
        if student_form.is_valid():
            if group_id:
                group = Group.objects.get(id=group_id)

                student = student_form.save(commit=False)
                student.save()
                group.students_id.add(student)

                return redirect('all_students')
            else:
                student = student_form.save(commit=False)
                student.save()
                return redirect('all_students')
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


def update_students(request, id_student):
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


def delete_students(request, id_student):
    student = get_object_or_404(Student, pk=id_student)
    current_year = datetime.today().year
    if request.method == 'POST':
        student.delete()
        return redirect('all_students')
    data = {"student": student, "current_year": current_year}
    return render(request, 'students/delete-student.html', data)


def profile_students(request, id_student):
    student = get_object_or_404(Student, id=id_student)
    payments = Payment.objects.filter(student_id=student)

    selected_month = request.GET.get('month')

    if selected_month:
        selected_month = int(selected_month)
        attendance = Attendance.objects.filter(students_id=id_student, date_attendance__month=selected_month)
    else:
        attendance = Attendance.objects.filter(students_id=id_student)
    # ошибка
    groups = Group.objects.filter(students_id=id_student)

    courses = Course.objects.filter(group__in=groups)

    current_year = datetime.today().year

    data = {
        'student': student,
        'payments': payments,
        'current_year': current_year,
        'attendance': attendance,
        'selected_month': selected_month,
        'courses': courses
    }

    return render(request, 'students/student-profile.html', data)


def all_audience(request):
    audience = Audience.objects.all()
    current_year = datetime.today().year
    data = {'audience': audience, 'current_year': current_year}
    return render(request, 'audience/all-audience.html', data)


def add_audience(request):
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


def update_audience(request, id_audience):
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


def delete_audience(request, id_audience):
    audience = get_object_or_404(Audience, pk=id_audience)
    current_year = datetime.today().year
    if request.method == 'POST':
        audience.delete()
        return redirect('all_audience')
    data = {'audience': audience, 'current_year': current_year}
    return render(request, 'audience/delete-audience.html', data)


def all_groups(request):
    groups = Group.objects.all()
    current_year = datetime.today().year
    data = {'groups': groups, 'current_year': current_year}
    return render(request, 'groups/all-groups.html', data)


def add_group(request):
    if request.method == 'POST':
        group_form = GroupForm(request.POST)
        if group_form.is_valid():
            group = group_form.save()
            return redirect('all_groups')
    else:
        group_form = GroupForm()

    current_year = datetime.today().year
    data = {"group_form": group_form, 'current_year': current_year}
    return render(request, 'groups/add-groups.html', data)


def update_group(request, id_group):
    group = get_object_or_404(Group, pk=id_group)
    current_year = datetime.today().year

    if request.method == 'POST':
        group_form = GroupForm(request.POST, instance=group)
        if group_form.is_valid():
            group_form.save()
            students_to_remove = request.POST.getlist('students_to_remove')
            if students_to_remove:
                group.students_id.remove(*students_to_remove)
            return redirect('all_groups')
        else:
            print(group_form.errors)
    else:
        group_form = GroupForm(instance=group)

    students_in_group = group.students_id.all()

    data = {
        "group_form": group_form,
        'current_year': current_year,
        'students_in_group': students_in_group,
        'group': group,
    }
    return render(request, 'groups/edit-groups.html', data)


def delete_group(request, id_group):
    group = get_object_or_404(Group, pk=id_group)
    current_year = datetime.today().year
    if request.method == 'POST':
        group.delete()
        return redirect('all_groups')
    data = {"group": group, 'current_year': current_year}
    return render(request, 'groups/delete-groups.html', data)


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
                    branch=group.branch
                )

        return redirect('all_groups')

    data = {
        'group': group,
    }
    return render(request, 'groups/attendance-group.html', data)


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
        'today': today
    }
    return render(request, 'groups/info-group.html', data)


def process_payment(request, student_id):
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


def delete_selected_students(request):
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


def archived_students(request):
    archived_students = ArchivedStudent.objects.all()
    current_year = datetime.today().year
    data = {
        'archived_students': archived_students,
        'current_year': current_year
    }
    return render(request, 'students/archive-students.html', data)


def restore_student(request, student_id):
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


def delete_archived_students_bulk(request):
    student_ids = request.POST.getlist('students_to_delete')
    for student_id in student_ids:
        archived_student = get_object_or_404(ArchivedStudent, original_id=student_id)
        archived_student.delete()
    return redirect('archived_students')


def main_page(request):
    groups = Group.objects.all()
    group_data = []

    for group in groups:
        students_count = group.students_id.count()
        group_data.append({
            'group': group,
            'students_count': students_count,
            'course': group.course_id
        })

    data = {
        'group_data': group_data,
        'total_groups': groups.count(),
        'total_students': Student.objects.count(),

    }

    return render(request, 'base.html', data)
