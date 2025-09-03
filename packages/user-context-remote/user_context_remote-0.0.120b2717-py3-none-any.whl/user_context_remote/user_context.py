import json
import warnings
from http import HTTPStatus

import requests
from language_remote.lang_code import LangCode
from python_sdk_remote.mini_logger import MiniLogger as logger
from python_sdk_remote.utilities import get_brand_name, get_environment_name, our_get_env
from url_remote import action_name_enum, component_name_enum, entity_name_enum
from url_remote.our_url import OurUrl
from url_remote.api_version_dicts import AUTHENTICATION_API_VERSION_DICT

# TODO Shall we use authentication-remote-python-package and not directly authentication-local-restapi-typescript?

BRAND_NAME = get_brand_name()
ENVIRONMENT_NAME = get_environment_name()
print("Environment name:", ENVIRONMENT_NAME)

# TODO How about using AUTHENTICATION_API_VERSION_DICT per environment_name in url-remote-python-package?
# TODO This should be array in url-remote, right? Please change all of the API_VERSIONs to array
AUTHENTICATION_API_VERSION = AUTHENTICATION_API_VERSION_DICT.get(ENVIRONMENT_NAME) ## [-1]  # noqa E501
print("AUTHENTICATION_API_VERSION:", AUTHENTICATION_API_VERSION)
print("AUTHENTICATION_API_VERSION_DICT[ENVIRONMENT_NAME]:", AUTHENTICATION_API_VERSION_DICT[ENVIRONMENT_NAME])
DEFAULT_LANG_CODE = LangCode.ENGLISH


# MetaClass that dynamically genrates getters & setters.
class GetterSetterGenerator(type):
    def __new__(cls, name: str, bases: tuple, dct: dict) -> type:
        def make_getter(attr: str) -> callable:
            def getter(self) -> any:
                return getattr(self, attr)

            return getter

        for attr in dct.get('__annotations__', {}):
            dct[f'get_{attr}'] = make_getter(attr)

        return super().__new__(cls, name, bases, dct)


# We want to have only one global instance object which is updateable - i.e. when another one login,
#   we should update the existing instance and not create a new one.
global_user = None


