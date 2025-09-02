import os
import shutil
import pytest


from nemo_library import NemoLibrary

from tests.testutils import getNL


def test_createOrUpdateRulesByConfigFile():
    nl = getNL()
    nl.createOrUpdateRulesByConfigFile("./tests/NEMO_RULE_CONFIGURATION.xlsx")
