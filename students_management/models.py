from datetime import datetime

from django.contrib.auth.models import User, AbstractUser
from django.db import models
from django.urls import reverse




class Branch(models.Model):
    first_name_d = models.CharField(max_length=50)
    last_name_d = models.CharField(max_length=50)
    name = models.CharField("Название филиала", max_length=255)
    address = models.CharField("Адрес", max_length=255)
    phone_number = models.CharField("Телефон", max_length=55)
    logo_branch = models.ImageField(upload_to="logo", verbose_name='Лого филиала')
    short_logo_branch = models.ImageField(upload_to="logo", verbose_name='Короткий логотип филиала')
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_branches',
                              verbose_name="Админ филиала")

    class Meta:
        db_table = 'branch'
        verbose_name = 'Филиал'
        verbose_name_plural = 'Филиалы'
        ordering = ['name']

    def __str__(self):
        return self.name

    def is_admin(self):
        return self.admin


# Create your models here.
class Student(models.Model):
    STATUS_CHOICES = [
        ("Оплатил", "Оплатил"),
        ("Не оплатил", "Не оплатил")
    ]
    first_name_s = models.CharField(max_length=55, verbose_name='Имя студента')
    last_name_s = models.CharField(max_length=55, verbose_name='Фамилия студента')
    phone_number_s = models.CharField(max_length=55, verbose_name='Телефон номер')
    paid_check = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Не оплатил")
    parents_phone_number = models.CharField(max_length=55, verbose_name='Телефон номер родителей')
    joined_date = models.DateField(default=datetime.today, verbose_name='Дата присоединение')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='students', verbose_name="Филиал")

    class Meta:
        db_table = 'student'
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'
        ordering = ['first_name_s']

    def __str__(self):
        return f"{self.first_name_s} {self.last_name_s}"

    def get_absolute_url(self):
        return reverse("update_students", kwargs={"id_student": self.pk})


class Course(models.Model):
    name_course = models.CharField(max_length=55, verbose_name='Имя курсе')
    price_course = models.CharField(max_length=55, verbose_name='Цена курса')
    duration = models.CharField(max_length=55, verbose_name='Длительность курса')
    img_course = models.ImageField(upload_to='course', verbose_name='Фото')
    slug_course = models.CharField(max_length=55)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='courses', verbose_name="Филиал")

    class Meta:
        db_table = 'course'
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['name_course']

    def __str__(self):
        return self.name_course

    def get_absolute_url(self):
        return reverse('update_course', kwargs={'id_course': self.pk})


class Payment(models.Model):
    STATUS_CHOICES = [
        ("наличными", "Наличными"),
        ("click", "Click"),
        ("терминал", "Терминал")
    ]
    method_pay = models.CharField(max_length=55, choices=STATUS_CHOICES, default='', verbose_name='Способ оплаты')
    date_pay = models.DateField(default=datetime.today, verbose_name='Дата оплаты')
    price = models.CharField(max_length=69, default='', verbose_name='Цена')
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Студент')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='payments', verbose_name="Филиал")
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Курс')

    class Meta:
        db_table = 'payment'
        verbose_name = "Оплата"
        verbose_name_plural = 'Оплаты'
        ordering = ('-date_pay',)

    def __str__(self):
        return f"{self.method_pay} {self.date_pay} {self.price} {self.student_id.first_name_s}"


class Audience(models.Model):
    number_audience = models.CharField(max_length=45, verbose_name='Аудитория')
    capacity = models.CharField(max_length=45, verbose_name='Вместимость')
    slug_audience = models.CharField(max_length=45)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='audiences', verbose_name="Филиал")

    class Meta:
        db_table = 'audience'
        verbose_name = 'Аудитория'
        verbose_name_plural = 'Аудитории'
        ordering = ['number_audience']

    def __str__(self):
        return self.number_audience

    def get_absolute_url(self):
        return reverse('update_audience', kwargs={'id_audience': self.pk})


