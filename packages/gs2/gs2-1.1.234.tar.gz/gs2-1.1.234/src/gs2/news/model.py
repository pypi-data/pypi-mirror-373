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

import re
from typing import *
from gs2 import core


class GitHubCheckoutSetting(core.Gs2Model):
    api_key_id: str = None
    repository_name: str = None
    source_path: str = None
    reference_type: str = None
    commit_hash: str = None
    branch_name: str = None
    tag_name: str = None

    def with_api_key_id(self, api_key_id: str) -> GitHubCheckoutSetting:
        self.api_key_id = api_key_id
        return self

    def with_repository_name(self, repository_name: str) -> GitHubCheckoutSetting:
        self.repository_name = repository_name
        return self

    def with_source_path(self, source_path: str) -> GitHubCheckoutSetting:
        self.source_path = source_path
        return self

    def with_reference_type(self, reference_type: str) -> GitHubCheckoutSetting:
        self.reference_type = reference_type
        return self

    def with_commit_hash(self, commit_hash: str) -> GitHubCheckoutSetting:
        self.commit_hash = commit_hash
        return self

    def with_branch_name(self, branch_name: str) -> GitHubCheckoutSetting:
        self.branch_name = branch_name
        return self

    def with_tag_name(self, tag_name: str) -> GitHubCheckoutSetting:
        self.tag_name = tag_name
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
    ) -> Optional[GitHubCheckoutSetting]:
        if data is None:
            return None
        return GitHubCheckoutSetting()\
            .with_api_key_id(data.get('apiKeyId'))\
            .with_repository_name(data.get('repositoryName'))\
            .with_source_path(data.get('sourcePath'))\
            .with_reference_type(data.get('referenceType'))\
            .with_commit_hash(data.get('commitHash'))\
            .with_branch_name(data.get('branchName'))\
            .with_tag_name(data.get('tagName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "apiKeyId": self.api_key_id,
            "repositoryName": self.repository_name,
            "sourcePath": self.source_path,
            "referenceType": self.reference_type,
            "commitHash": self.commit_hash,
            "branchName": self.branch_name,
            "tagName": self.tag_name,
        }


class LogSetting(core.Gs2Model):
    logging_namespace_id: str = None

    def with_logging_namespace_id(self, logging_namespace_id: str) -> LogSetting:
        self.logging_namespace_id = logging_namespace_id
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
    ) -> Optional[LogSetting]:
        if data is None:
            return None
        return LogSetting()\
            .with_logging_namespace_id(data.get('loggingNamespaceId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "loggingNamespaceId": self.logging_namespace_id,
        }


class SetCookieRequestEntry(core.Gs2Model):
    key: str = None
    value: str = None

    def with_key(self, key: str) -> SetCookieRequestEntry:
        self.key = key
        return self

    def with_value(self, value: str) -> SetCookieRequestEntry:
        self.value = value
        return self

    @classmethod
    def create_grn(
        cls,
    ):
        return ''.format(
        )

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
    ) -> Optional[SetCookieRequestEntry]:
        if data is None:
            return None
        return SetCookieRequestEntry()\
            .with_key(data.get('key'))\
            .with_value(data.get('value'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
        }


class News(core.Gs2Model):
    section: str = None
    content: str = None
    title: str = None
    schedule_event_id: str = None
    timestamp: int = None
    front_matter: str = None

    def with_section(self, section: str) -> News:
        self.section = section
        return self

    def with_content(self, content: str) -> News:
        self.content = content
        return self

    def with_title(self, title: str) -> News:
        self.title = title
        return self

    def with_schedule_event_id(self, schedule_event_id: str) -> News:
        self.schedule_event_id = schedule_event_id
        return self

    def with_timestamp(self, timestamp: int) -> News:
        self.timestamp = timestamp
        return self

    def with_front_matter(self, front_matter: str) -> News:
        self.front_matter = front_matter
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
    ) -> Optional[News]:
        if data is None:
            return None
        return News()\
            .with_section(data.get('section'))\
            .with_content(data.get('content'))\
            .with_title(data.get('title'))\
            .with_schedule_event_id(data.get('scheduleEventId'))\
            .with_timestamp(data.get('timestamp'))\
            .with_front_matter(data.get('frontMatter'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "section": self.section,
            "content": self.content,
            "title": self.title,
            "scheduleEventId": self.schedule_event_id,
            "timestamp": self.timestamp,
            "frontMatter": self.front_matter,
        }


class Content(core.Gs2Model):
    section: str = None
    content: str = None
    front_matter: str = None

    def with_section(self, section: str) -> Content:
        self.section = section
        return self

    def with_content(self, content: str) -> Content:
        self.content = content
        return self

    def with_front_matter(self, front_matter: str) -> Content:
        self.front_matter = front_matter
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
    ) -> Optional[Content]:
        if data is None:
            return None
        return Content()\
            .with_section(data.get('section'))\
            .with_content(data.get('content'))\
            .with_front_matter(data.get('frontMatter'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "section": self.section,
            "content": self.content,
            "frontMatter": self.front_matter,
        }


class View(core.Gs2Model):
    contents: List[Content] = None
    remove_contents: List[Content] = None

    def with_contents(self, contents: List[Content]) -> View:
        self.contents = contents
        return self

    def with_remove_contents(self, remove_contents: List[Content]) -> View:
        self.remove_contents = remove_contents
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
    ) -> Optional[View]:
        if data is None:
            return None
        return View()\
            .with_contents(None if data.get('contents') is None else [
                Content.from_dict(data.get('contents')[i])
                for i in range(len(data.get('contents')))
            ])\
            .with_remove_contents(None if data.get('removeContents') is None else [
                Content.from_dict(data.get('removeContents')[i])
                for i in range(len(data.get('removeContents')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contents": None if self.contents is None else [
                self.contents[i].to_dict() if self.contents[i] else None
                for i in range(len(self.contents))
            ],
            "removeContents": None if self.remove_contents is None else [
                self.remove_contents[i].to_dict() if self.remove_contents[i] else None
                for i in range(len(self.remove_contents))
            ],
        }


class Output(core.Gs2Model):
    output_id: str = None
    name: str = None
    text: str = None
    created_at: int = None
    revision: int = None

    def with_output_id(self, output_id: str) -> Output:
        self.output_id = output_id
        return self

    def with_name(self, name: str) -> Output:
        self.name = name
        return self

    def with_text(self, text: str) -> Output:
        self.text = text
        return self

    def with_created_at(self, created_at: int) -> Output:
        self.created_at = created_at
        return self

    def with_revision(self, revision: int) -> Output:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        upload_token,
        output_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:news:{namespaceName}:progress:{uploadToken}:output:{outputName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            uploadToken=upload_token,
            outputName=output_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):news:(?P<namespaceName>.+):progress:(?P<uploadToken>.+):output:(?P<outputName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):news:(?P<namespaceName>.+):progress:(?P<uploadToken>.+):output:(?P<outputName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):news:(?P<namespaceName>.+):progress:(?P<uploadToken>.+):output:(?P<outputName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_upload_token_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):news:(?P<namespaceName>.+):progress:(?P<uploadToken>.+):output:(?P<outputName>.+)', grn)
        if match is None:
            return None
        return match.group('upload_token')

    @classmethod
    def get_output_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):news:(?P<namespaceName>.+):progress:(?P<uploadToken>.+):output:(?P<outputName>.+)', grn)
        if match is None:
            return None
        return match.group('output_name')

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
    ) -> Optional[Output]:
        if data is None:
            return None
        return Output()\
            .with_output_id(data.get('outputId'))\
            .with_name(data.get('name'))\
            .with_text(data.get('text'))\
            .with_created_at(data.get('createdAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "outputId": self.output_id,
            "name": self.name,
            "text": self.text,
            "createdAt": self.created_at,
            "revision": self.revision,
        }


class Progress(core.Gs2Model):
    progress_id: str = None
    upload_token: str = None
    generated: int = None
    pattern_count: int = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_progress_id(self, progress_id: str) -> Progress:
        self.progress_id = progress_id
        return self

    def with_upload_token(self, upload_token: str) -> Progress:
        self.upload_token = upload_token
        return self

    def with_generated(self, generated: int) -> Progress:
        self.generated = generated
        return self

    def with_pattern_count(self, pattern_count: int) -> Progress:
        self.pattern_count = pattern_count
        return self

    def with_created_at(self, created_at: int) -> Progress:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Progress:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Progress:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        upload_token,
    ):
        return 'grn:gs2:{region}:{ownerId}:news:{namespaceName}:progress:{uploadToken}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            uploadToken=upload_token,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):news:(?P<namespaceName>.+):progress:(?P<uploadToken>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):news:(?P<namespaceName>.+):progress:(?P<uploadToken>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):news:(?P<namespaceName>.+):progress:(?P<uploadToken>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_upload_token_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):news:(?P<namespaceName>.+):progress:(?P<uploadToken>.+)', grn)
        if match is None:
            return None
        return match.group('upload_token')

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
    ) -> Optional[Progress]:
        if data is None:
            return None
        return Progress()\
            .with_progress_id(data.get('progressId'))\
            .with_upload_token(data.get('uploadToken'))\
            .with_generated(data.get('generated'))\
            .with_pattern_count(data.get('patternCount'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "progressId": self.progress_id,
            "uploadToken": self.upload_token,
            "generated": self.generated,
            "patternCount": self.pattern_count,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    version: str = None
    log_setting: LogSetting = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_namespace_id(self, namespace_id: str) -> Namespace:
        self.namespace_id = namespace_id
        return self

    def with_name(self, name: str) -> Namespace:
        self.name = name
        return self

    def with_description(self, description: str) -> Namespace:
        self.description = description
        return self

    def with_version(self, version: str) -> Namespace:
        self.version = version
        return self

    def with_log_setting(self, log_setting: LogSetting) -> Namespace:
        self.log_setting = log_setting
        return self

    def with_created_at(self, created_at: int) -> Namespace:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Namespace:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Namespace:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:news:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):news:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):news:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):news:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

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
    ) -> Optional[Namespace]:
        if data is None:
            return None
        return Namespace()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_version(data.get('version'))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }