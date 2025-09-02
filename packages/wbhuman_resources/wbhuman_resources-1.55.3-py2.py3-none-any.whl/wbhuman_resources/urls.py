#!/usr/bin/env python3

from django.urls import include, path
from wbcore.routers import WBCoreRouter

from wbhuman_resources import viewsets

router = WBCoreRouter()


# Calendar viewsets

router.register(
    "defaultdailyperiodrepresentation",
    viewsets.DefaultDailyPeriodRepresentationViewSet,
    basename="defaultdailyperiodrepresentation",
)
router.register(
    "employeeweeklyoffperiodrepresentation",
    viewsets.EmployeeWeeklyOffPeriodsRepresentationViewSet,
    basename="employeeweeklyoffperiodrepresentation",
)
router.register("dayoffrepresentation", viewsets.DayOffRepresentationViewSet, basename="dayoffrepresentation")
router.register(
    "dayoffcalendarrepresentation",
    viewsets.DayOffCalendarRepresentationViewSet,
    basename="dayoffcalendarrepresentation",
)

router.register("dayoffcalendar", viewsets.DayOffCalendarModelViewSet, basename="dayoffcalendar")
router.register("dayoff", viewsets.DayOffModelViewSet, basename="dayoff")

calendar_router = WBCoreRouter()
calendar_router.register("dayoff", viewsets.DayOffDayOffCalendarModelViewSet, basename="calendar-dayoff")
calendar_router.register(
    "defaultperiod", viewsets.DefaultDailyPeriodDayOffCalendarModelViewSet, basename="calendar-defaultperiod"
)

# absence request type router
absencerequesttype_router = WBCoreRouter()
absencerequesttype_router.register(
    "crossbordercountry",
    viewsets.AbsenceRequestCrossBorderCountryModelViewSet,
    basename="absencerequesttype-crossbordercountry",
)


# Employee routers
router.register(
    r"employeehumanresourcerepresentation",
    viewsets.EmployeeHumanResourceRepresentationViewSet,
    basename="employeehumanresourcerepresentation",
)
router.register(r"positionrepresentation", viewsets.PositionRepresentationViewSet, basename="positionrepresentation")
router.register(
    "employeeyearbalancerepresentation",
    viewsets.EmployeeYearBalanceRepresentationViewSet,
    basename="employeeyearbalancerepresentation",
)

router.register(r"employeebalance", viewsets.EmployeeBalanceModelViewSet, basename="employeebalance")
router.register(r"employee", viewsets.EmployeeModelViewSet, basename="employee")
router.register(r"position", viewsets.PositionModelViewSet, basename="position")


employee_router = WBCoreRouter()
employee_router.register(
    r"weeklyoffperiod",
    viewsets.WeeklyOffPeriodEmployeeHumanResourceModelViewSet,
    basename="employee-weeklyoffperiod",
)
employee_router.register(
    r"absence",
    viewsets.AbsenceTypeCountEmployeeModelViewSet,
    basename="employee-absencecount",
)

employee_router.register(
    r"absencerequest",
    viewsets.AbsenceRequestEmployeeHumanResourceModelViewset,
    basename="employee-absencerequest",
)
employee_router.register(
    r"employeeyearbalance",
    viewsets.YearBalanceEmployeeHumanResourceModelViewset,
    basename="employee-employeeyearbalance",
)

# Absence routers
router.register(
    r"absencerequesttyperepresentation",
    viewsets.AbsenceRequestTypeRepresentationViewSet,
    basename="absencerequesttyperepresentation",
)


router.register(r"absenceplanner", viewsets.AbsenceRequestPlanner, basename="absenceplanner")
router.register(r"absencerequest", viewsets.AbsenceRequestModelViewSet)
router.register(r"absencerequesttype", viewsets.AbsenceRequestTypeModelViewSet, basename="absencerequesttype")

absence_request_router = WBCoreRouter()
absence_request_router.register(
    r"periods",
    viewsets.AbsenceRequestPeriodsAbsenceRequestModelViewSet,
    basename="request-periods",
)

# Review Routers
router.register(r"reviewrepresentation", viewsets.ReviewRepresentationViewSet, basename="reviewrepresentation")
router.register(
    r"reviewgrouprepresentation", viewsets.ReviewGroupRepresentationViewSet, basename="reviewgrouprepresentation"
)
router.register(
    r"reviewquestioncategoryrepresentation",
    viewsets.ReviewQuestionCategoryRepresentationViewSet,
    basename="reviewquestioncategoryrepresentation",
)
router.register(
    r"reviewquestionrepresentation",
    viewsets.ReviewQuestionRepresentationViewSet,
    basename="reviewquestionrepresentation",
)

