import json
import logging
from collections import defaultdict
from datetime import timedelta

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# from django.contrib.sites import requests
from django.core.paginator import Paginator
from django.db.models import Max, Count
from django.db.models.functions import ExtractYear, TruncMonth
from django.http import HttpResponseBadRequest
# Create your views here.
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from .forms import *

logger = logging.getLogger(__name__)


@csrf_exempt
def send_sms(phone,text,request):
    user = request.user
    if user.role == 'super admin':
        main_offices = MainOffice.objects.filter(admin=user).first()
    elif user.role == 'admin':
        branch = Branch.objects.filter(admin=user).first()
        main_offices = branch.main_office if branch else None
    elif user.role == 'teacher':
        teacher = Teacher.objects.filter(user=user).first()
        main_offices = teacher.main_office_id if teacher else None
    else:
        main_offices = None
    login_password = SMSLoginPassword.objects.filter(
        main_office_id__in=main_offices
    ).first()

    if not login_password:
        return 400, "Login and password not found"

    url = "http://83.69.139.182:8083/"
    encoded_text = text.encode('utf-8').decode('utf-8')
    payload = [{
        "phone": phone,
        "text": encoded_text
    }]
    data = {
        'login': login_password.login,
        'password': login_password.password,
        'data': json.dumps(payload)
    }

    response = requests.post(url, data=data, timeout=30)
    # try:
    #     response = requests.post(url, data=data,timeout=30)
    #     response.raise_for_status()  # проверка на HTTP ошибки
    #     print("Ответ сервера:", response.status_code, response.text)
    # except requests.exceptions.RequestException as e:
    #     print(f"Ошибка при отправке SMS: {e}")
    #     return 500, f"Ошибка при отправке SMS: {e}"

    return response.status_code, response.text


# Professor
@login_required(login_url='/login/')
def get_professor(request):
    user = request.user
    search = SearchForm(request.GET)
    current_year = datetime.today().year
    page_number = request.GET.get("page")
    if user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect('main_page')
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    branch_logo = Branch.objects.filter(admin_id=user.id)
    selected_main_office_id = request.GET.get('main_office')
    selected_branch_id = request.GET.get('branch')
    teachers = Teacher.objects.all()
    if user.role == 'super admin':
        if selected_main_office_id:
            teachers = teachers.filter(main_office_id=selected_main_office_id)
        elif selected_branch_id:
            teachers = teachers.filter(branch_id=selected_branch_id)
        else:
            teachers = teachers.filter(Q(main_office_id__in=main_offices) | Q(branch__in=branches))
    elif user.role == 'admin':
        if selected_branch_id:
            teachers = teachers.filter(branch_id=selected_branch_id)
        else:
            admin_branches = Branch.objects.filter(admin=user)
            teachers = teachers.filter(branch__in=admin_branches)
    elif user.role == 'teacher':
        user = request.user.id
        professor = Teacher.objects.filter(user_id=user).first()
        groups = Group.objects.filter(teacher_id=professor)

    if search.is_valid():
        search_professor_name = search.cleaned_data.get('search_input', '')
        if search_professor_name:
            teachers = teachers.filter(
                Q(first_name__icontains=search_professor_name) | Q(last_name__icontains=search_professor_name))

    paginator = Paginator(teachers, 10)
    page_obj = paginator.get_page(page_number)

    data = {
        'search': search,
        'professor': page_obj,
        'current_year': current_year,
        'user': user,
        'main_offices': main_offices,
        'branches': branches,
        'selected_main_office_id': selected_main_office_id,
        'selected_branch_id': selected_branch_id,
        'branch_logo': branch_logo
    }

    return render(request, 'professors/all-professors.html', data)


@login_required(login_url='/login/')
def delete_professor(request, id_professor):
    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branch_logo = Branch.objects.filter(admin_id=user.id)
    if request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    professor = get_object_or_404(Teacher, id=id_professor)
    current_year = datetime.today().year
    if request.method == 'POST':
        professor.delete()
        return redirect('all_professors')
    data = {'professor': professor, 'current_year': current_year, 'branch_logo': branch_logo,
            'main_offices': main_offices,
            'branch': Branch.objects.filter(admin_id=request.user.id)}
    return render(request, 'professors/delete-professor.html', data)


@login_required(login_url='/login/')
def update_professor(request, id_professor):
    professor = get_object_or_404(Teacher, pk=id_professor)
    current_year = datetime.today().year
    user = request.user

    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    branch_logo = Branch.objects.filter(admin_id=user.id)

    if request.user.role == 'teacher' and professor.user != request.user:
        return redirect('all_groups')

    if request.method == 'POST':
        form = TeacherUpdateForm(request.POST, instance=professor)
        if form.is_valid():
            form.save()
            return redirect('all_professors')
    else:
        form = TeacherUpdateForm(instance=professor)

    data = {"form": form, "current_year": current_year, 'professor': professor, 'main_offices': main_offices,
            'branches': branches, 'branch_logo': branch_logo,
            'branch': Branch.objects.filter(admin_id=request.user.id)}

    if request.user.role == 'super admin':
        template_name = 'professors/edit-professor.html'
    elif request.user.role == 'teacher':
        template_name = 'teachers-group/teachers-profile.html'

    return render(request, template_name, data)


@login_required(login_url='/login/')
def add_professor(request):
    user = request.user
    main_office = MainOffice.objects.filter(admin=user).first()
    branch_office = Branch.objects.filter(admin=user).first()
    branch_logo = Branch.objects.filter(admin_id=user.id)
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)

    if request.user.role != 'teacher':
        if request.method == 'POST':
            professor_form = TeacherForm(request.POST, request.FILES,
                                         main_office_id=main_office.id if main_office else None,
                                         branch_office_id=branch_office.id if branch_office else None)
            if professor_form.is_valid():
                professor = professor_form.save(commit=False)
                if request.user.role == 'super admin':
                    professor.main_office_id = main_office
                elif request.user.role == 'admin':
                    professor.branch = branch_office
                professor.save()
                return redirect('all_professors')
        else:
            professor_form = TeacherForm(main_office_id=main_office.id if main_office else None,
                                         branch_office_id=branch_office.id if branch_office else None)
    else:
        professor_form = None

    return render(request, 'professors/add-professor.html', {
        'professor_form': professor_form,
        'branch': Branch.objects.filter(admin_id=request.user.id),
        'main_offices': main_offices,
        'branches': branches,
        'branch_logo': branch_logo
    })


