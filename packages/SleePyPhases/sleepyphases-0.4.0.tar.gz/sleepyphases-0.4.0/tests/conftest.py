from phases.commands.test import Test as PhasesTest
from pyPhases.test import TestCase


def pytest_runtest_setup(item):
    phasesTest = PhasesTest({})
    phasesTest.prepareConfig()
    testConfig = phasesTest.loadConfig("tests/config.yml")
    phasesTest.config.update(testConfig)
    project = phasesTest.createProjectFromConfig(phasesTest.config)
    TestCase.project = project