# TODO:  Impersonation methot which changes the effective user only upon login (but not the real one)
class UserContext(metaclass=GetterSetterGenerator):
    real_user_id: int = None
    real_profile_id: int = None
    effective_user_id: int = None
    effective_profile_id: int = None
    lang_code_str: str or None = None
    real_first_name: str = None
    real_last_name: str = None
    real_name: str = None
    subscription_id: int = 5  # TODO temp solution, so we can debug

    def __new__(cls, user_identifier: str = None, password: str = None, user_jwt: str = None):
        global global_user
        if not global_user:
            user = super(UserContext, cls).__new__(cls)
        else:
            user = global_user
        user_identifier = user_identifier or our_get_env("PRODUCT_USER_IDENTIFIER")
        password = password or our_get_env("PRODUCT_PASSWORD")
        if not global_user or any(
                [user_identifier != user.__user_identifier, password != user.__password,
                 (user_jwt and user_jwt != user._user_jwt)]):
            user.__login(user_identifier=user_identifier, password=password, user_jwt=user_jwt)
        user.__user_identifier = user_identifier
        user.__password = password
        if user_jwt:  # override _user_jwt defined in __login
            user._user_jwt = user_jwt
        elif "_user_jwt" not in user.__dict__:
            user._user_jwt = None
        global_user = user
        return user

    def __login(self, user_identifier: str = None, password: str = None, user_jwt: str = None) -> None:
        if user_jwt:  # Keep the priority to user_jwt
            authenticate_product_user_response = self.__authenticate_by_user_jwt(user_jwt=user_jwt)
        else:
            authenticate_product_user_response = self.__authenticate_by_user_identification_and_password(
                user_identifier=user_identifier, password=password)
        # TODO logger.info(user_context)
        # TODO error handing to verify user_context is valid
        # Populate the private data members with data we received from Authentication Local REST-API
        # https://github.com/circles-zone/authentication-local-restapi-typescript-serverless-com/edit/dev/auth-restapi-serverless-com/src/services/auth-service/auth-service-impl.ts
        self.__retrieve_and_populate_user_data(authenticate_product_user_response=authenticate_product_user_response)

    @classmethod
    def login_using_user_identification_and_password(cls,
                                                     user_identifier: str | None = None,  # noqa E501
                                                     password: str | None = None):  # noqa E501
        LOGIN_USING_USER_IDENTIFICATION_AND_PASSWORD_METHOD_NAME = "login_using_user_identification_and_password"
        logger.start(LOGIN_USING_USER_IDENTIFICATION_AND_PASSWORD_METHOD_NAME,
                     object={"user_identifier": user_identifier, "password": password})
        user_identifier = user_identifier or our_get_env("PRODUCT_USER_IDENTIFIER")
        password = password or our_get_env("PRODUCT_PASSWORD")
        if not user_identifier or not password:
            # To support cases with no PRODUCT_USER_IDENTIFIER and PRODUCT_PASSWORD in the deployment.
            error_message = "login failed, check PRODUCT_USER_IDENTIFIER and PRODUCT_PASSWORD in .env file"
            logger.error(error_message)
            raise Exception(error_message)
        try:
            user = UserContext.__new__(cls, user_identifier=user_identifier, password=password)
        except Exception as e:
            error_message = "login failed, check PRODUCT_USER_IDENTIFIER and PRODUCT_PASSWORD in .env file"
            logger.exception(error_message, object=e)
            raise Exception(error_message)
        logger.end(LOGIN_USING_USER_IDENTIFICATION_AND_PASSWORD_METHOD_NAME, object={"user": str(user)})
        return user

    @classmethod
    def login_using_user_jwt(cls, user_jwt: str) -> 'UserContext':
        LOGIN_USING_USER_JWT_METHOD_NAME = "login_using_user_jwt"
        logger.start(LOGIN_USING_USER_JWT_METHOD_NAME, object={"user_jwt": user_jwt})
        user = UserContext.__new__(cls, user_jwt=user_jwt)
        if user is None:
            message: str = "login failed with user_jwt=" + user_jwt
            logger.exception(message)
            raise Exception(message)
        logger.end(LOGIN_USING_USER_JWT_METHOD_NAME, object={"user": str(user)})
        return user

    def get_effective_profile_preferred_lang_code_string(self) -> str:
        GET_CURENT_LANG_CODE_STRING_METHOD_NAME = "get_effective_profile_preferred_lang_code"
        logger.start(GET_CURENT_LANG_CODE_STRING_METHOD_NAME)
        lang_code_return_str = self.lang_code_str or DEFAULT_LANG_CODE.value
        logger.end(GET_CURENT_LANG_CODE_STRING_METHOD_NAME, object={"lang_code_string": self.lang_code_str})
        return lang_code_return_str

    def get_effective_profile_preferred_lang_code(self) -> LangCode:
        lang_code = LangCode(self.lang_code_str or DEFAULT_LANG_CODE.value)
        return lang_code

    def get_effective_subscription_id(self) -> int:
        GET_EFFECTIVE_SUBSCRIPTION_ID_METHOD_NAME = "get_effective_subscription_id"
        logger.start(GET_EFFECTIVE_SUBSCRIPTION_ID_METHOD_NAME)
        warnings.warn(
            "Warning: autogenerated getter method is get_subscription_id, please use that method. - WARNING -",
            DeprecationWarning)
        subscription_id = self.subscription_id
        logger.end(GET_EFFECTIVE_SUBSCRIPTION_ID_METHOD_NAME, object={"subscription_id": subscription_id})
        return subscription_id

    def get_user_jwt(self) -> str:
        return self._user_jwt

    def __authenticate_by_user_identification_and_password(
            self, *, user_identifier: str, password: str) -> requests.Response:
        AUTHENTICATE_BY_USER_IDENTIFICATION_AND_PASSWORD_METHOD_NAME = "_authenticate_by_user_identification_and_password"
        logger.start(AUTHENTICATE_BY_USER_IDENTIFICATION_AND_PASSWORD_METHOD_NAME, object={
            "userIdentifier": user_identifier, "password": "***"})
        try:
            authentication_login_enpoint_url = OurUrl.endpoint_url(
                brand_name=BRAND_NAME,
                environment_name=ENVIRONMENT_NAME,
                component_name=component_name_enum.ComponentName.AUTHENTICATION.value,
                entity_name=entity_name_enum.EntityName.AUTH_LOGIN.value,
                version=AUTHENTICATION_API_VERSION_DICT[ENVIRONMENT_NAME],
                action_name=action_name_enum.ActionName.LOGIN.value
            )
            authentication_login_request_dict = {"userIdentifier": user_identifier, "password": password}
            # TOOD Please use get_http_headers() from Python-SDK
            headers = create_return_http_headers()
            authentication_login_response_json = requests.post(
                url=authentication_login_enpoint_url,
                data=json.dumps(authentication_login_request_dict, separators=(",", ":")), headers=headers
            )
            if authentication_login_response_json.status_code != HTTPStatus.OK:
                logger.error(AUTHENTICATE_BY_USER_IDENTIFICATION_AND_PASSWORD_METHOD_NAME +
                             " authentication_login_response_json.status_code != HTTPStatus.OK " + authentication_login_response_json.text)
                raise Exception(authentication_login_response_json.text)
            # Maybe there is no "data"
            logger.end(AUTHENTICATE_BY_USER_IDENTIFICATION_AND_PASSWORD_METHOD_NAME, object={
                "authentication_login_response_json": authentication_login_response_json,
                "authentication_login_response_json.json()": authentication_login_response_json.json()})
            return authentication_login_response_json
        # TODO Catch KeyError: 'data'
        except Exception as exception:
            logger.exception(
                "Error(Exception): user-context-remote-python _authenticate() " + str(exception))
            logger.end(AUTHENTICATE_BY_USER_IDENTIFICATION_AND_PASSWORD_METHOD_NAME)
            raise exception

    def __authenticate_by_user_jwt(self, user_jwt: str) -> requests.Response:
        AUTHENTICATE_BY_USER_JWT_METHOD_NAME = "_authenticate_by_user_jwt"
        logger.start(AUTHENTICATE_BY_USER_JWT_METHOD_NAME,
                     object={"user_jwt": user_jwt})
        authentication_login_validate_user_jwt_url = OurUrl.endpoint_url(
            brand_name=BRAND_NAME,
            environment_name=ENVIRONMENT_NAME,
            component_name=component_name_enum.ComponentName.AUTHENTICATION.value,
            entity_name=entity_name_enum.EntityName.AUTH_LOGIN.value,
            # TODO This should be an array per environment in url-remote, right? - Please fix all of them in url-remote to be array.
            version=AUTHENTICATION_API_VERSION_DICT[ENVIRONMENT_NAME],
            action_name=action_name_enum.ActionName.VALIDATE_USER_JWT.value
        )
        validate_user_jwt_request_dict = {"userJwt": user_jwt}
        headers = create_return_http_headers()
        authentication_login_validate_user_jwt_response = requests.post(
            url=authentication_login_validate_user_jwt_url,
            data=json.dumps(validate_user_jwt_request_dict, separators=(",", ":")), headers=headers
        )
        if authentication_login_validate_user_jwt_response.status_code != HTTPStatus.OK:
            logger.error(
                "user-context-remote-python-package _authenticate_by_user_jwt() authentication_login_validate_user_jwt_response.status_code != HTTPStatus.OK " + authentication_login_validate_user_jwt_response.text)
            # logger.end()
            raise Exception(authentication_login_validate_user_jwt_response.text)
        logger.end(AUTHENTICATE_BY_USER_JWT_METHOD_NAME,
                   object={"authenticate_product_user_response": authentication_login_validate_user_jwt_response})
        return authentication_login_validate_user_jwt_response

    # this private method is being used only in one place
    # TODO authenticate_product_user_response -> authenticate_product_user_response
    def __retrieve_and_populate_user_data(self, authenticate_product_user_response: requests.Response) -> None:
        _GET_USER_DATA_LOGIN_RESPONSE_METHOD_NAME = "get_user_data_login_response"
        # authenticate_product_user_response created in Authentication Local REST-API
        # https://github.com/circles-zone/authentication-local-restapi-typescript-serverless-com/edit/dev/auth-restapi-serverless-com/src/services/auth-service/auth-service-impl.ts
        validate_user_jwt_data_dict = authenticate_product_user_response.json()
        data_dict = validate_user_jwt_data_dict.get('data')
        if "userJwt" in data_dict:
            self._user_jwt = data_dict.get("userJwt")
        first_name = last_name = None
        if not data_dict:
            logger.error(_GET_USER_DATA_LOGIN_RESPONSE_METHOD_NAME + " data from authenticate_product_user_response",
                         object={"authenticate_product_user_response": authenticate_product_user_response.text})
            raise Exception(
                "Can't get data from authenticate_product_user_response: " + authenticate_product_user_response.text)

        if "userDetails" in data_dict:
            # TODO user_details
            user_details: dict = data_dict.get("userDetails")

            if "profileId" in user_details:
                profile_id = int(user_details.get("profileId"))
                self.real_profile_id = profile_id
                self.effective_profile_id = profile_id

            if "userId" in user_details:
                user_id = int(user_details.get("userId"))
                self.effective_user_id = user_id
                self.real_user_id = user_id

            if "profilePreferredLangCode" in user_details:
                lang_code = user_details.get("profilePreferredLangCode")
                self.lang_code_str = lang_code or DEFAULT_LANG_CODE.value
            if "firstName" in user_details:
                first_name = user_details.get("firstName")
                self.real_first_name = first_name

            if "lastName" in user_details:
                last_name = user_details.get("lastName")
                self.real_last_name = last_name

            if "subscriptionId" in user_details:
                subscription_id = user_details.get("subscriptionId")
                self.subscription_id = subscription_id

            if first_name is not None and last_name is not None:
                name = first_name + " " + last_name
            else:
                # If first_name and last_name are not available, use the email as the name
                name = user_details.get("email")

            self.real_name = name

    def get_country_code(self) -> int:  # TODO: temp solution
        return 972

    # Impersonate
    def set_effective_profile(self, profile_id) -> None:
        if self.user_has_admin_role():
            self.effective_profile_id = profile_id
        else:
            raise PermissionError("User does not have the admin role to set effective profile.")

    def set_effective_user(self, user_id) -> None:
        if self.user_has_admin_role():
            self.effective_user_id = user_id
        else:
            raise PermissionError("User does not have the admin role to set effective user.")

    def user_has_admin_role(self) -> bool:
        return "admin" in self.get_user_roles()

    def get_user_roles(self) -> list[str]:
        return self._user_roles

