from logger_local.LoggerComponentEnum import LoggerComponentEnum

# TODO Add SmartDatastoreAttributes Class which includes seller_sales_organization_id, seller_delivery_organization_id, buyer_organization_id, distribution_organization_id, end_customer_organization_id, organization_project_id, seller_case_id, customer_case_id, location_id, knowledge_base, segment_id, vertical_id, industry_id, practice_id, segment_id, vertical_id, business_unit_id, driver_id, distribution_line_id,  (Add it to python-sdk-remote as both Storage, SmartDataStore should use it)  # noqa E501

PYTHON_SDK_REMOTE_COMPONENT_ID = 184
PYTHON_SDK_REMOTE_COMPONENT_NAME = 'python_sdk_remote'

OBJECT_TO_INSERT_CODE = {
    'component_id': PYTHON_SDK_REMOTE_COMPONENT_ID,
    'component_name': PYTHON_SDK_REMOTE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email_address': 'sahar.g@circ.zone'
}

# Move this to the constants_test_python_sdk_remote file (based on the python-package-template)
OBJECT_TO_INSERT_TEST = {
    'component_id': PYTHON_SDK_REMOTE_COMPONENT_ID,
    'component_name': PYTHON_SDK_REMOTE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Unit_Test.value,
    'testing_framework': LoggerComponentEnum.testingFramework.pytest.value,
    'developer_email_address': 'sahar.g@circ.zone'
}