@login_required(login_url='/login/')
def get_courses(request):
    current_year = datetime.today().year
    if request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    branch_logo = Branch.objects.filter(admin_id=user.id)
    search = SearchForm(request.GET)
    selected_main_office_id = request.GET.get('main_office')
    selected_branch_id = request.GET.get('branch')
    selected_branch_id = request.GET.get('branch')
    page_number = request.GET.get("page")
    courses = Course.objects.all()
    if user.role == 'super admin':
        if selected_main_office_id:
            courses = courses.filter(main_office_id=selected_main_office_id)

        elif selected_branch_id:
            courses = courses.filter(branch_id=selected_branch_id)
        else:
            courses = courses.filter(Q(main_office_id__in=main_offices) | Q(branch__in=branches))
    elif user.role == 'admin':
        if selected_branch_id:
            courses = courses.filter(branch_id=selected_branch_id)
        else:
            admin_branches = Branch.objects.filter(admin=user)
            courses = courses.filter(branch__in=admin_branches)
    print(courses.values())
    if search.is_valid():
        search_course_name = search.cleaned_data.get('search_input', '')
        if search_course_name:
            found_course = Course.objects.filter(name_course__icontains=search_course_name)

    paginator = Paginator(courses, 10)
    page_obj = paginator.get_page(page_number)

    data = {
        'search': search,
        'course': page_obj,
        'current_year': current_year,
        'user': user,
        'main_offices': main_offices,
        'branches': branches,
        'selected_main_office_id': selected_main_office_id,
        'selected_branch_id': selected_branch_id,
        'branch_logo': branch_logo
    }
    # if request.user.role == 'super admin':
    #     search = SearchForm(request.GET)
    #     if search.is_valid():
    #         search_course_name = search.cleaned_data.get('search_input', '')
    #         if search_course_name:
    #             found_course = Course.objects.filter(name_course__icontains=search_course_name)
    #         else:
    #             found_course = Course.objects.all()
    #         paginator = Paginator(found_course, 10)
    #         page_number = request.GET.get("page")
    #         page_obj = paginator.get_page(page_number)
    #         current_year = datetime.today().year
    #         data = {'search': search, 'courses': page_obj, 'current_year': current_year,
    #                 'branch': Branch.objects.filter(admin_id=request.user.id)}
    #     else:
    #         course = Course.objects.all()
    #         paginator = Paginator(course, 10)
    #
    #         page_number = request.GET.get("page")
    #         page_obj = paginator.get_page(page_number)
    #         current_year = datetime.today().year
    #         data = {'search': search, 'courses': page_obj, 'current_year': current_year,
    #                 'branch': Branch.objects.filter(admin_id=request.user.id)}
    # elif request.user.role == 'admin':
    #     search = SearchForm(request.GET)
    #     if search.is_valid():
    #         search_course_name = search.cleaned_data.get('search_input', '')
    #         if search_course_name:
    #             found_course = Course.objects.filter(name_course__icontains=search_course_name)
    #         else:
    #             found_course = Course.objects.filter(branch__admin=request.user)
    #         paginator = Paginator(found_course, 10)
    #         page_number = request.GET.get("page")
    #         page_obj = paginator.get_page(page_number)
    #         current_year = datetime.today().year
    #         data = {'search': search, 'courses': page_obj, 'current_year': current_year}
    #     else:
    #         course = Course.objects.filter(branch__admin=request.user)
    #         paginator = Paginator(course, 10)
    #
    #         page_number = request.GET.get("page")
    #         page_obj = paginator.get_page(page_number)
    #         current_year = datetime.today().year
    #         data = {'search': search, 'courses': page_obj, 'current_year': current_year}

    return render(request, 'courses/all-courses.html', data)


@login_required(login_url='/login/')
def add_course(request):
    if request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    course_form = CourseForm()
    current_year = datetime.today().year
    user = request.user
    branch_logo = Branch.objects.filter(admin_id=user.id)
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    if request.method == 'POST':

        course_form = CourseForm(request.POST, request.FILES)

        if course_form.is_valid():
            course = course_form.save(commit=False)
            if request.user.role == 'super admin':
                user = request.user
                main_offices = MainOffice.objects.filter(admin_id=user.id).first()

                course.main_office_id = main_offices
            elif request.user.role == 'admin':
                user = request.user
                branches = Branch.objects.filter(admin_id=user.id).first()

                course.branch = branches
            course.save()

        return redirect('all_courses')
    else:
        course_form = CourseForm()
        data = {"course_form": course_form, 'current_year': current_year, 'main_offices': main_offices,
                'branches': branches, 'branch_logo': branch_logo}
    return render(request, 'courses/add-course.html', data)


@login_required(login_url='/login/')
def update_course(request, id_course):
    if request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    course = get_object_or_404(Course, pk=id_course)
    current_year = datetime.today().year
    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branch_logo = Branch.objects.filter(admin_id=user.id)
    branches = Branch.objects.filter(main_office__in=main_offices)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('all_courses')
    else:
        form = CourseForm(instance=course)
    data = {"form": form, "current_year": current_year, 'main_offices': main_offices, 'branch_logo': branch_logo,
            'branches': branches, }
    return render(request, 'courses/edit-course.html', data)


@login_required(login_url='/login/')
def delete_course(request, id_course):
    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    branch_logo = Branch.objects.filter(admin_id=user.id)
    if request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    course = get_object_or_404(Course, pk=id_course)
    current_year = datetime.today().year
    if request.method == 'POST':
        course.delete()
        return redirect('all_courses')
    data = {"course": course, "current_year": current_year, 'main_offices': main_offices,
            'branches': branches, 'branch_logo': branch_logo}
    return render(request, 'courses/delete-course.html', data)


