"""Top-level package for SmartModels.


Recommended design steps:

1. [ ] write a minimal description of the project goals and possible use cases (README.rst)
2. [ ] define a first version of the data models needed to support such logic (models/*.py)
3. [ ] define the first use cases related to model consistency (docs/use_cases.md)
4. [ ] define the common helpers that will be necessary for these use cases
    4.1 [ ] random synthetic data that will feed pytest cases and FastAPI examples
    4.2 [ ] write down some test cases (tests/test__model_validations.py)
            for verifying pydantic models allowing use of `make ptw` from this stage.

5. [ ] define the use cases related to business logic (docs/use_cases.md)
    5.1. [ ] extend use cases based on (1)

6. [ ] define the use cases skeleton
    6.1 [ ] skeleton of business logic (logic/*.py), but not coding yet.
    6.2 [ ] skeleton of test cases  (tests/test__*.py), but not coding yet.
    6.3 [ ] review and check main concerns detection (TDD)

7. [ ] define the primary abstract ports to allow incoming interaction (ports/*.py)
8. [ ] implement primary ports: cli and/or rest api
    8.1 [ ] use make docker-run to have a instant feedback when code is broken from API perspective
    8.2 [ ] use make ptw to have a instant feedback when code is broken from CLI perspective

9. [ ] define the secondary abstract ports to allow external interaction (ports/*.py)
10. [ ] implement secondary ports (i.e. storage/*.py)
11. [ ] define test cases (tests/*.py) and get main
12. [ ] implement automatic test cases

"""

__author__ = """Asterio Gonzalez"""
__email__ = "asterio.gonzalez@gmail.com"
__version__ = "0.1.334"