class Status(models.Model):
    name_status = models.CharField(max_length=45, verbose_name='Имя статуса')
    slug_status = models.CharField(max_length=45)

    class Meta:
        db_table = 'status'
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'

    def __str__(self):
        return self.name_status

    def get_absolute_url(self):
        return reverse('update_status', kwargs={'id_status': self.pk})


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=45, verbose_name='Имя')
    last_name = models.CharField(max_length=45, verbose_name='Фамилия')
    phone_number = models.CharField(max_length=45, verbose_name='Номер телефона')
    img_teacher = models.ImageField(upload_to='teacher', verbose_name='Фото учителя')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, verbose_name='Курс')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='teachers', verbose_name="Филиал")

    class Meta:
        db_table = 'teacher'
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'
        ordering = ['last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse('update_professor', kwargs={'id_professor': self.pk})


class Group(models.Model):
    DAYS_CHOICES = [
        ('четные', 'Четные'),
        ('нечетные', 'Нечетные')
    ]
    name_group = models.CharField(max_length=45, verbose_name='Название группы')
    start_date = models.DateField(verbose_name='Дата начала группы', default=datetime.today)
    end_date = models.DateField(verbose_name='Дата завершения группы')
    start_time = models.TimeField(default=datetime.today().time())
    end_time = models.TimeField(default=datetime.today().time())
    lesson_days = models.CharField(choices=DAYS_CHOICES, default='')
    teacher_id = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='Преподаватель')
    audience_id = models.ForeignKey(Audience, on_delete=models.CASCADE, verbose_name='Аудитория')
    students_id = models.ManyToManyField(Student, related_name='students', verbose_name='Студенты', blank=True)
    status_group = models.ForeignKey(Status, on_delete=models.PROTECT, default='', verbose_name='Статус группы')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='groups', verbose_name="Филиал")
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, default='', verbose_name="Курсы")

    class Meta:
        db_table = 'group'
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['status_group']

    def get_absolute_url(self):
        return reverse('update_group', kwargs={'id_group': self.pk})


class Attendance_Status(models.Model):
    name_attendance_status = models.CharField(max_length=45)

    class Meta:
        db_table = 'attendance_status'
        verbose_name = 'Статус посещение'
        verbose_name_plural = 'Статусы посещения'

    def __str__(self):
        return self.name_attendance_status


class Attendance(models.Model):
    date_attendance = models.DateField(verbose_name='Дата пропуска')
    attendance_status = models.ForeignKey(Attendance_Status, on_delete=models.CASCADE, verbose_name='Статус пропуска')
    students_id = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Студент')
    groups_id = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='Группа')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='attendances', verbose_name="Филиал")

    class Meta:
        db_table = 'attendance'
        verbose_name = 'Посещение студента'
        verbose_name_plural = 'Посещения студентов'


class ArchivedStudent(models.Model):
    STATUS_CHOICES = [
        ("окончил(а) курс", "Окончил(а) Курс"),
        ("прекратил(а) обучение", "Прекратил(а) обучение"),
    ]

    first_name_s = models.CharField("Имя", max_length=55)
    last_name_s = models.CharField("Фамилия", max_length=55)
    phone_number_s = models.CharField("Телефон", max_length=55)
    paid_check = models.CharField("Статус оплаты", max_length=20)
    parents_phone_number = models.CharField("Телефон родителей", max_length=55)
    joined_date = models.DateField("Дата присоединения")
    archived_date = models.DateTimeField("Дата архивирования", auto_now_add=True)
    comments = models.CharField(choices=STATUS_CHOICES, max_length=45)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='archived_students',
                               verbose_name="Филиал")

    class Meta:
        db_table = 'archived_student'
        verbose_name = 'Архивированный студент'
        verbose_name_plural = 'Архивированные студенты'
        ordering = ['archived_date']


class ArchivedPayment(models.Model):
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    method_pay = models.CharField("Метод оплаты", max_length=55)
    date_pay = models.DateField("Дата оплаты")
    price = models.CharField("Сумма", max_length=69)
    archived_date = models.DateTimeField("Дата архивирования", auto_now_add=True)
    comments = models.TextField(max_length=100, default='')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='archived_payments',
                               verbose_name="Филиал")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Курс')  # Добавлено поле для курса

    class Meta:
        db_table = 'archived_payment'
        verbose_name = 'Архивированный платеж'
        verbose_name_plural = 'Архивированные платежи'


class ArchivedGroup(models.Model):
    name_group = models.CharField(max_length=45, verbose_name='Название группы')
    start_date = models.DateField(verbose_name='Дата начала группы', default=datetime.today)
    end_date = models.DateField(verbose_name='Дата окончания группы')
    teacher_id = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='Преподаватель')
    audience_id = models.ForeignKey(Audience, on_delete=models.CASCADE, verbose_name='Аудитория')
    students_id = models.ManyToManyField(Student, related_name='archived_groups_students', verbose_name='Студенты',
                                         blank=True)
    status_group = models.ForeignKey(Status, on_delete=models.PROTECT, verbose_name='Статус группы')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='archived_groups', verbose_name="Филиал")
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Курс')
    comments = models.TextField(max_length=100, default='', verbose_name='Комментарии')
    archived_date = models.DateField(verbose_name='Дата архивации', default=datetime.today)

    class Meta:
        db_table = 'archived_group'
        verbose_name = 'Архивированная группа'
        verbose_name_plural = 'Архивированные группы'

    def __str__(self):
        return self.name_group