# @login_required(login_url='/login/')
# def all_status(request):
#     user = request.user
#     current_year = datetime.today().year
#     if user.role == 'teacher':
#         messages.error(request, 'У вас нет прав доступа.')
#         return redirect('main_page')
#     main_offices = MainOffice.objects.filter(admin=user)
#     branches = Branch.objects.filter(main_office__in=main_offices)
#     selected_main_office_id = request.GET.get('main_office')
#     selected_branch_id = request.GET.get('branch')
#     selected_branch_id = request.GET.get('branch')
#
#     teachers = Teacher.objects.all()
#     if user.role == 'super admin':
#         if selected_main_office_id:
#             teachers = teachers.filter(main_office_id=selected_main_office_id)
#         elif selected_branch_id:
#             teachers = teachers.filter(branch_id=selected_branch_id)
#         else:
#             teachers = teachers.filter(Q(main_office_id__in=main_offices) | Q(branch__in=branches))
#     elif user.role == 'admin':
#         if selected_branch_id:
#             teachers = teachers.filter(branch_id=selected_branch_id)
#         else:
#             admin_branches = Branch.objects.filter(admin=user)
#             teachers = teachers.filter(branch__in=admin_branches)
#     if not request.user.is_superuser:
#         messages.error(request, 'У вас нет прав доступа.')
#         return redirect(
#             'main_page')
#     if request.user.role == 'super admin':
#         user = request.user
#     status = Status.objects.all()
#     current_year = datetime.today().year
#     data = {'status': status, 'current_year': current_year}
#     return render(request, 'status/all-status.html', data)
#
#
# @login_required(login_url='/login/')
# def add_status(request):
#     if not request.user.is_superuser:
#         messages.error(request, 'У вас нет прав доступа.')
#         return redirect(
#             'main_page')
#     status_form = StatusForm(request.POST)
#     current_year = datetime.today().year
#     if status_form.is_valid():
#         status = status_form.save(commit=False)
#         status.slug_status = status.name_status
#         status.save()
#         return redirect('all_status')
#     status_form = StatusForm()
#     data = {"status_form": status_form, 'current_year': current_year}
#     return render(request, 'status/add-status.html', data)
#
#
# @login_required(login_url='/login/')
# def update_status(request, id_status):
#     if not request.user.is_superuser:
#         messages.error(request, 'У вас нет прав доступа.')
#         return redirect(
#             'main_page')
#     status = get_object_or_404(Status, pk=id_status)
#     current_year = datetime.today().year
#     if request.method == 'POST':
#         form = StatusForm(request.POST, instance=status)
#         if form.is_valid():
#             status.slug_status = status.name_status
#             form.save()
#             return redirect('all_status')
#     else:
#         form = StatusForm(instance=status)
#     data = {"form": form, "current_year": current_year}
#     return render(request, 'status/update-status.html', data)
#
#
# @login_required(login_url='/login/')
# def delete_status(request, id_status):
#     if not request.user.is_superuser:
#         messages.error(request, 'У вас нет прав доступа.')
#         return redirect(
#             'main_page')
#     status = get_object_or_404(Status, pk=id_status)
#     current_year = datetime.today().year
#     if request.method == 'POST':
#         status.delete()
#         return redirect('all_status')
#     data = {"status": status, "current_year": current_year}
#     return render(request, 'status/delete-status.html', data)


