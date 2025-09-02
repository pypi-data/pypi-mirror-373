import os

from rara_tools.task_reporter import TaskReporter

REPORTER = TaskReporter(
    os.getenv("TASK_REPORTER_URL", "http://localhost:8000/api/v1/"),
    os.getenv("TASK_REPORTER_TOKEN", "")
)

# TODO: write tests when Core API is ready.

# def test_api_health():
#     """Tests TaskReporter's health check.
#     """
#     # normal response
#     response = REPORTER.check()
#     assert response is True
#     # wrong URL
#     response = TaskReporter("http://whatever.com", "xxx").check()
#     assert response is False

# def test_api_report():
#     """Tests reporting functionaly of the class.
#     """
#     data_to_patch = {
#         "number_of_pages": 10,
#         "elasticID": "foobar"
#     }
#     task_id = 1
#     response = REPORTER.report_results(data_to_patch, task_id)
#     print(response)
