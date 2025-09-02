from __future__ import absolute_import, unicode_literals

from datetime import date, datetime, timedelta
from io import BytesIO

import pandas as pd
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template.loader import get_template
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from dynamic_preferences.registries import global_preferences_registry
from wbcore.contrib.notifications.dispatch import send_notification
from wbcore.utils.date import current_month_date_end
from wbcore.utils.html import convert_html2text

from wbhuman_resources.models import KPI, DayOffCalendar, EmployeeHumanResource, Review

from .models.preferences import get_previous_year_balance_expiration_date


@shared_task
def create_future_public_holiday(today: date | None = None, forecast_year: int = 5):
    if not today:
        today = date.today()
    for calendar in DayOffCalendar.objects.all():
        for year in range(today.year, today.year + forecast_year):
            calendar.create_public_holidays(year)


@shared_task
def daily_birthday(today=None):
    """
    Cron task supposed to be ran every day. Check and notify employee about a colleague's birthday.
    """
    day = "today"
    if not today:
        # Notify employee the day before
        today = datetime.today() + timedelta(days=1)
        day = "tomorrow"
    for birthday_employee in EmployeeHumanResource.active_internal_employees.filter(
        Q(profile__birthday__day=today.day) & Q(profile__birthday__month=today.month)
    ).all():
        for employee in EmployeeHumanResource.active_internal_employees.exclude(id=birthday_employee.id):
            send_notification(
                code="wbhuman_resources.employeehumanresource.birthday",
                title=_("{} {}'s birthday is {}!").format(
                    birthday_employee.profile.first_name, birthday_employee.profile.last_name, day
                ),
                body=_("Wish her/him a happy birthday!"),
                user=employee.profile.user_account,
            )


@shared_task
def assign_balance(today=None):
    """
    Yearly periodic cron tasks that increase for an employee
    """
    if not today:
        today = datetime.now().date()

    for employee in EmployeeHumanResource.active_internal_employees.all():
        [start_period, end_period] = EmployeeHumanResource.ExtraDaysBalanceFrequency[
            employee.extra_days_frequency
        ].get_date_range(today)
        employee.assign_vacation_allowance_from_range(start_period.date(), end_period.date())


@shared_task
def check_and_warn_user_with_previous_year_available_balance(year=None):
    """
    When this task run, it will send a reminder Notification to user with still available balance for the previous year
    """
    if not year:
        year = date.today().year

    for employee in EmployeeHumanResource.active_internal_employees.all():
        previous_year_balance = employee.get_or_create_balance(year - 1)[0]
        if (previous_year_remaining_days := previous_year_balance.total_vacation_hourly_balance) > 0:
            send_notification(
                code="wbhuman_resources.employeehumanresource.vacation",
                title=_("You still have {} hours of vacation to take from {}").format(
                    previous_year_remaining_days, year - 1
                ),
                body=_(
                    "Please take vacation from now to {:%d.%m.%Y} (excluded). Your balance will not be available after that date"
                ).format(get_previous_year_balance_expiration_date(year=year)),
                user=employee.profile.user_account,
            )


@shared_task
def send_mail_to_accounting():
    global_preferences = global_preferences_registry.manager()
    accounting_company_emails = list(
        filter(None, global_preferences["wbhuman_resources__accounting_company_emails"].split(";"))
    )
    cc_emails = list(EmployeeHumanResource.get_administrators().values_list("email", flat=True))

    end_of_month = current_month_date_end()

    output = BytesIO()
    EmployeeHumanResource.get_end_of_month_employee_balance_report_df(
        EmployeeHumanResource.active_internal_employees.all(), end_of_month
    ).to_excel(output, engine="xlsxwriter", index=False)

    html = get_template("notifications/email_template.html")

    notification = {
        "message": gettext(
            "Please find the vacation days balance valid to the end of the month as attached excel file"
        ),
        "title": gettext("Vacation balance summary at {:%d.%m.%Y}").format(end_of_month),
    }
    html_content = html.render({"notification": notification})
    mail_text = convert_html2text(html_content)
    msg = EmailMultiAlternatives(
        gettext("Vacation Report {:%d.%m.%Y}").format(end_of_month),
        body=mail_text,
        from_email=global_preferences["wbhuman_resources__default_from_email_address"],
        to=accounting_company_emails,
        cc=cc_emails,
    )
    msg.attach_alternative(html_content, "text/html")
    output.seek(0)
    msg.attach(
        "vacation_report_{:%m-%d-%Y}.xlsx".format(end_of_month),
        output.read(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    msg.send()


@shared_task
def daily_automatic_application_deadline():
    for review in Review.objects.filter(
        Q(status=Review.Status.FILL_IN_REVIEW) & Q(review_deadline__lte=datetime.now().date())
    ):
        review.save()

    week = datetime.now().date() - timedelta(days=7)
    for review in Review.objects.filter(Q(status=Review.Status.FILL_IN_REVIEW) & Q(review_deadline=week)):
        persons = [review.reviewee, review.reviewer]
        for person in persons:
            if hasattr(person, "user_account"):
                msg = gettext("Dear {} {}, <p>you only have one more week to complete the review.</p>").format(
                    person.first_name, person.last_name
                )
                review.send_review_notification(
                    title=gettext("Stage 2: Fill in review - {}").format(str(review)),
                    message=msg,
                    recipient=person.user_account,
                )

    # Daily notification
    for review in Review.objects.filter(
        Q(status=Review.Status.FILL_IN_REVIEW) & Q(review_deadline=datetime.now().date() - timedelta(days=1))
    ):
        persons = [review.reviewee, review.reviewer]
        for person in persons:
            if hasattr(person, "user_account"):
                msg = gettext("Dear {} {}, <p>you only have one more day to complete the review.</p>").format(
                    person.first_name, person.last_name
                )

                review.send_review_notification(
                    title=gettext("Stage 2: Fill in review - {}").format(str(review)),
                    message=msg,
                    recipient=person.user_account,
                )


@shared_task
def periodic_updating_kpi_task(kpi_id=[], start=None, end=None):
    intervals = {elt.name: KPI.Interval.get_frequence_correspondance(elt.name) for elt in KPI.Interval}
    for key, value in intervals.items():
        kpis = (
            KPI.objects.filter(id__in=kpi_id, evaluated_intervals=key)
            if kpi_id
            else KPI.objects.filter(evaluated_intervals=key, is_active=True)
        )
        for kpi in kpis:
            if not start:
                start = kpi.period.lower
            if not end:
                end = kpi.period.upper
            for date_evaluation in pd.date_range(start=start, end=end, freq=value):
                kpi.generate_evaluation(date_evaluation.date())