@login_required(login_url='/login/')
def all_students(request):
    user = request.user
    search = SearchForm(request.GET)
    current_year = datetime.today().year
    page_number = request.GET.get("page")
    branch_logo = Branch.objects.filter(admin_id=user.id)

    if user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect('all_groups')

    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)

    selected_main_office_id = request.GET.get('main_office')
    selected_branch_id = request.GET.get('branch')

    found_student = Student.objects.all()
    paid_students = 0
    no_paid_students = 0

    if user.role == 'super admin':
        paid_students = Student.objects.filter(paid_check='Оплатил', main_office_id__admin=user).count()
        no_paid_students = Student.objects.filter(paid_check='Не оплатил', main_office_id__admin=user).count()

        if selected_main_office_id:
            found_student = found_student.filter(main_office_id=selected_main_office_id)
        elif selected_branch_id:
            found_student = found_student.filter(branch_id=selected_branch_id)
        else:
            found_student = found_student.filter(Q(main_office_id__in=main_offices) | Q(branch__in=branches))


    elif user.role == 'admin':
        paid_students = Student.objects.filter(paid_check='Оплатил', main_office_id=branches.first()).count()
        no_paid_students = Student.objects.filter(paid_check='Не оплатил', main_office_id=branches.first()).count()

        if selected_branch_id:
            found_student = found_student.filter(branch_id=selected_branch_id)
        else:
            admin_branches = Branch.objects.filter(admin=user)
            found_student = found_student.filter(branch__in=admin_branches)

    filter_option = request.GET.get('filter')
    if filter_option == 'not_paid':
        found_student = found_student.filter(paid_check='Не оплатил')

    paginator = Paginator(found_student, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

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

    if search.is_valid():
        search_professor_name = search.cleaned_data.get('search_input', '')
        if search_professor_name:
            found_student = found_student.filter(
                Q(first_name__icontains=search_professor_name) | Q(last_name__icontains=search_professor_name))

    paginator = Paginator(found_student, 10)
    page_obj = paginator.get_page(page_number)

    groups_branch = Group.objects.all()
    data = {
        'search': search,
        'groups_branch': groups_branch,
        'student': page_obj,
        'current_year': current_year,
        'user': user,
        'main_offices': main_offices,
        'branches': branches,
        'selected_main_office_id': selected_main_office_id,
        'selected_branch_id': selected_branch_id,
        'branch_logo': branch_logo,
        'paid_students': paid_students,
        'no_paid_students': no_paid_students
    }
    return render(request, 'students/all-students.html', data)


@login_required(login_url='/login/')
def add_students(request, group_id=None):
    current_year = datetime.today().year
    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    branch_logo = Branch.objects.filter(admin_id=user.id)

    students_without_group = Student.objects.filter(group_student_id__isnull=True)

    if request.method == "POST":
        student_id = request.POST.get('student_id')
        if student_id:
            student = Student.objects.get(id=student_id)
            if group_id:
                group = Group.objects.get(id=group_id)
                student.group_student_id = group
                student.save()
                group.students_id.add(student)
                group.save()
                QuantityStudent.objects.create(first_name_s=student.first_name_s, last_name_s=student.last_name_s,
                                               joined_date=datetime.today(), branch=student.branch,
                                               main_office_id=student.main_office_id)
                return redirect('add_students_to_group', group_id=group_id)

        student_form = StudentForm(request.POST)
        if request.user.role == 'super admin':
            if student_form.is_valid():
                student = student_form.save(commit=False)
                if group_id:
                    group = Group.objects.get(id=group_id)
                    if group.main_office_id in main_offices:
                        student.main_office_id = group.main_office_id
                    elif group.branch in branches:
                        student.branch = group.branch
                    student.group_student_id = group
                    student.save()
                    group.students_id.add(student)
                    QuantityStudent.objects.create(first_name_s=student.first_name_s, last_name_s=student.last_name_s,
                                                   joined_date=datetime.today(), branch=student.branch,
                                                   main_office_id=student.main_office_id)
                    return redirect('all_groups')
                else:
                    student.save()
                    return redirect('all_groups')
        elif request.user.role == 'admin':
            if student_form.is_valid():
                student = student_form.save(commit=False)
                if group_id:
                    group = Group.objects.get(id=group_id)
                    student.branch = group.branch
                    student.group_student_id = group  # Присваиваем объект группы
                    student.save()
                    group.students_id.add(student)
                    QuantityStudent.objects.create(first_name_s=student.first_name_s, last_name_s=student.last_name_s,
                                                   joined_date=datetime.today(), branch=student.branch,
                                                   main_office_id=student.main_office_id)
                    return redirect('all_groups')
                else:
                    student.save()
                    return redirect('all_groups')
    else:
        student_form = StudentForm()

    groups = Group.objects.all()
    data = {
        "student_form": student_form,
        'current_year': current_year,
        'groups': groups,
        'selected_group_id': group_id,
        'main_offices': main_offices,
        'branches': branches,
        'branch_logo': branch_logo,
        'students_without_group': students_without_group
    }
    return render(request, 'groups/add_students_to_group.html', data)


@login_required(login_url='/login/')
def update_students(request, id_student):
    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    branch_logo = Branch.objects.filter(admin_id=user.id)
    if request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    student = get_object_or_404(Student, pk=id_student)
    current_year = datetime.today().year
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('all_students')
    else:
        form = StudentForm(instance=student)
    data = {"form": form, "current_year": current_year, 'main_offices': main_offices,
            'branches': branches, 'branch_logo': branch_logo}
    return render(request, 'students/edit-student.html', data)


@login_required(login_url='/login/')
def delete_students(request, id_student):
    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    branch_logo = Branch.objects.filter(admin_id=user.id)
    if request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    student = get_object_or_404(Student, pk=id_student)
    current_year = datetime.today().year
    if request.method == 'POST':
        student.delete()
        return redirect('all_students')
    data = {"student": student, "current_year": current_year, 'main_offices': main_offices,
            'branches': branches, 'branch_logo': branch_logo}
    return render(request, 'students/delete-student.html', data)


@login_required(login_url='/login/')
def profile_students(request, id_student):
    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    student = get_object_or_404(Student, id=id_student)
    payments = Payment.objects.filter(student_id=student)
    branch_logo = Branch.objects.filter(admin_id=user.id)
    selected_month = request.GET.get('month')

    if selected_month:
        selected_month = int(selected_month)
        attendance = Attendance.objects.filter(students_id=id_student, date_attendance__month=selected_month)
    else:
        attendance = Attendance.objects.filter(students_id=id_student)

    groups = Group.objects.filter(students_id=id_student, branch__admin=request.user)

    courses = Course.objects.filter(group__in=groups, branch__admin=request.user).distinct()

    current_year = datetime.today().year

    data = {
        'student': student,
        'payments': payments,
        'current_year': current_year,
        'attendance': attendance,
        'selected_month': selected_month,
        'courses': courses,
        'main_offices': main_offices,
        'branches': branches,
        'branch_logo': branch_logo
    }

    if request.user.role == 'super admin' or request.user.role == 'admin':
        template_name = 'students/student-profile.html'
    else:
        template_name = 'teachers-group/teachers-st-profile.html'

    return render(request, template_name, data)


@login_required(login_url='/login/')
def all_audience(request):
    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    branch_logo = Branch.objects.filter(admin_id=user.id)
    selected_main_office_id = request.GET.get('main_office')
    selected_branch_id = request.GET.get('branch')

    audience = Audience.objects.all()
    if user.role == 'super admin':
        if selected_main_office_id:
            audience = audience.filter(main_office_id=selected_main_office_id)
        elif selected_branch_id:
            audience = audience.filter(branch_id=selected_branch_id)
        else:
            audience = audience.filter(Q(main_office_id__in=main_offices) | Q(branch__in=branches))
    elif user.role == 'admin':
        if selected_branch_id:
            audience = audience.filter(branch_id=selected_branch_id)
        else:
            admin_branches = Branch.objects.filter(admin=user)
            audience = audience.filter(branch__in=admin_branches)

    current_year = datetime.today().year
    data = {'audience': audience, 'current_year': current_year, 'main_offices': main_offices,
            'branches': branches,
            'selected_main_office_id': selected_main_office_id,
            'selected_branch_id': selected_branch_id, 'branch_logo': branch_logo}
    return render(request, 'audience/all-audience.html', data)


@login_required(login_url='/login/')
def add_audience(request):
    audience_form = AudienceForm(request.POST)
    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    audience = Audience.objects.all()
    current_year = datetime.today().year
    branch_logo = Branch.objects.filter(admin_id=user.id)
    if audience_form.is_valid():
        audience = audience_form.save(commit=False)
        if request.user.role == 'super admin':
            user = request.user
            main_offices = MainOffice.objects.filter(admin_id=user.id).first()
            print(main_offices)
            audience.main_office_id = main_offices
            audience.slug_audience = audience.number_audience
        elif request.user.role == 'admin':
            user = request.user
            branches = Branch.objects.filter(admin_id=user.id).first()
            audience.slug_audience = audience.number_audience
            print(branches)
            audience.branch = branches
        audience.save()

        return redirect('all_audience')
    audience_form = AudienceForm()
    data = {"audience_form": audience_form, 'current_year': current_year, 'main_offices': main_offices,
            'branches': branches, 'branch_logo': branch_logo}
    return render(request, 'audience/add-audience.html', data)


@login_required(login_url='/login/')
def update_audience(request, id_audience):
    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    branch_logo = Branch.objects.filter(admin_id=user.id)
    if request.user.role == 'teacher':
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
    data = {"audience_form": audience_form, 'current_year': current_year, 'main_offices': main_offices,
            'branches': branches, 'branch_logo': branch_logo}
    return render(request, 'audience/edit-audience.html', data)


@login_required(login_url='/login/')
def delete_audience(request, id_audience):
    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    branch_logo = Branch.objects.filter(admin_id=user.id)
    if request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    audience = get_object_or_404(Audience, pk=id_audience)
    current_year = datetime.today().year
    if request.method == 'POST':
        audience.delete()
        return redirect('all_audience')
    data = {'audience': audience, 'current_year': current_year, 'main_offices': main_offices,
            'branches': branches, 'branch_logo': branch_logo}
    return render(request, 'audience/delete-audience.html', data)


@login_required(login_url='/login/')
def all_groups(request):
    user = request.user
    current_year = datetime.today().year
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    selected_main_office_id = request.GET.get('main_office')
    selected_branch_id = request.GET.get('branch')
    branch_logo = Branch.objects.filter(admin_id=user.id)
    groups = Group.objects.all()

    if user.role == 'super admin':
        if selected_main_office_id:
            groups = groups.filter(main_office_id=selected_main_office_id)
        elif selected_branch_id:
            groups = groups.filter(branch_id=selected_branch_id)
        else:
            groups = groups.filter(Q(main_office_id__in=main_offices) | Q(branch__in=branches))
    elif user.role == 'admin':
        if selected_branch_id:
            groups = groups.filter(branch_id=selected_branch_id)
        else:
            admin_branches = Branch.objects.filter(admin=user)
            groups = groups.filter(branch__in=admin_branches)
    elif user.role == 'teacher':
        user = request.user.id

        professor = Teacher.objects.filter(user_id=user).first()

        groups = Group.objects.filter(teacher_id=professor)
        data = {'groups': groups, 'current_year': current_year, 'professors': professor, 'branch_logo': branch_logo}
        return render(request, 'teachers-group/teachers_group.html', data)
    data = {
        'groups': groups,
        'current_year': current_year,
        'user': user,
        'main_offices': main_offices,
        'branches': branches,
        'selected_main_office_id': selected_main_office_id,
        'selected_branch_id': selected_branch_id,
        'branch_logo': branch_logo
    }

    return render(request, 'groups/all-groups.html', data)


@login_required(login_url='/login/')
def add_group(request):
    current_year = datetime.today().year
    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    branch_logo = Branch.objects.filter(admin_id=user.id)

    if request.method == 'POST':
        main_office = MainOffice.objects.filter(admin=user).first()
        branch_office = Branch.objects.filter(admin=user).first()

        group_form = GroupForm(request.POST, main_office_id=main_office.id if main_office else None,
                               branch_office_id=branch_office.id if branch_office else None)

        if group_form.is_valid():
            group = group_form.save(commit=False)
            if request.user.role == 'super admin':
                group.main_office_id = main_office
            elif request.user.role == 'admin':
                group.branch = branch_office
            group.save()
            return redirect('all_groups')
    else:
        main_office = MainOffice.objects.filter(admin=user).first()
        branch_office = Branch.objects.filter(admin=user).first()

        group_form = GroupForm(main_office_id=main_office.id if main_office else None,
                               branch_office_id=branch_office.id if branch_office else None)

    data = {
        'group_form': group_form,
        'current_year': current_year,
        'main_offices': main_offices,
        'branches': branches,
        'branch_logo': branch_logo
    }
    return render(request, 'groups/add-groups.html', data)


@login_required(login_url='/login/')
def update_group(request, id_group):
    group = get_object_or_404(Group, pk=id_group)
    current_year = datetime.today().year
    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    branch_logo = Branch.objects.filter(admin_id=user.id)
    if request.user.role == 'super admin' or request.user.role == 'admin':
        if request.method == 'POST':
            main_office = MainOffice.objects.filter(admin=user).first()
            branch_office = Branch.objects.filter(admin=user).first()
            group_form = GroupForm(request.POST, instance=group, main_office_id=main_office.id if main_office else None,
                                   branch_office_id=branch_office.id if branch_office else None)
            if group_form.is_valid():
                group_form.save()
                students_to_remove = request.POST.getlist('students_to_remove')
                if students_to_remove:
                    group.students_id.remove(*students_to_remove)
                return redirect('all_groups')
            else:
                messages.error(request, group_form.errors)
        else:
            main_office = MainOffice.objects.filter(admin=user).first()
            branch_office = Branch.objects.filter(admin=user).first()
            group_form = GroupForm(instance=group, main_office_id=main_office.id if main_office else None,
                                   branch_office_id=branch_office.id if branch_office else None)
        students_in_group = group.students_id.all()
    elif request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав')
        return redirect('all_groups')

    data = {"group_form": group_form, 'current_year': current_year, 'messages': messages,
            'students_in_group': students_in_group, 'main_offices': main_offices,
            'branches': branches, 'branch_logo': branch_logo}
    return render(request, 'groups/edit-groups.html', data)


@login_required(login_url='/login/')
def delete_group(request, id_group):
    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    branch_logo = Branch.objects.filter(admin_id=user.id)
    if request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect('all_groups')

    group = get_object_or_404(Group, pk=id_group)

    if request.method == 'POST':
        comment = request.POST.get('comment', '')

        status_instance = get_object_or_404(Status, name_status='Курс окончен')

        # Create the archived group
        archived_group = ArchivedGroup.objects.create(
            name_group=group.name_group,
            start_date=group.start_date,
            end_date=group.end_date,
            teacher_id=group.teacher_id,
            audience_id=group.audience_id,
            status_group=status_instance,
            branch=group.branch,
            main_office_id=group.main_office_id,
            course_id=group.course_id,
            comments=comment,
        )

        # Archive the students
        for student in group.students_id.all():
            ArchivedStudent.objects.create(
                first_name_s=student.first_name_s,
                last_name_s=student.last_name_s,
                phone_number_s=student.phone_number_s,
                paid_check=student.paid_check,
                parents_phone_number=student.parents_phone_number,
                joined_date=student.joined_date,
                comments="окончил(а) курс",
                branch=student.branch,
            )
            student.delete()

        archived_group.students_id.set(group.students_id.all())
        group.students_id.clear()
        group.delete()

        return redirect('archived_students')

    comment_form = CommentForm()

    data = {"group": group, 'comment_form': comment_form, 'main_offices': main_offices,
            'branches': branches, 'branch_logo': branch_logo}
    return render(request, 'groups/delete-groups.html', data)


@login_required(login_url='/login/')
def mark_attendance(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    branch_logo = Branch.objects.filter(admin_id=user.id)
    template_sms = SmsTemplates.objects.filter(text_categories='sms для посещаемости').first()

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

                phone = student.parents_phone_number
                text = template_sms.text_sms.format(
                    edu_name=student.main_office_id.name_main_office,
                    student_name=f'{student.first_name_s} {student.last_name_s}',
                    date=date_attendance
                )

                send_sms(phone, text, request)
        return redirect('all_groups')

    data = {
        'group': group,
        'main_offices': main_offices,
        'branches': branches,
        'branch_logo': branch_logo
    }

    template_name = 'groups/attendance-group.html' if request.user.role in ['super admin',
                                                                            'admin'] else 'teachers-group/teachers-mark-att.html'
    return render(request, template_name, data)


@login_required(login_url='/login/')
def info_group(request, id_group):
    current_year = datetime.now().year
    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    branch_logo = Branch.objects.filter(admin_id=user.id)
    group = get_object_or_404(Group, pk=id_group)
    students = group.students_id.all()
    today = datetime.today().date()
    student_ids = students.values_list('id', flat=True)
    user = request.user.id
    professor = Teacher.objects.filter(user_id=user).first()
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
        'main_offices': main_offices,
        'branches': branches,
        'branch_logo': branch_logo,
        'student': student,
        'professors': professor,

    }

    if request.user.role == 'admin' or request.user.role == 'super admin':
        template_name = 'groups/info-group.html'
    else:
        template_name = 'teachers-group/teachers-group-info.html'

    return render(request, template_name, data)


@login_required(login_url='/login/')
def process_payment(request, student_id):
    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    branch_logo = Branch.objects.filter(admin_id=user.id)
    if request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect('all_groups')

    student = get_object_or_404(Student, id=student_id)
    payments = Payment.objects.filter(student_id=student_id).order_by('-date_pay')

    group = Group.objects.filter(students_id=student).first()
    if not group:
        messages.error(request, 'Студент не зарегистрирован ни в одной группе.')
        return redirect('main_page')

    course = group.course_id
    course_price = course.price_course

    last_payment_date = payments.first().date_pay if payments.exists() else None

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.student_id = student
            payment.course_id = course
            payment.price = course_price
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
        'course_price': course_price,
        'message': messages,
        'last_payment_date': last_payment_date,  # Передаем дату последней оплаты в контекст
        'main_offices': main_offices,
        'branches': branches,
        'branch_logo': branch_logo
    }
    return render(request, 'students/payment.html', data)


