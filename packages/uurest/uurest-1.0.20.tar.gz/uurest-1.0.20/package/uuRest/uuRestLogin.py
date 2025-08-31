# from .uuCommon import uuRestMethod
#
#
# class uuRestLogin:
#     """
#     General login class
#     """
#     def __init__(self):
#         """
#         General login class.
#         This class should not be instantiated. Use uuRestLoginEmpty, uuRestLoginByToken, ... instead
#         """
#         self.oidc_url = ""
#         self.token = None
#         self.request_payload = {}
#
#     def get_request_payload(self):
#         raise Exception(f'Not implemented. Please use uuRestLoginGeneral.')
#
#
# class uuRestLoginEmpty(uuRestLogin):
#     """
#     uuRestLoginEmpty is used in case there is no login or Token provided
#     """
#     def __init__(self):
#         """
#         uuRestLoginEmpty is used in case there is no login or Token provided
#         """
#         super().__init__()
#
#
# class uuRestLoginByToken(uuRestLogin):
#     """
#     uuRestLoginByToken is used when the Token is provided
#     """
#     def __init__(self, token: str):
#         """
#         uuRestLoginByToken is used when the Token is provided
#         The developer must assure the token is valid
#         """
#         super().__init__()
#         self.token = token
#
#
# class uuRestLoginGeneral(uuRestLogin):
#     """
#     Login class containing credentials and grant_token_url
#     It automatically renews token if necessary
#     """
#     def __init__(self, oidc_url: str, awid_owner1: str, awid_owner2: str, scope: str = "openid http:// https://", method: uuRestMethod = uuRestMethod.POST):
#         """
#         Login class containing credentials and grant_token_url
#         It automatically renews token if necessary
#         """
#         super().__init__()
#         self.oidc_url = oidc_url
#         self.awid_owner1 = awid_owner1
#         self.awid_owner2 = awid_owner2
#         self.scope = scope
#         self.method = method
#
#     def get_request_payload(self):
#         result = {
#             "grant_type": "password",
#             "username": f"{self.awid_owner1}",
#             "password": f"{self.awid_owner2}",
#             "scope": f'openid {self.scope}'
#         }
#         return result
