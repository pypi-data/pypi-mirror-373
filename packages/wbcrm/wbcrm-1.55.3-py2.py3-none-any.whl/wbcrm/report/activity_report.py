from datetime import datetime
from io import BytesIO

import xlsxwriter
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template.loader import get_template
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.translation import gettext as _
from wbcore.contrib.directory.models import Person
from wbcrm.models import Activity, ActivityType
from xlsxwriter.utility import xl_rowcol_to_cell


def set_cell(worksheet, row, col, value, width_cols, base_format):
    cell = xl_rowcol_to_cell(row, col)
    if value:
        worksheet.write_string(cell, value, base_format)
        if len(value) > width_cols[col]:
            width_cols[col] = len(value)


@shared_task
def create_report_and_send(profile_id, employee_id, start_date=None, end_date=None):
    employee = Person.all_objects.get(id=employee_id)
    profile = Person.all_objects.get(id=profile_id)
    if end_date is None:
        end_date = timezone.now()
    if start_date is None:
        start_date = datetime(year=end_date.year, month=1, day=1, hour=0, minute=0, second=0)

    report = create_report(employee_id, start_date, end_date)

    html = get_template("email/activity_report.html")

    context = {"profile": profile, "employee": employee}
    html_content = html.render(context)

    msg = EmailMultiAlternatives(
        _("Report"), strip_tags(html_content), settings.DEFAULT_FROM_EMAIL, [profile.user_account.email]
    )
    msg.attach_alternative(html_content, "text/html")
    title = _("all")
    if start_date and end_date:
        title = "{}_{}".format(start_date.strftime("%m/%d/%Y-%H:%M:%S"), end_date.strftime("%m/%d/%Y-%H:%M:%S"))
    msg.attach(
        "report_{}_{}.xlsx".format(employee.computed_str, title),
        report.read(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    msg.send()


def create_report(employee, start_date, end_date):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})

    base_format = workbook.add_format({"font_name": "Liberation Sans", "font_size": 10})
    bold_format = workbook.add_format({"font_name": "Liberation Sans", "font_size": 10, "bold": True})
    related_activities = Activity.objects.filter(
        Q(participants__id=employee) | Q(creator__id=employee) | Q(assigned_to__id=employee)
    )
    activities = Activity.get_inrange_activities(related_activities, start_date, end_date)
    # HERE STARTS THE FIRST WORKSHEET
    for type in ActivityType.objects.all():
        width_cols = [5, 5, 16, 8, 7, 11, 12]
        activities_type = activities.filter(type=type.id)
        worksheet = workbook.add_worksheet(type.title)
        worksheet.write_string(0, 0, _("Title"), bold_format)
        worksheet.write_string(0, 1, _("Start"), bold_format)
        worksheet.write_string(0, 2, _("Duration (hours)"), bold_format)
        worksheet.write_string(0, 3, _("Location"), bold_format)
        worksheet.write_string(0, 4, _("Creator"), bold_format)
        worksheet.write_string(0, 5, _("Assigned to"), bold_format)
        worksheet.write_string(0, 6, _("Participants"), bold_format)

        worksheet.write_string(2, 0, _("Total"), bold_format)
        worksheet.write_string(2, 1, str(len(activities_type.all())), bold_format)

        for row, activity in enumerate(activities_type.all(), start=4):
            hours = (activity.period.upper - activity.period.lower).total_seconds() / 3600
            duration = format(hours, ".2f")
            creator = activity.creator
            creator_name = ""
            if creator:
                creator_name = creator.computed_str
            assigned_to = activity.assigned_to
            assigned_to_name = ""
            if assigned_to:
                assigned_to_name = assigned_to.computed_str
            participants = ", ".join([participant.computed_str for participant in activity.participants.all()])

            set_cell(worksheet, row, 0, activity.title, width_cols, base_format)
            set_cell(worksheet, row, 1, f"{activity.period.lower:%d.%m.%Y}", width_cols, base_format)
            set_cell(worksheet, row, 2, duration, width_cols, base_format)
            set_cell(worksheet, row, 2, activity.location, width_cols, base_format)
            set_cell(worksheet, row, 4, creator_name, width_cols, base_format)
            set_cell(worksheet, row, 5, assigned_to_name, width_cols, base_format)
            set_cell(worksheet, row, 6, participants, width_cols, base_format)

        for col, max_width in enumerate(width_cols):
            if max_width > 300:
                max_width = 300
            worksheet.set_column(col, col, max_width)
    workbook.close()
    output.seek(0)
    return output