@login_required(login_url='/login/')
def delete_selected_students(request):
    if request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect('all_groups')
    selected_students = request.POST.getlist('selected_students')
    template_sms = SmsTemplates.objects.filter(text_categories='sms для должников').first()
    action = request.POST.get('action')

    if request.method == 'POST':
        if action == 'delete':
            comments = request.POST.get('comments', '')

            for student_id in selected_students:
                try:
                    student = Student.objects.get(id=student_id)
                    archived_student = ArchivedStudent.objects.create(
                        first_name_s=student.first_name_s,
                        last_name_s=student.last_name_s,
                        phone_number_s=student.phone_number_s,
                        parents_phone_number=student.parents_phone_number,
                        paid_check=student.paid_check,
                        joined_date=student.joined_date,
                        comments=comments,
                        branch=student.branch,
                        main_office_id=student.main_office_id,
                    )
                    payments_to_archive = Payment.objects.filter(student_id=student.id)
                    for payment in payments_to_archive:
                        ArchivedPayment.objects.create(
                            student_id=student,
                            method_pay=payment.method_pay,
                            date_pay=payment.date_pay,
                            price=payment.price,
                            branch=payment.branch,
                            course=payment.course_id,

                        )
                    payments_to_archive.delete()
                    student.delete()
                except Student.DoesNotExist:
                    messages.error(request, f'Студент с ID {student_id} не найден.')

        elif action == 'send_sms':
            for student_id in selected_students:
                student = get_object_or_404(Student, pk=student_id)
                phone = student.phone_number_s
                text = template_sms.text_sms.format(
                    edu_name=student.main_office_id.name_main_office,
                    student_name=f'{student.first_name_s} {student.last_name_s}',
                    date=datetime.today(),
                )
                send_sms(phone, text, request)
        return redirect('all_students')

    else:
        return HttpResponseBadRequest('Метод запроса должен быть POST.')


