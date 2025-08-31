# deleted as the validation is done in utilities.our_get_env


# TODO Align with https://github.com/circles-zone/typescript-sdk-remote-typescript-package/edit/dev/typescript-sdk/src/utils/index.ts validateTenantEnvironmentVariables()  # noqa501
def validate_environment_variables():
    """This is done for cross variables validation, as single variables are validated by our_get_env.
    This should be called only once."""

    pass  # No cross validation needed yet

    # TODO: delete the following code

    # validate_brand_name()
    # validate_environment_name()
    # if(os.getenv("PRODUCT_USER_IDENTIFIER") is None):
    #     raise Exception("logger-local-python-package LoggerLocal.py please add Environment Variable called "
    #                     "PRODUCT_USER_IDENTIFIER (instead of PRODUCT_USERNAME)")
    # removed by Idan because it dont has to be in every project
    # if(os.getenv("PRODUCT_PASSWORD") is None):
    #     raise Exception("logger-local-python-package LoggerLocal.py please add Environment Variable called PRODUCT_PASSWORD")
    # validate_logzio_token()
    # validate_google_port_for_authentication()
#
#
# def validate_environment_name():
#     if ENVIRONMENT_NAME is None:
#         raise Exception("logger-local-python-package LoggerLocal.py please add Environment Variable called "
#                         "ENVIRONMENT_NAME=local or play1 (instead of ENVIRONMENT)")
#
#
# def validate_brand_name():
#     if BRAND_NAME is None:
#         raise Exception(
#             "logger-local-python-package LoggerLocal.py please add Environment Variable called BRAND_NAME=Circlez")
#
#
# def validate_logzio_token():
#     if LOGZIO_TOKEN is None:
#         raise Exception("logger-local-python-package LoggerLocal.py please add Environment Variable called"
#                         " LOGZIO_TOKEN=cXNHuVkkffkilnkKzZlWExECRlSKqopE")
#
#
# def validate_google_port_for_authentication():
#     if GOOGLE_PORT_FOR_AUTHENTICATION is None:
#         # The port is 54219 because the authentication url is http://localhost:54219/
#         raise Exception("please add Environment Variable"
#                         " PORT_FOR_AUTHENTICATION=54219 because"
#                         " the authentication url is http://localhost:54219/")
