from django.urls import path

from students_management import views

urlpatterns = [

    # professor
    path('all-professors/', views.get_professor, name='all_professors'),
    path('update-professor/<int:id_professor>/', views.update_professor, name='update_professor'),
    path('delete-professor/<int:id_professor>/', views.delete_professor, name='delete_professor'),
    path('add-professor/', views.add_professor, name='add_professor'),

    # course
    path('all-courses/', views.get_courses, name='all_courses'),
    path('add-course/', views.add_course, name='add_course'),
    path('update-course/<int:id_course>/', views.update_course, name='update_course'),
    path('delete-course/<int:id_course>/', views.delete_course, name='delete_course'),

    # status
    path('all-status/', views.all_status, name='all_status'),
    path('add-status/', views.add_status, name='add_status'),
    path('update-status/<int:id_status>/', views.update_status, name='update_status'),
    path('delete-status/<int:id_status>/', views.delete_status, name='delete_status'),

    # student
    path('all-students/', views.all_students, name='all_students'),
    path('add-students/', views.add_students, name='add_students'),
    path('update-students/<int:id_student>/', views.update_students, name='update_students'),
    path('delete-students/<int:id_student>/', views.delete_students, name='delete_students'),
    path('profile-students/<int:id_student>/', views.profile_students, name='profile_students'),
    path('process-payment/<int:student_id>/', views.process_payment, name='process_payment'),
    path('delete_selected_students/', views.delete_selected_students, name='delete_selected_students'),
    path('archived_students/', views.archived_students, name='archived_students'),
    path('restore_student/<int:student_id>/', views.restore_student, name='restore_student'),

    # audience
    path('all-audience/', views.all_audience, name='all_audience'),
    path('add-audience/', views.add_audience, name='add_audience'),
    path('update-audience/<int:id_audience>/', views.update_audience, name='update_audience'),
    path('delete_audience/<int:id_audience>/', views.delete_audience, name='delete_audience'),

    # group
    path('all-groups/', views.all_groups, name='all_groups'),
    path('add-group/', views.add_group, name='add_group'),
    path('update-group/<int:id_group>/', views.update_group, name='update_group'),
    path('delete-group/<int:id_group>/', views.delete_group, name='delete_group'),
    path('info-group/<int:id_group>/', views.info_group, name='info_group'),

    path('group/<int:group_id>/mark-attendance/', views.mark_attendance, name='mark_attendance'),

]