@login_required(login_url='/login/')
def archived_students(request):
    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    branch_logo = Branch.objects.filter(admin_id=user.id)
    selected_main_office_id = request.GET.get('main_office')
    selected_branch_id = request.GET.get('branch')
    archived_students = ArchivedStudent.objects.all()

    if user.role == 'super admin':
        if selected_main_office_id:
            archived_students = archived_students.filter(main_office_id=selected_main_office_id)
        if selected_branch_id:
            archived_students = archived_students.filter(branch_id=selected_branch_id)
        if not selected_main_office_id and not selected_branch_id:
            archived_students = archived_students.filter(Q(main_office_id__in=main_offices) | Q(branch__in=branches))
    elif user.role == 'admin':
        if selected_branch_id:
            archived_students = archived_students.filter(branch_id=selected_branch_id)
        else:
            admin_branches = Branch.objects.filter(admin=user)
            archived_students = archived_students.filter(branch__in=admin_branches)
    if request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')

    current_year = datetime.today().year
    paginator = Paginator(archived_students, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    data = {
        'archived_students': page_obj,
        'current_year': current_year,
        'selected_main_office_id': selected_main_office_id,
        'selected_branch_id': selected_branch_id,
        'main_offices': main_offices,
        'branches': branches,
        'branch_logo': branch_logo
    }
    return render(request, 'students/archive-students.html', data)


@login_required(login_url='/login/')
def restore_student(request, student_id):
    if request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    archived_student = get_object_or_404(ArchivedStudent, pk=student_id)

    Student.objects.create(
        first_name_s=archived_student.first_name_s,
        last_name_s=archived_student.last_name_s,
        phone_number_s=archived_student.phone_number_s,
        parents_phone_number=archived_student.parents_phone_number,
        paid_check=archived_student.paid_check,
        joined_date=archived_student.joined_date,
        branch=archived_student.branch,
        main_office_id=archived_student.main_office_id,
    )

    archived_student.delete()
    return redirect('archived_students')


@login_required(login_url='/login/')
def delete_archived_students(request):
    if request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    student_ids = request.POST.getlist('students_to_delete')
    for student_id in student_ids:
        archived_student = get_object_or_404(ArchivedStudent, id=student_id)
        archived_student.delete()
    return redirect('archived_students')


@login_required(login_url='/login/')
def main_page(request):
    user = request.user
    branch_logo = Branch.objects.filter(admin_id=user.id)
    template_sms = SmsTemplates.objects.filter(text_categories='sms для посещаемости').first()
    if not request.user.is_authenticated:
        return redirect('login_page')
    if request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect('all_groups')

    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(admin=user)

    if request.user.role == 'super admin':
        completed_the_course = ArchivedStudent.objects.filter(comments='окончил(а) курс',
                                                              main_office_id=main_offices.first()).count()
        dropped_lesson = ArchivedStudent.objects.filter(comments='прекратил(а) обучение',
                                                        main_office_id=main_offices.first()).count()
        left_students = ArchivedStudent.objects.all().count()
        paid_students = Student.objects.filter(paid_check='Оплатил', main_office_id=main_offices.first()).count()
        no_paid_students = Student.objects.filter(paid_check='Не оплатил', main_office_id=main_offices.first()).count()
        students_no_paid = Student.objects.filter(paid_check='Не оплатил', main_office_id=main_offices.first())
        other_students = Student.objects.filter(paid_check=None, main_office_id=main_offices.first()).count()
        groups = Group.objects.filter(Q(branch__admin=request.user) | Q(main_office_id__admin=request.user))
        group_data = []

        for group in groups:
            students_count = group.students_id.count()
            group_data.append({
                'group': group,
                'students_count': students_count,
                'course': group.course_id,
            })

        years = Student.objects.all().annotate(year=ExtractYear('joined_date')).values_list(
            'year',
            flat=True).distinct().order_by('year')

        current_year = request.GET.get('year', None)
        if current_year:
            students_per_month = QuantityStudent.objects.filter(joined_date__year=current_year,
                                                                main_office_id__admin=request.user).annotate(
                month=TruncMonth('joined_date')).values('month').annotate(count=Count('id')).order_by('month')
        else:
            students_per_month = QuantityStudent.objects.filter(main_office_id__admin=request.user).annotate(
                month=TruncMonth('joined_date')).values('month').annotate(
                count=Count('id')).order_by('month')

        left_students_per_month = ArchivedStudent.objects.filter(main_office_id__admin=request.user).annotate(
            month=TruncMonth('archived_date')).values('month').annotate(count=Count('id')).order_by('month')

        # Объединение результатов
        month_data = defaultdict(lambda: {'joined': 0, 'left': 0})
        for item in students_per_month:
            month_data[item['month'].strftime('%B')]['joined'] += item['count']

        for item in left_students_per_month:
            month_data[item['month'].strftime('%B')]['left'] += item['count']

        all_months = [datetime.strptime(str(month), "%m").strftime("%B") for month in range(1, 13)]
        students_per_month_full = [(month, month_data[month]['joined'], month_data[month]['left']) for month in
                                   all_months]

        data = {
            'group_data': group_data,
            'total_groups': groups.count(),
            'total_students': Student.objects.filter(main_office_id__admin=request.user).count(),
            'paid_students': paid_students,
            'groups': groups,
            'no_paid_students': no_paid_students,
            'other_students': other_students,
            'students_per_month': students_per_month_full,
            'years': years,
            'current_year': current_year,
            'completed_the_course': completed_the_course,
            'dropped_lesson': dropped_lesson,
            'archived_students': ArchivedStudent.objects.filter(main_office_id__admin=request.user).count(),
            'left_students': left_students,
            'branch_logo': branch_logo,
            'main_offices': main_offices,
            'branches': branches,
            'user': user
        }
        return render(request, 'base.html', data)
    elif request.user.role == 'admin':
        completed_the_course = ArchivedStudent.objects.filter(comments='окончил(а) курс',
                                                              branch=branches.first()).count()
        dropped_lesson = ArchivedStudent.objects.filter(comments='прекратил(а) обучение',
                                                        branch=branches.first()).count()
        left_students = ArchivedStudent.objects.all().count()
        paid_students = Student.objects.filter(paid_check='Оплатил', branch=branches.first()).count()

        no_paid_students = Student.objects.filter(paid_check='Не оплатил', branch=branches.first()).count()
        other_students = Student.objects.filter(paid_check=None, branch=branches.first()).count()
        groups = Group.objects.filter(branch__admin=request.user)
        group_data = []

        for group in groups:
            students_count = group.students_id.count()
            group_data.append({
                'group': group,
                'students_count': students_count,
                'course': group.course_id,
            })

        years = Student.objects.filter(branch__admin=request.user).annotate(
            year=ExtractYear('joined_date')).values_list(
            'year',
            flat=True).distinct().order_by('year')
        current_year = request.GET.get('year', None)
        if current_year:
            students_per_month = QuantityStudent.objects.filter(joined_date__year=current_year,
                                                                branch__admin=request.user).annotate(
                month=TruncMonth('joined_date')).values('month').annotate(count=Count('id')).order_by('month')
        else:
            students_per_month = QuantityStudent.objects.filter(branch__admin=request.user).annotate(
                month=TruncMonth('joined_date')).values('month').annotate(
                count=Count('id')).order_by('month')

        left_students_per_month = ArchivedStudent.objects.filter(branch__admin=request.user).annotate(
            month=TruncMonth('archived_date')).values(
            'month').annotate(count=Count('id')).order_by('month')

        # Объединение результатов
        month_data = defaultdict(lambda: {'joined': 0, 'left': 0})
        for item in students_per_month:
            month_data[item['month'].strftime('%B')]['joined'] += item['count']

        for item in left_students_per_month:
            month_data[item['month'].strftime('%B')]['left'] += item['count']

        all_months = [datetime.strptime(str(month), "%m").strftime("%B") for month in range(1, 13)]
        students_per_month_full = [(month, month_data[month]['joined'], month_data[month]['left']) for month in
                                   all_months]

        data = {
            'group_data': group_data,
            'total_groups': groups.count(),
            'total_students': Student.objects.filter(branch__admin=request.user).count(),
            'paid_students': paid_students,
            'no_paid_students': no_paid_students,
            'other_students': other_students,
            'students_per_month': students_per_month_full,
            'years': years,
            'current_year': current_year,
            'completed_the_course': completed_the_course,
            'dropped_lesson': dropped_lesson,
            'archived_students': ArchivedStudent.objects.filter(branch__admin=request.user).count(),
            'left_students': left_students,
            'branch': Branch.objects.filter(admin_id=request.user.id),
            'branch_logo': branch_logo,
            'main_offices': main_offices,
            'branches': branches,
            'user': user
        }

        return render(request, 'base.html', data)
    return render(request, 'base.html')


@login_required(login_url='/login/')
def archived_groups(request):
    if request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect('all_groups')

    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    branch_logo = Branch.objects.filter(admin_id=user.id)
    selected_main_office_id = request.GET.get('main_office')
    selected_branch_id = request.GET.get('branch')
    arch_groups = ArchivedGroup.objects.all()

    if user.role == 'super admin':
        if selected_main_office_id:
            arch_groups = arch_groups.filter(main_office_id=selected_main_office_id)
        if selected_branch_id:
            arch_groups = arch_groups.filter(branch_id=selected_branch_id)
        if not selected_main_office_id and not selected_branch_id:
            arch_groups = arch_groups.filter(Q(main_office_id__in=main_offices) | Q(branch__in=branches))
    elif user.role == 'admin':
        if selected_branch_id:
            arch_groups = arch_groups.filter(branch_id=selected_branch_id)
        else:
            admin_branches = Branch.objects.filter(admin=user)
            arch_groups = arch_groups.filter(branch__in=admin_branches)

    data = {
        'arch_groups': arch_groups,
        'main_offices': main_offices,
        'branches': branches,
        'selected_main_office_id': selected_main_office_id,
        'selected_branch_id': selected_branch_id,
        'branch_logo': branch_logo
    }
    return render(request, 'groups/archived_group.html', data)


@login_required(login_url='/login/')
def delete_archived_group(request, id_archived_group):
    if request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    archived_group = get_object_or_404(ArchivedGroup, pk=id_archived_group)
    if request.method == 'POST':
        archived_group.delete()
        return redirect('archived_groups')


@login_required(login_url='/login/')
def restore_group(request, group_id):
    if request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    archived_group = get_object_or_404(ArchivedGroup, pk=group_id)
    status_instance = get_object_or_404(Status, name_status='Курс окончен')

    instance_teacher = get_object_or_404(Teacher, id=archived_group.teacher_id.id)
    instance_audience = get_object_or_404(Audience, id=archived_group.audience_id.id)

    restored_group = Group.objects.create(
        name_group=archived_group.name_group,
        start_date=archived_group.start_date,
        end_date=archived_group.end_date,
        teacher_id=instance_teacher,
        audience_id=instance_audience,
        status_group=status_instance,
        main_office_id=archived_group.main_office_id,
        branch=archived_group.branch,
        course_id=archived_group.course_id
    )

    restored_group.students_id.set(archived_group.students_id.all())

    archived_group.delete()

    return redirect('archived_students')


@login_required(login_url='/login/')
def delete_payment(request, payment_id):
    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    branch_logo = Branch.objects.filter(admin_id=user.id)
    if request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'all_groups')
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

    return render(request, 'students/delete_payment.html',
                  {'payment': payment, 'comment_form': comment_form, 'main_offices': main_offices,
                   'branches': branches, 'branch_logo': branch_logo})


