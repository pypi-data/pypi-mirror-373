# Copyright 2016 Game Server Services, Inc. or its affiliates. All Rights
# Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

from __future__ import annotations

from .model import *


class CreateAccountRequest(core.Gs2Request):

    context_stack: str = None
    email: str = None
    full_name: str = None
    company_name: str = None
    password: str = None
    lang: str = None

    def with_email(self, email: str) -> CreateAccountRequest:
        self.email = email
        return self

    def with_full_name(self, full_name: str) -> CreateAccountRequest:
        self.full_name = full_name
        return self

    def with_company_name(self, company_name: str) -> CreateAccountRequest:
        self.company_name = company_name
        return self

    def with_password(self, password: str) -> CreateAccountRequest:
        self.password = password
        return self

    def with_lang(self, lang: str) -> CreateAccountRequest:
        self.lang = lang
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateAccountRequest]:
        if data is None:
            return None
        return CreateAccountRequest()\
            .with_email(data.get('email'))\
            .with_full_name(data.get('fullName'))\
            .with_company_name(data.get('companyName'))\
            .with_password(data.get('password'))\
            .with_lang(data.get('lang'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "email": self.email,
            "fullName": self.full_name,
            "companyName": self.company_name,
            "password": self.password,
            "lang": self.lang,
        }


class VerifyRequest(core.Gs2Request):

    context_stack: str = None
    verify_token: str = None

    def with_verify_token(self, verify_token: str) -> VerifyRequest:
        self.verify_token = verify_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyRequest]:
        if data is None:
            return None
        return VerifyRequest()\
            .with_verify_token(data.get('verifyToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verifyToken": self.verify_token,
        }


class SignInRequest(core.Gs2Request):

    context_stack: str = None
    email: str = None
    password: str = None
    otp: str = None

    def with_email(self, email: str) -> SignInRequest:
        self.email = email
        return self

    def with_password(self, password: str) -> SignInRequest:
        self.password = password
        return self

    def with_otp(self, otp: str) -> SignInRequest:
        self.otp = otp
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SignInRequest]:
        if data is None:
            return None
        return SignInRequest()\
            .with_email(data.get('email'))\
            .with_password(data.get('password'))\
            .with_otp(data.get('otp'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "email": self.email,
            "password": self.password,
            "otp": self.otp,
        }


class ForgetRequest(core.Gs2Request):

    context_stack: str = None
    email: str = None
    lang: str = None

    def with_email(self, email: str) -> ForgetRequest:
        self.email = email
        return self

    def with_lang(self, lang: str) -> ForgetRequest:
        self.lang = lang
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ForgetRequest]:
        if data is None:
            return None
        return ForgetRequest()\
            .with_email(data.get('email'))\
            .with_lang(data.get('lang'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "email": self.email,
            "lang": self.lang,
        }


class IssuePasswordRequest(core.Gs2Request):

    context_stack: str = None
    issue_password_token: str = None

    def with_issue_password_token(self, issue_password_token: str) -> IssuePasswordRequest:
        self.issue_password_token = issue_password_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[IssuePasswordRequest]:
        if data is None:
            return None
        return IssuePasswordRequest()\
            .with_issue_password_token(data.get('issuePasswordToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issuePasswordToken": self.issue_password_token,
        }


class UpdateAccountRequest(core.Gs2Request):

    context_stack: str = None
    email: str = None
    full_name: str = None
    company_name: str = None
    password: str = None
    account_token: str = None

    def with_email(self, email: str) -> UpdateAccountRequest:
        self.email = email
        return self

    def with_full_name(self, full_name: str) -> UpdateAccountRequest:
        self.full_name = full_name
        return self

    def with_company_name(self, company_name: str) -> UpdateAccountRequest:
        self.company_name = company_name
        return self

    def with_password(self, password: str) -> UpdateAccountRequest:
        self.password = password
        return self

    def with_account_token(self, account_token: str) -> UpdateAccountRequest:
        self.account_token = account_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateAccountRequest]:
        if data is None:
            return None
        return UpdateAccountRequest()\
            .with_email(data.get('email'))\
            .with_full_name(data.get('fullName'))\
            .with_company_name(data.get('companyName'))\
            .with_password(data.get('password'))\
            .with_account_token(data.get('accountToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "email": self.email,
            "fullName": self.full_name,
            "companyName": self.company_name,
            "password": self.password,
            "accountToken": self.account_token,
        }


class EnableMfaRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None

    def with_account_token(self, account_token: str) -> EnableMfaRequest:
        self.account_token = account_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[EnableMfaRequest]:
        if data is None:
            return None
        return EnableMfaRequest()\
            .with_account_token(data.get('accountToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
        }


class ChallengeMfaRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    passcode: str = None

    def with_account_token(self, account_token: str) -> ChallengeMfaRequest:
        self.account_token = account_token
        return self

    def with_passcode(self, passcode: str) -> ChallengeMfaRequest:
        self.passcode = passcode
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ChallengeMfaRequest]:
        if data is None:
            return None
        return ChallengeMfaRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_passcode(data.get('passcode'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "passcode": self.passcode,
        }


class DisableMfaRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None

    def with_account_token(self, account_token: str) -> DisableMfaRequest:
        self.account_token = account_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DisableMfaRequest]:
        if data is None:
            return None
        return DisableMfaRequest()\
            .with_account_token(data.get('accountToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
        }


class DeleteAccountRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None

    def with_account_token(self, account_token: str) -> DeleteAccountRequest:
        self.account_token = account_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteAccountRequest]:
        if data is None:
            return None
        return DeleteAccountRequest()\
            .with_account_token(data.get('accountToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
        }


class DescribeProjectsRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    page_token: str = None
    limit: int = None

    def with_account_token(self, account_token: str) -> DescribeProjectsRequest:
        self.account_token = account_token
        return self

    def with_page_token(self, page_token: str) -> DescribeProjectsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeProjectsRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeProjectsRequest]:
        if data is None:
            return None
        return DescribeProjectsRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateProjectRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    name: str = None
    description: str = None
    plan: str = None
    currency: str = None
    activate_region_name: str = None
    billing_method_name: str = None
    enable_event_bridge: str = None
    event_bridge_aws_account_id: str = None
    event_bridge_aws_region: str = None

    def with_account_token(self, account_token: str) -> CreateProjectRequest:
        self.account_token = account_token
        return self

    def with_name(self, name: str) -> CreateProjectRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateProjectRequest:
        self.description = description
        return self

    def with_plan(self, plan: str) -> CreateProjectRequest:
        self.plan = plan
        return self

    def with_currency(self, currency: str) -> CreateProjectRequest:
        self.currency = currency
        return self

    def with_activate_region_name(self, activate_region_name: str) -> CreateProjectRequest:
        self.activate_region_name = activate_region_name
        return self

    def with_billing_method_name(self, billing_method_name: str) -> CreateProjectRequest:
        self.billing_method_name = billing_method_name
        return self

    def with_enable_event_bridge(self, enable_event_bridge: str) -> CreateProjectRequest:
        self.enable_event_bridge = enable_event_bridge
        return self

    def with_event_bridge_aws_account_id(self, event_bridge_aws_account_id: str) -> CreateProjectRequest:
        self.event_bridge_aws_account_id = event_bridge_aws_account_id
        return self

    def with_event_bridge_aws_region(self, event_bridge_aws_region: str) -> CreateProjectRequest:
        self.event_bridge_aws_region = event_bridge_aws_region
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateProjectRequest]:
        if data is None:
            return None
        return CreateProjectRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_plan(data.get('plan'))\
            .with_currency(data.get('currency'))\
            .with_activate_region_name(data.get('activateRegionName'))\
            .with_billing_method_name(data.get('billingMethodName'))\
            .with_enable_event_bridge(data.get('enableEventBridge'))\
            .with_event_bridge_aws_account_id(data.get('eventBridgeAwsAccountId'))\
            .with_event_bridge_aws_region(data.get('eventBridgeAwsRegion'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "name": self.name,
            "description": self.description,
            "plan": self.plan,
            "currency": self.currency,
            "activateRegionName": self.activate_region_name,
            "billingMethodName": self.billing_method_name,
            "enableEventBridge": self.enable_event_bridge,
            "eventBridgeAwsAccountId": self.event_bridge_aws_account_id,
            "eventBridgeAwsRegion": self.event_bridge_aws_region,
        }


class GetProjectRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    project_name: str = None

    def with_account_token(self, account_token: str) -> GetProjectRequest:
        self.account_token = account_token
        return self

    def with_project_name(self, project_name: str) -> GetProjectRequest:
        self.project_name = project_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetProjectRequest]:
        if data is None:
            return None
        return GetProjectRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_project_name(data.get('projectName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "projectName": self.project_name,
        }


class GetProjectTokenRequest(core.Gs2Request):

    context_stack: str = None
    project_name: str = None
    account_token: str = None

    def with_project_name(self, project_name: str) -> GetProjectTokenRequest:
        self.project_name = project_name
        return self

    def with_account_token(self, account_token: str) -> GetProjectTokenRequest:
        self.account_token = account_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetProjectTokenRequest]:
        if data is None:
            return None
        return GetProjectTokenRequest()\
            .with_project_name(data.get('projectName'))\
            .with_account_token(data.get('accountToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "projectName": self.project_name,
            "accountToken": self.account_token,
        }


class GetProjectTokenByIdentifierRequest(core.Gs2Request):

    context_stack: str = None
    account_name: str = None
    project_name: str = None
    user_name: str = None
    password: str = None
    otp: str = None

    def with_account_name(self, account_name: str) -> GetProjectTokenByIdentifierRequest:
        self.account_name = account_name
        return self

    def with_project_name(self, project_name: str) -> GetProjectTokenByIdentifierRequest:
        self.project_name = project_name
        return self

    def with_user_name(self, user_name: str) -> GetProjectTokenByIdentifierRequest:
        self.user_name = user_name
        return self

    def with_password(self, password: str) -> GetProjectTokenByIdentifierRequest:
        self.password = password
        return self

    def with_otp(self, otp: str) -> GetProjectTokenByIdentifierRequest:
        self.otp = otp
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetProjectTokenByIdentifierRequest]:
        if data is None:
            return None
        return GetProjectTokenByIdentifierRequest()\
            .with_account_name(data.get('accountName'))\
            .with_project_name(data.get('projectName'))\
            .with_user_name(data.get('userName'))\
            .with_password(data.get('password'))\
            .with_otp(data.get('otp'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountName": self.account_name,
            "projectName": self.project_name,
            "userName": self.user_name,
            "password": self.password,
            "otp": self.otp,
        }


class UpdateProjectRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    project_name: str = None
    description: str = None
    plan: str = None
    billing_method_name: str = None
    enable_event_bridge: str = None
    event_bridge_aws_account_id: str = None
    event_bridge_aws_region: str = None

    def with_account_token(self, account_token: str) -> UpdateProjectRequest:
        self.account_token = account_token
        return self

    def with_project_name(self, project_name: str) -> UpdateProjectRequest:
        self.project_name = project_name
        return self

    def with_description(self, description: str) -> UpdateProjectRequest:
        self.description = description
        return self

    def with_plan(self, plan: str) -> UpdateProjectRequest:
        self.plan = plan
        return self

    def with_billing_method_name(self, billing_method_name: str) -> UpdateProjectRequest:
        self.billing_method_name = billing_method_name
        return self

    def with_enable_event_bridge(self, enable_event_bridge: str) -> UpdateProjectRequest:
        self.enable_event_bridge = enable_event_bridge
        return self

    def with_event_bridge_aws_account_id(self, event_bridge_aws_account_id: str) -> UpdateProjectRequest:
        self.event_bridge_aws_account_id = event_bridge_aws_account_id
        return self

    def with_event_bridge_aws_region(self, event_bridge_aws_region: str) -> UpdateProjectRequest:
        self.event_bridge_aws_region = event_bridge_aws_region
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateProjectRequest]:
        if data is None:
            return None
        return UpdateProjectRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_project_name(data.get('projectName'))\
            .with_description(data.get('description'))\
            .with_plan(data.get('plan'))\
            .with_billing_method_name(data.get('billingMethodName'))\
            .with_enable_event_bridge(data.get('enableEventBridge'))\
            .with_event_bridge_aws_account_id(data.get('eventBridgeAwsAccountId'))\
            .with_event_bridge_aws_region(data.get('eventBridgeAwsRegion'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "projectName": self.project_name,
            "description": self.description,
            "plan": self.plan,
            "billingMethodName": self.billing_method_name,
            "enableEventBridge": self.enable_event_bridge,
            "eventBridgeAwsAccountId": self.event_bridge_aws_account_id,
            "eventBridgeAwsRegion": self.event_bridge_aws_region,
        }


class ActivateRegionRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    project_name: str = None
    region_name: str = None

    def with_account_token(self, account_token: str) -> ActivateRegionRequest:
        self.account_token = account_token
        return self

    def with_project_name(self, project_name: str) -> ActivateRegionRequest:
        self.project_name = project_name
        return self

    def with_region_name(self, region_name: str) -> ActivateRegionRequest:
        self.region_name = region_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ActivateRegionRequest]:
        if data is None:
            return None
        return ActivateRegionRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_project_name(data.get('projectName'))\
            .with_region_name(data.get('regionName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "projectName": self.project_name,
            "regionName": self.region_name,
        }


class WaitActivateRegionRequest(core.Gs2Request):

    context_stack: str = None
    project_name: str = None
    region_name: str = None

    def with_project_name(self, project_name: str) -> WaitActivateRegionRequest:
        self.project_name = project_name
        return self

    def with_region_name(self, region_name: str) -> WaitActivateRegionRequest:
        self.region_name = region_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[WaitActivateRegionRequest]:
        if data is None:
            return None
        return WaitActivateRegionRequest()\
            .with_project_name(data.get('projectName'))\
            .with_region_name(data.get('regionName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "projectName": self.project_name,
            "regionName": self.region_name,
        }


class DeleteProjectRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    project_name: str = None

    def with_account_token(self, account_token: str) -> DeleteProjectRequest:
        self.account_token = account_token
        return self

    def with_project_name(self, project_name: str) -> DeleteProjectRequest:
        self.project_name = project_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteProjectRequest]:
        if data is None:
            return None
        return DeleteProjectRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_project_name(data.get('projectName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "projectName": self.project_name,
        }


class DescribeBillingMethodsRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    page_token: str = None
    limit: int = None

    def with_account_token(self, account_token: str) -> DescribeBillingMethodsRequest:
        self.account_token = account_token
        return self

    def with_page_token(self, page_token: str) -> DescribeBillingMethodsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeBillingMethodsRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeBillingMethodsRequest]:
        if data is None:
            return None
        return DescribeBillingMethodsRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateBillingMethodRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    description: str = None
    method_type: str = None
    card_customer_id: str = None
    partner_id: str = None

    def with_account_token(self, account_token: str) -> CreateBillingMethodRequest:
        self.account_token = account_token
        return self

    def with_description(self, description: str) -> CreateBillingMethodRequest:
        self.description = description
        return self

    def with_method_type(self, method_type: str) -> CreateBillingMethodRequest:
        self.method_type = method_type
        return self

    def with_card_customer_id(self, card_customer_id: str) -> CreateBillingMethodRequest:
        self.card_customer_id = card_customer_id
        return self

    def with_partner_id(self, partner_id: str) -> CreateBillingMethodRequest:
        self.partner_id = partner_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateBillingMethodRequest]:
        if data is None:
            return None
        return CreateBillingMethodRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_description(data.get('description'))\
            .with_method_type(data.get('methodType'))\
            .with_card_customer_id(data.get('cardCustomerId'))\
            .with_partner_id(data.get('partnerId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "description": self.description,
            "methodType": self.method_type,
            "cardCustomerId": self.card_customer_id,
            "partnerId": self.partner_id,
        }


class GetBillingMethodRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    billing_method_name: str = None

    def with_account_token(self, account_token: str) -> GetBillingMethodRequest:
        self.account_token = account_token
        return self

    def with_billing_method_name(self, billing_method_name: str) -> GetBillingMethodRequest:
        self.billing_method_name = billing_method_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetBillingMethodRequest]:
        if data is None:
            return None
        return GetBillingMethodRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_billing_method_name(data.get('billingMethodName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "billingMethodName": self.billing_method_name,
        }


class UpdateBillingMethodRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    billing_method_name: str = None
    description: str = None

    def with_account_token(self, account_token: str) -> UpdateBillingMethodRequest:
        self.account_token = account_token
        return self

    def with_billing_method_name(self, billing_method_name: str) -> UpdateBillingMethodRequest:
        self.billing_method_name = billing_method_name
        return self

    def with_description(self, description: str) -> UpdateBillingMethodRequest:
        self.description = description
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateBillingMethodRequest]:
        if data is None:
            return None
        return UpdateBillingMethodRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_billing_method_name(data.get('billingMethodName'))\
            .with_description(data.get('description'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "billingMethodName": self.billing_method_name,
            "description": self.description,
        }


class DeleteBillingMethodRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    billing_method_name: str = None

    def with_account_token(self, account_token: str) -> DeleteBillingMethodRequest:
        self.account_token = account_token
        return self

    def with_billing_method_name(self, billing_method_name: str) -> DeleteBillingMethodRequest:
        self.billing_method_name = billing_method_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteBillingMethodRequest]:
        if data is None:
            return None
        return DeleteBillingMethodRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_billing_method_name(data.get('billingMethodName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "billingMethodName": self.billing_method_name,
        }


class DescribeReceiptsRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    page_token: str = None
    limit: int = None

    def with_account_token(self, account_token: str) -> DescribeReceiptsRequest:
        self.account_token = account_token
        return self

    def with_page_token(self, page_token: str) -> DescribeReceiptsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeReceiptsRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeReceiptsRequest]:
        if data is None:
            return None
        return DescribeReceiptsRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeBillingsRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    project_name: str = None
    year: int = None
    month: int = None
    region: str = None
    service: str = None

    def with_account_token(self, account_token: str) -> DescribeBillingsRequest:
        self.account_token = account_token
        return self

    def with_project_name(self, project_name: str) -> DescribeBillingsRequest:
        self.project_name = project_name
        return self

    def with_year(self, year: int) -> DescribeBillingsRequest:
        self.year = year
        return self

    def with_month(self, month: int) -> DescribeBillingsRequest:
        self.month = month
        return self

    def with_region(self, region: str) -> DescribeBillingsRequest:
        self.region = region
        return self

    def with_service(self, service: str) -> DescribeBillingsRequest:
        self.service = service
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeBillingsRequest]:
        if data is None:
            return None
        return DescribeBillingsRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_project_name(data.get('projectName'))\
            .with_year(data.get('year'))\
            .with_month(data.get('month'))\
            .with_region(data.get('region'))\
            .with_service(data.get('service'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "projectName": self.project_name,
            "year": self.year,
            "month": self.month,
            "region": self.region,
            "service": self.service,
        }


class DescribeDumpProgressesRequest(core.Gs2Request):

    context_stack: str = None
    page_token: str = None
    limit: int = None

    def with_page_token(self, page_token: str) -> DescribeDumpProgressesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeDumpProgressesRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeDumpProgressesRequest]:
        if data is None:
            return None
        return DescribeDumpProgressesRequest()\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class GetDumpProgressRequest(core.Gs2Request):

    context_stack: str = None
    transaction_id: str = None

    def with_transaction_id(self, transaction_id: str) -> GetDumpProgressRequest:
        self.transaction_id = transaction_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetDumpProgressRequest]:
        if data is None:
            return None
        return GetDumpProgressRequest()\
            .with_transaction_id(data.get('transactionId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transactionId": self.transaction_id,
        }


class WaitDumpUserDataRequest(core.Gs2Request):

    context_stack: str = None
    owner_id: str = None
    transaction_id: str = None
    user_id: str = None
    microservice_name: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_owner_id(self, owner_id: str) -> WaitDumpUserDataRequest:
        self.owner_id = owner_id
        return self

    def with_transaction_id(self, transaction_id: str) -> WaitDumpUserDataRequest:
        self.transaction_id = transaction_id
        return self

    def with_user_id(self, user_id: str) -> WaitDumpUserDataRequest:
        self.user_id = user_id
        return self

    def with_microservice_name(self, microservice_name: str) -> WaitDumpUserDataRequest:
        self.microservice_name = microservice_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> WaitDumpUserDataRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> WaitDumpUserDataRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[WaitDumpUserDataRequest]:
        if data is None:
            return None
        return WaitDumpUserDataRequest()\
            .with_owner_id(data.get('ownerId'))\
            .with_transaction_id(data.get('transactionId'))\
            .with_user_id(data.get('userId'))\
            .with_microservice_name(data.get('microserviceName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ownerId": self.owner_id,
            "transactionId": self.transaction_id,
            "userId": self.user_id,
            "microserviceName": self.microservice_name,
            "timeOffsetToken": self.time_offset_token,
        }


class ArchiveDumpUserDataRequest(core.Gs2Request):

    context_stack: str = None
    owner_id: str = None
    transaction_id: str = None

    def with_owner_id(self, owner_id: str) -> ArchiveDumpUserDataRequest:
        self.owner_id = owner_id
        return self

    def with_transaction_id(self, transaction_id: str) -> ArchiveDumpUserDataRequest:
        self.transaction_id = transaction_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ArchiveDumpUserDataRequest]:
        if data is None:
            return None
        return ArchiveDumpUserDataRequest()\
            .with_owner_id(data.get('ownerId'))\
            .with_transaction_id(data.get('transactionId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ownerId": self.owner_id,
            "transactionId": self.transaction_id,
        }


class DumpUserDataRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_user_id(self, user_id: str) -> DumpUserDataRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DumpUserDataRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DumpUserDataRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DumpUserDataRequest]:
        if data is None:
            return None
        return DumpUserDataRequest()\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class GetDumpUserDataRequest(core.Gs2Request):

    context_stack: str = None
    transaction_id: str = None

    def with_transaction_id(self, transaction_id: str) -> GetDumpUserDataRequest:
        self.transaction_id = transaction_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetDumpUserDataRequest]:
        if data is None:
            return None
        return GetDumpUserDataRequest()\
            .with_transaction_id(data.get('transactionId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transactionId": self.transaction_id,
        }


class DescribeCleanProgressesRequest(core.Gs2Request):

    context_stack: str = None
    page_token: str = None
    limit: int = None

    def with_page_token(self, page_token: str) -> DescribeCleanProgressesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeCleanProgressesRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeCleanProgressesRequest]:
        if data is None:
            return None
        return DescribeCleanProgressesRequest()\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class GetCleanProgressRequest(core.Gs2Request):

    context_stack: str = None
    transaction_id: str = None

    def with_transaction_id(self, transaction_id: str) -> GetCleanProgressRequest:
        self.transaction_id = transaction_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetCleanProgressRequest]:
        if data is None:
            return None
        return GetCleanProgressRequest()\
            .with_transaction_id(data.get('transactionId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transactionId": self.transaction_id,
        }


class WaitCleanUserDataRequest(core.Gs2Request):

    context_stack: str = None
    transaction_id: str = None
    user_id: str = None
    microservice_name: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_transaction_id(self, transaction_id: str) -> WaitCleanUserDataRequest:
        self.transaction_id = transaction_id
        return self

    def with_user_id(self, user_id: str) -> WaitCleanUserDataRequest:
        self.user_id = user_id
        return self

    def with_microservice_name(self, microservice_name: str) -> WaitCleanUserDataRequest:
        self.microservice_name = microservice_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> WaitCleanUserDataRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> WaitCleanUserDataRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[WaitCleanUserDataRequest]:
        if data is None:
            return None
        return WaitCleanUserDataRequest()\
            .with_transaction_id(data.get('transactionId'))\
            .with_user_id(data.get('userId'))\
            .with_microservice_name(data.get('microserviceName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transactionId": self.transaction_id,
            "userId": self.user_id,
            "microserviceName": self.microservice_name,
            "timeOffsetToken": self.time_offset_token,
        }


class CleanUserDataRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_user_id(self, user_id: str) -> CleanUserDataRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CleanUserDataRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CleanUserDataRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CleanUserDataRequest]:
        if data is None:
            return None
        return CleanUserDataRequest()\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class DescribeImportProgressesRequest(core.Gs2Request):

    context_stack: str = None
    page_token: str = None
    limit: int = None

    def with_page_token(self, page_token: str) -> DescribeImportProgressesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeImportProgressesRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeImportProgressesRequest]:
        if data is None:
            return None
        return DescribeImportProgressesRequest()\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class GetImportProgressRequest(core.Gs2Request):

    context_stack: str = None
    transaction_id: str = None

    def with_transaction_id(self, transaction_id: str) -> GetImportProgressRequest:
        self.transaction_id = transaction_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetImportProgressRequest]:
        if data is None:
            return None
        return GetImportProgressRequest()\
            .with_transaction_id(data.get('transactionId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transactionId": self.transaction_id,
        }


class WaitImportUserDataRequest(core.Gs2Request):

    context_stack: str = None
    transaction_id: str = None
    user_id: str = None
    microservice_name: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_transaction_id(self, transaction_id: str) -> WaitImportUserDataRequest:
        self.transaction_id = transaction_id
        return self

    def with_user_id(self, user_id: str) -> WaitImportUserDataRequest:
        self.user_id = user_id
        return self

    def with_microservice_name(self, microservice_name: str) -> WaitImportUserDataRequest:
        self.microservice_name = microservice_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> WaitImportUserDataRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> WaitImportUserDataRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[WaitImportUserDataRequest]:
        if data is None:
            return None
        return WaitImportUserDataRequest()\
            .with_transaction_id(data.get('transactionId'))\
            .with_user_id(data.get('userId'))\
            .with_microservice_name(data.get('microserviceName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transactionId": self.transaction_id,
            "userId": self.user_id,
            "microserviceName": self.microservice_name,
            "timeOffsetToken": self.time_offset_token,
        }


class PrepareImportUserDataRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_user_id(self, user_id: str) -> PrepareImportUserDataRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> PrepareImportUserDataRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> PrepareImportUserDataRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[PrepareImportUserDataRequest]:
        if data is None:
            return None
        return PrepareImportUserDataRequest()\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class ImportUserDataRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    upload_token: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_user_id(self, user_id: str) -> ImportUserDataRequest:
        self.user_id = user_id
        return self

    def with_upload_token(self, upload_token: str) -> ImportUserDataRequest:
        self.upload_token = upload_token
        return self

    def with_time_offset_token(self, time_offset_token: str) -> ImportUserDataRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ImportUserDataRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ImportUserDataRequest]:
        if data is None:
            return None
        return ImportUserDataRequest()\
            .with_user_id(data.get('userId'))\
            .with_upload_token(data.get('uploadToken'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "uploadToken": self.upload_token,
            "timeOffsetToken": self.time_offset_token,
        }


class DescribeImportErrorLogsRequest(core.Gs2Request):

    context_stack: str = None
    transaction_id: str = None
    page_token: str = None
    limit: int = None

    def with_transaction_id(self, transaction_id: str) -> DescribeImportErrorLogsRequest:
        self.transaction_id = transaction_id
        return self

    def with_page_token(self, page_token: str) -> DescribeImportErrorLogsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeImportErrorLogsRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeImportErrorLogsRequest]:
        if data is None:
            return None
        return DescribeImportErrorLogsRequest()\
            .with_transaction_id(data.get('transactionId'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transactionId": self.transaction_id,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class GetImportErrorLogRequest(core.Gs2Request):

    context_stack: str = None
    transaction_id: str = None
    error_log_name: str = None

    def with_transaction_id(self, transaction_id: str) -> GetImportErrorLogRequest:
        self.transaction_id = transaction_id
        return self

    def with_error_log_name(self, error_log_name: str) -> GetImportErrorLogRequest:
        self.error_log_name = error_log_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetImportErrorLogRequest]:
        if data is None:
            return None
        return GetImportErrorLogRequest()\
            .with_transaction_id(data.get('transactionId'))\
            .with_error_log_name(data.get('errorLogName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transactionId": self.transaction_id,
            "errorLogName": self.error_log_name,
        }