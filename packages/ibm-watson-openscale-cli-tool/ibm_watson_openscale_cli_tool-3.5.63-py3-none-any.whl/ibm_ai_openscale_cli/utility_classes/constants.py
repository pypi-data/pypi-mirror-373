# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale_cli.enums import Environment

"""
Constants used throughout the fast-path CLI.
"""

# Stored the environment mapping to the Spark version supported by WML for the Spark model
WML_SPARK_VERSION_SUPPORT_MAPPING = {
    Environment.PUBLIC_CLOUD.value: "spark_3.4",
    Environment.CPD_3_X.value: "spark_2.4",
    Environment.CPD_4_0_0.value: "spark_2.4",
    Environment.CPD_4_0_1.value: "spark_2.4",
    Environment.CPD_4_0_2_PLUS.value: "spark_3.0",
    Environment.CPD_4_0_8_PLUS.value: "spark_3.0",
    Environment.CPD_4_5.value: "spark_3.0",
    Environment.CPD_4_5_1_PLUS.value: "spark_3.2",
    Environment.CPD_4_5_3_PLUS.value: "spark_3.3",
    Environment.CPD_4_7_PLUS.value: "spark_3.3",
    Environment.CPD_4_8_4_PLUS.value: "spark_3.3",
    Environment.CPD_4_8_7_PLUS.value: "spark_3.3",
    Environment.CPD_5_0_1_PLUS.value: "spark_3.4",
    Environment.CPD_5_0_3_PLUS.value: "spark_3.4",
    Environment.CPD_5_1_PLUS.value: "spark_3.4"
}

# Stored the environment to use for the Challenger model
WML_CHALLENGER_ENVIRONMENT_MAPPING = {
    Environment.PUBLIC_CLOUD.value: "py_3.11",
    Environment.CPD_3_X.value: "py_3.7",
    Environment.CPD_4_0_0.value: "py_3.7",
    Environment.CPD_4_0_1.value: "py_3.7",
    Environment.CPD_4_0_2_PLUS.value: "py_3.7",
    Environment.CPD_4_0_8_PLUS.value: "py_3.9",
    Environment.CPD_4_5.value: "py_3.9",
    Environment.CPD_4_5_1_PLUS.value: "py_3.9",
    Environment.CPD_4_5_3_PLUS.value: "py_3.10",
    Environment.CPD_4_7_PLUS.value: "4.7",
    Environment.CPD_4_8_4_PLUS.value: "4.7",
    Environment.CPD_4_8_7_PLUS.value: "4.7",
    Environment.CPD_5_0_1_PLUS.value: "py_3.11",
    Environment.CPD_5_0_3_PLUS.value: "py_3.11",
    Environment.CPD_5_1_PLUS.value: "py_3.11"
}
WML_CHALLENGER_ENVIRONMENT_MAPPING_ZLINUX = {
    Environment.PUBLIC_CLOUD.value: "py_3.11",
    Environment.CPD_3_X.value: "py_3.7",
    Environment.CPD_4_0_0.value: "py_3.7",
    Environment.CPD_4_0_1.value: "py_3.7",
    Environment.CPD_4_0_2_PLUS.value: "py_3.7",
    Environment.CPD_4_0_8_PLUS.value: "py_3.9",
    Environment.CPD_4_5.value: "py_3.9",
    Environment.CPD_4_5_1_PLUS.value: "py_3.9",
    Environment.CPD_4_5_3_PLUS.value: "py_3.10",
    Environment.CPD_4_7_PLUS.value: "py_3.10",
    Environment.CPD_4_8_4_PLUS.value: "py_3.10",
    Environment.CPD_4_8_7_PLUS.value: "py_3.10",
    Environment.CPD_5_0_1_PLUS.value: "py_3.10",
    Environment.CPD_5_0_3_PLUS.value: "py_3.11",
    Environment.CPD_5_1_PLUS.value: "py_3.11"
}