@login_required(login_url='/login/')
def archived_payments(request):
    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    archived_payments = ArchivedPayment.objects.all()
    branch_logo = Branch.objects.filter(admin_id=user.id)

    paginator = Paginator(archived_payments, 1)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        'archived_payments': page_obj,
        'main_offices': main_offices,
        'branches': branches,
        'branch_logo': branch_logo
    }
    return render(request, 'students/payment_archive.html', context)


@login_required(login_url='/login/')
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
        if not CustomUser.objects.filter(username=username).exists():
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


@login_required(login_url='/login/')
def sms_temp(request):
    user = request.user
    main_office = MainOffice.objects.filter(admin=user)
    branch = Branch.objects.filter(main_office__in=main_office)
    branch_logo = Branch.objects.filter(admin_id=user.id)

    if request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'all_groups')
    elif request.user.role == 'super admin':
        sms_template = SmsTemplates.objects.filter(main_office_id=main_office.first())
    else:
        sms_template = SmsTemplates.objects.all()

    data = {
        'sms_template': sms_template,
        'main_offices': main_office,
        'branch': branch,
        'branch_logo': branch_logo
    }
    return render(request, 'sms_templates/all_sms_templates.html', data)


@login_required(login_url='/login/')
def add_sms_template(request):
    user = request.user
    main_offices = MainOffice.objects.filter(admin=user)
    branch = Branch.objects.filter(main_office__in=main_offices)
    branch_logo = Branch.objects.filter(admin_id=user.id)
    sms_template_form = SmsTemplateForm()
    if request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'all_groups')
    elif request.user.role == 'admin':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'main_page')
    elif request.user.role == 'super admin':
        if request.method == 'POST':
            sms_template_form = SmsTemplateForm(request.POST, request.FILES)
            if sms_template_form.is_valid():
                sms_form = sms_template_form.save(commit=False)
                sms_form.main_office_id = main_offices.first()
                sms_form.save()
                return redirect('sms_temp')
            else:
                sms_template_form = SmsTemplateForm(request.POST)
    data = {
        'sms_template_form': sms_template_form,
        'user': user,
        'main_offices': main_offices,
        branch: 'branch',
        branch_logo: 'branch_logo'
    }
    return render(request, 'sms_templates/add_sms_template.html', data)