router.register(r"reviewgroup", viewsets.ReviewGroupModelViewSet, basename="reviewgroup")

router.register(r"review", viewsets.ReviewModelViewSet, basename="review")
router.register(r"reviewtemplate", viewsets.ReviewTemplateModelViewSet, basename="reviewtemplate")

router.register(
    r"reviewquestioncategory", viewsets.ReviewQuestionCategoryModelViewSet, basename="reviewquestioncategory"
)

router.register(r"reviewquestion", viewsets.ReviewQuestionModelViewSet, basename="reviewquestion")
router.register(r"reviewanswer", viewsets.ReviewAnswerModelViewSet, basename="reviewanswer")
router.register(r"absencetable", viewsets.AbsenceTablePandasViewSet, basename="absencetable")

reviewgroup_router = WBCoreRouter()
reviewgroup_router.register(r"review", viewsets.ReviewReviewGroupModelViewSet, basename="reviewgroup-review")

review_router = WBCoreRouter()
review_router.register(r"reviewquestion", viewsets.ReviewQuestionReviewModelViewSet, basename="review-reviewquestion")
review_router.register(
    r"reviewquestionnocategory",
    viewsets.ReviewQuestionReviewNoCategoryModelViewSet,
    basename="review-reviewquestionnocategory",
)
review_router.register(
    r"reviewanswerquestionnocategory",
    viewsets.ReviewAnswerReviewNoCategoryModelViewSet,
    basename="review-reviewanswerquestionnocategory",
)


review_category_router = WBCoreRouter()
review_category_router.register(
    r"reviewquestioncategory",
    viewsets.ReviewQuestionReviewCategoryModelViewSet,
    basename="review-reviewquestioncategory",
)
review_category_router.register(
    r"reviewanswerquestioncategory",
    viewsets.ReviewAnswerReviewQuestionCategoryModelViewSet,
    basename="review-reviewanswerquestioncategory",
)

review_question_category_router = WBCoreRouter()
review_question_category_router.register(
    r"reviewquestion",
    viewsets.ReviewQuestionReviewQuestionCategoryModelViewSet,
    basename="reviewquestioncategory-reviewquestion",
)

# KPI routers
router.register(r"kpi", viewsets.KPIModelViewSet, basename="kpi")
router.register(r"kpirepresentation", viewsets.KPIRepresentationViewSet, basename="kpirepresentation")
router.register(
    r"evaluationrepresentation", viewsets.EvaluationRepresentationViewSet, basename="evaluationrepresentation"
)

kpi_router = WBCoreRouter()

kpi_router.register(
    r"evaluation",
    viewsets.KPIEvaluationModelViewSet,
    basename="kpi-evaluation",
)
kpi_router.register(r"evaluationgraph", viewsets.EvaluationGraphChartViewset, basename="kpi-evaluationgraph")


# Review pandas views
router.register("reviewprogress", viewsets.ReviewProgressPandasViewSet, basename="reviewprogress")
router.register("kpievaluationpandas", viewsets.KPIEvaluationPandasViewSet, basename="kpievaluationpandas")
review_router.register(r"progress", viewsets.ReviewProgressReviewPandasViewSet, basename="review-progress")
review_router.register(
    r"reviewanswerpandasview", viewsets.ReviewAnswerReviewPandasViewSet, basename="review-reviewanswerpandasview"
)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "absencerequesttype/<int:absencerequesttype_id>/",
        include(absencerequesttype_router.urls),
    ),
    path(
        "employee/<int:employee_id>/",
        include(employee_router.urls),
    ),
    path(
        "request/<int:request_id>/",
        include(absence_request_router.urls),
    ),
    path(
        "calendar/<int:calendar_id>/",
        include(calendar_router.urls),
    ),
    path("reviewgroup/<int:review_group_id>/", include(reviewgroup_router.urls)),
    path("review/<int:review_id>/", include(review_router.urls)),
    path("review/<int:review_id>/category/<int:category_id>/", include(review_category_router.urls)),
    path("reviewquestioncategory/<int:category_id>/", include(review_question_category_router.urls)),
    path("kpi/<int:kpi_id>/", include(kpi_router.urls)),
]