# from #logger_local.#loggerComponentEnum import #loggerComponentEnum
# from #logger_local.#logger import #logger

# USER_CONTEXT_LOCAL_PYTHON_COMPONENT_ID = 197
# USER_CONTEXT_LOCAL_PYTHON_COMPONENT_NAME = "User Context python package"
# DEVELOPER_EMAIL = "idan.a@circ.zone"
# obj = {
#     'component_id': USER_CONTEXT_LOCAL_PYTHON_COMPONENT_ID,
#     'component_name': USER_CONTEXT_LOCAL_PYTHON_COMPONENT_NAME,
#     'component_category': #loggerComponentEnum.ComponentCategory.Code.value,
#     'developer_email': DEVELOPER_EMAIL
# }
# #logger = #logger.create_#logger(object=obj)

# Commented as we get the decoded user_user_jwt from the authentication service and the user-context do not have access to the USER_JWT_SECRET_KEY
# def get_user_json_by_user_user_jwt(self, user_jwt: str) -> None:
#     if user_jwt is None or user_jwt == "":
#         raise Exception(
#             "Your .env PRODUCT_NAME or PRODUCT_PASSWORD is wrong")
#     #logger.start(object={"user_jwt": user_jwt})
#     try:
#         secret_key = our_get_env("JWT_SECRET_KEY")
#         if secret_key is not None:
#             decoded_payload = jwt.decode(user_jwt, secret_key, algorithms=[
#                                          "HS256"], options={"verify_signature": False})
#             self.profile_id = int(decoded_payload.get('profileId'))
#             self.user_id = int(decoded_payload.get('userId'))
#             self.profilePreferredLangCode = decoded_payload.get('profilePreferredLangCode')
#             #logger.end()
#     except jwt.ExpiredSignatureError as e:
#         # Handle token expiration
#         #logger.exception(object=e)
#         print("Error: userJwt has expired.", sys.stderr)
#         #logger.end()
#         raise
#     except jwt.InvalidTokenError as e:
#         # Handle invalid token
#         #logger.exception(object=e)
#         print("Error:Invalid userJwt.", sys.stderr)
#         #logger.end()
#         raise


# We copy just this from sdk_local, so it can import user-context
def create_return_http_headers() -> dict:
    logger.start()
    return_http_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
    }
    logger.end(object={"return_http_headers": return_http_headers})
    return return_http_headers