@login_required(login_url='/login/')
def groups_sms(request):
    if request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'all_groups')

    user = request.user
    current_year = datetime.today().year
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    selected_main_office_id = request.GET.get('main_office')
    selected_branch_id = request.GET.get('branch')
    branch_logo = Branch.objects.filter(admin_id=user.id)
    groups = Group.objects.all()
    sms_date = request.POST.get('sms_date')
    if user.role == 'super admin':
        template_sms = SmsTemplates.objects.filter(text_categories='sms для уведомления групп').first()
        if selected_main_office_id:
            groups = groups.filter(main_office_id=selected_main_office_id)
        elif selected_branch_id:
            groups = groups.filter(branch_id=selected_branch_id)
        else:
            groups = groups.filter(Q(main_office_id__in=main_offices) | Q(branch__in=branches))
        if request.method == 'POST':
            selected_groups = request.POST.getlist('selected_groups')
            for group_id in selected_groups:
                group = get_object_or_404(Group, pk=group_id)
                students = group.students_id.all()
                for student in students:
                    phone = student.phone_number_s
                    text = template_sms.text_sms.format(
                        edu_name=student.main_office_id.name_main_office,
                        student_name=f'{student.first_name_s} {student.last_name_s}',
                        date=sms_date,
                    )
                    send_sms(phone, text, request)

    elif user.role == 'admin':
        if selected_branch_id:
            groups = groups.filter(branch_id=selected_branch_id)
            text_sms = SmsTemplates.objects.filter(text_categories='sms для уведомления групп').first()
            if request.method == 'POST':
                selected_groups = request.POST.getlist('selected_groups')
                print(selected_groups)
                for group_id in selected_groups:
                    group = get_object_or_404(Group, pk=group_id)
                    print(group)
                    students = group.students_id.all()
                    for student in students:
                        phone = student.phone_number_s
                        text = text_sms.format(
                            edu_name=student.main_office_id.name_main_office,
                            student_name=student.first_name_s,
                            date=datetime.today(),
                        )
                        send_sms(phone, text, request)
        else:
            admin_branches = Branch.objects.filter(admin=user)
            groups = groups.filter(branch__in=admin_branches)
    data = {
        'groups': groups,
        'current_year': current_year,
        'user': user,
        'main_offices': main_offices,
        'branches': branches,
        'selected_main_office_id': selected_main_office_id,
        'selected_branch_id': selected_branch_id,
        'branch_logo': branch_logo
    }

    return render(request, 'groups/groups_sms.html', data)


def edit_sms_template(request, id_template):
    if request.user.role == 'teacher':
        messages.error(request, 'У вас нет прав доступа.')
        return redirect(
            'all_groups')
    sms_template = get_object_or_404(SmsTemplates, pk=id_template)
    user = request.user
    current_year = datetime.today().year
    main_offices = MainOffice.objects.filter(admin=user)
    branches = Branch.objects.filter(main_office__in=main_offices)
    branch_logo = Branch.objects.filter(admin_id=user.id)

    if request.method == 'POST':
        sms_form = SmsTemplateForm(request.POST, request.FILES, instance=sms_template)
        if sms_form.is_valid():
            sms_form = sms_form.save()
            return redirect('sms_temp')

    else:
        sms_form = SmsTemplateForm(instance=sms_template)
    data = {
        'sms_form': sms_form,
        'current_year': current_year,
        'user': user,
        'main_offices': main_offices,
        'branches': branches,
        'branch_logo': branch_logo

    }
    return render(request, 'sms_templates/edit_sms_template.html', data)