# Software spec mapping for the challenger model
WML_CHALLENGER_SOFTWARE_SPEC_MAPPING = {
    Environment.PUBLIC_CLOUD.value: "runtime-24.1-py3.11",
    Environment.CPD_3_X.value: "default_py3.7",
    Environment.CPD_4_0_0.value: "default_py3.7",
    Environment.CPD_4_0_1.value: "default_py3.7",
    Environment.CPD_4_0_2_PLUS.value: "default_py3.7_opence",
    Environment.CPD_4_0_8_PLUS.value: "runtime-22.1-py3.9",
    Environment.CPD_4_5.value: "runtime-22.1-py3.9",
    Environment.CPD_4_5_1_PLUS.value: "runtime-22.1-py3.9",
    Environment.CPD_4_5_3_PLUS.value: "runtime-22.2-py3.10",
    Environment.CPD_4_7_PLUS.value: "runtime-23.1-py3.10",
    Environment.CPD_4_8_4_PLUS.value: "runtime-23.1-py3.10",
    Environment.CPD_4_8_7_PLUS.value: "runtime-23.1-py3.10",
    Environment.CPD_5_0_1_PLUS.value: "runtime-24.1-py3.11",
    Environment.CPD_5_0_3_PLUS.value: "runtime-24.1-py3.11",
    Environment.CPD_5_1_PLUS.value: "runtime-24.1-py3.11"
}

WML_CHALLENGER_SOFTWARE_SPEC_MAPPING_ZLINUX = {
    Environment.PUBLIC_CLOUD.value: "runtime-24.1-py3.11",
    Environment.CPD_3_X.value: "default_py3.7",
    Environment.CPD_4_0_0.value: "default_py3.7",
    Environment.CPD_4_0_1.value: "default_py3.7",
    Environment.CPD_4_0_2_PLUS.value: "default_py3.7_opence",
    Environment.CPD_4_0_8_PLUS.value: "runtime-22.1-py3.9",
    Environment.CPD_4_5.value: "runtime-22.1-py3.9",
    Environment.CPD_4_5_1_PLUS.value: "runtime-22.1-py3.9",
    Environment.CPD_4_5_3_PLUS.value: "runtime-22.2-py3.10",
    Environment.CPD_4_7_PLUS.value: "runtime-22.2-py3.10",
    Environment.CPD_4_8_4_PLUS.value: "runtime-23.1-py3.10",
    Environment.CPD_4_8_7_PLUS.value: "runtime-23.1-py3.10",
    Environment.CPD_5_0_1_PLUS.value: "runtime-23.1-py3.10",
    Environment.CPD_5_0_3_PLUS.value: "runtime-24.1-py3.11",
    Environment.CPD_5_1_PLUS.value: "runtime-24.1-py3.11"
}

# Stores the environment mapping to the Drift_V2 baseline archive folder
DRIFT_V2_ARCHIVE_ENV_MAPPING = {
    Environment.PUBLIC_CLOUD.value: "public_cloud",
    Environment.CPD_4_7_PLUS.value: "4.7",
    Environment.CPD_4_8_4_PLUS.value: "4.7",
    Environment.CPD_4_8_7_PLUS.value: "4.8.7",
    Environment.CPD_5_0_1_PLUS.value: "5.0.1",
    Environment.CPD_5_0_3_PLUS.value: "5.0.1",
    Environment.CPD_5_1_PLUS.value: "5.1"
}

# Stores the environment mapping to the explain configuration archive folder
EXPLAIN_ARCHIVE_ENV_MAPPING = {
    Environment.PUBLIC_CLOUD.value: "public_cloud",
    Environment.CPD_4_7_PLUS.value: "4.7",
    Environment.CPD_4_8_4_PLUS.value: "4.7",
    Environment.CPD_4_8_7_PLUS.value: "4.7",
    Environment.CPD_5_0_1_PLUS.value: "5.0.1",
    Environment.CPD_5_0_3_PLUS.value: "5.0.1",
    Environment.CPD_5_1_PLUS.value: "5.0.1"
}