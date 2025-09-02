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


class NotificationSetting(core.Gs2Model):
    gateway_namespace_id: str = None
    enable_transfer_mobile_notification: bool = None
    sound: str = None

    def with_gateway_namespace_id(self, gateway_namespace_id: str) -> NotificationSetting:
        self.gateway_namespace_id = gateway_namespace_id
        return self

    def with_enable_transfer_mobile_notification(self, enable_transfer_mobile_notification: bool) -> NotificationSetting:
        self.enable_transfer_mobile_notification = enable_transfer_mobile_notification
        return self

    def with_sound(self, sound: str) -> NotificationSetting:
        self.sound = sound
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
    ) -> Optional[NotificationSetting]:
        if data is None:
            return None
        return NotificationSetting()\
            .with_gateway_namespace_id(data.get('gatewayNamespaceId'))\
            .with_enable_transfer_mobile_notification(data.get('enableTransferMobileNotification'))\
            .with_sound(data.get('sound'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gatewayNamespaceId": self.gateway_namespace_id,
            "enableTransferMobileNotification": self.enable_transfer_mobile_notification,
            "sound": self.sound,
        }


class ScriptSetting(core.Gs2Model):
    trigger_script_id: str = None
    done_trigger_target_type: str = None
    done_trigger_script_id: str = None
    done_trigger_queue_namespace_id: str = None

    def with_trigger_script_id(self, trigger_script_id: str) -> ScriptSetting:
        self.trigger_script_id = trigger_script_id
        return self

    def with_done_trigger_target_type(self, done_trigger_target_type: str) -> ScriptSetting:
        self.done_trigger_target_type = done_trigger_target_type
        return self

    def with_done_trigger_script_id(self, done_trigger_script_id: str) -> ScriptSetting:
        self.done_trigger_script_id = done_trigger_script_id
        return self

    def with_done_trigger_queue_namespace_id(self, done_trigger_queue_namespace_id: str) -> ScriptSetting:
        self.done_trigger_queue_namespace_id = done_trigger_queue_namespace_id
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
    ) -> Optional[ScriptSetting]:
        if data is None:
            return None
        return ScriptSetting()\
            .with_trigger_script_id(data.get('triggerScriptId'))\
            .with_done_trigger_target_type(data.get('doneTriggerTargetType'))\
            .with_done_trigger_script_id(data.get('doneTriggerScriptId'))\
            .with_done_trigger_queue_namespace_id(data.get('doneTriggerQueueNamespaceId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "triggerScriptId": self.trigger_script_id,
            "doneTriggerTargetType": self.done_trigger_target_type,
            "doneTriggerScriptId": self.done_trigger_script_id,
            "doneTriggerQueueNamespaceId": self.done_trigger_queue_namespace_id,
        }


class AppLovinMax(core.Gs2Model):
    allow_ad_unit_id: str = None
    event_key: str = None

    def with_allow_ad_unit_id(self, allow_ad_unit_id: str) -> AppLovinMax:
        self.allow_ad_unit_id = allow_ad_unit_id
        return self

    def with_event_key(self, event_key: str) -> AppLovinMax:
        self.event_key = event_key
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
    ) -> Optional[AppLovinMax]:
        if data is None:
            return None
        return AppLovinMax()\
            .with_allow_ad_unit_id(data.get('allowAdUnitId'))\
            .with_event_key(data.get('eventKey'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowAdUnitId": self.allow_ad_unit_id,
            "eventKey": self.event_key,
        }


class UnityAd(core.Gs2Model):
    keys: List[str] = None

    def with_keys(self, keys: List[str]) -> UnityAd:
        self.keys = keys
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
    ) -> Optional[UnityAd]:
        if data is None:
            return None
        return UnityAd()\
            .with_keys(None if data.get('keys') is None else [
                data.get('keys')[i]
                for i in range(len(data.get('keys')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "keys": None if self.keys is None else [
                self.keys[i]
                for i in range(len(self.keys))
            ],
        }


class AdMob(core.Gs2Model):
    allow_ad_unit_ids: List[str] = None

    def with_allow_ad_unit_ids(self, allow_ad_unit_ids: List[str]) -> AdMob:
        self.allow_ad_unit_ids = allow_ad_unit_ids
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
    ) -> Optional[AdMob]:
        if data is None:
            return None
        return AdMob()\
            .with_allow_ad_unit_ids(None if data.get('allowAdUnitIds') is None else [
                data.get('allowAdUnitIds')[i]
                for i in range(len(data.get('allowAdUnitIds')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowAdUnitIds": None if self.allow_ad_unit_ids is None else [
                self.allow_ad_unit_ids[i]
                for i in range(len(self.allow_ad_unit_ids))
            ],
        }


class Point(core.Gs2Model):
    point_id: str = None
    user_id: str = None
    point: int = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_point_id(self, point_id: str) -> Point:
        self.point_id = point_id
        return self

    def with_user_id(self, user_id: str) -> Point:
        self.user_id = user_id
        return self

    def with_point(self, point: int) -> Point:
        self.point = point
        return self

    def with_created_at(self, created_at: int) -> Point:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Point:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Point:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
    ):
        return 'grn:gs2:{region}:{ownerId}:adReward:{namespaceName}:user:{userId}:point'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):adReward:(?P<namespaceName>.+):user:(?P<userId>.+):point', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):adReward:(?P<namespaceName>.+):user:(?P<userId>.+):point', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):adReward:(?P<namespaceName>.+):user:(?P<userId>.+):point', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):adReward:(?P<namespaceName>.+):user:(?P<userId>.+):point', grn)
        if match is None:
            return None
        return match.group('user_id')

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
    ) -> Optional[Point]:
        if data is None:
            return None
        return Point()\
            .with_point_id(data.get('pointId'))\
            .with_user_id(data.get('userId'))\
            .with_point(data.get('point'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pointId": self.point_id,
            "userId": self.user_id,
            "point": self.point,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    admob: AdMob = None
    unity_ad: UnityAd = None
    app_lovin_maxes: List[AppLovinMax] = None
    acquire_point_script: ScriptSetting = None
    consume_point_script: ScriptSetting = None
    change_point_notification: NotificationSetting = None
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

    def with_admob(self, admob: AdMob) -> Namespace:
        self.admob = admob
        return self

    def with_unity_ad(self, unity_ad: UnityAd) -> Namespace:
        self.unity_ad = unity_ad
        return self

    def with_app_lovin_maxes(self, app_lovin_maxes: List[AppLovinMax]) -> Namespace:
        self.app_lovin_maxes = app_lovin_maxes
        return self

    def with_acquire_point_script(self, acquire_point_script: ScriptSetting) -> Namespace:
        self.acquire_point_script = acquire_point_script
        return self

    def with_consume_point_script(self, consume_point_script: ScriptSetting) -> Namespace:
        self.consume_point_script = consume_point_script
        return self

    def with_change_point_notification(self, change_point_notification: NotificationSetting) -> Namespace:
        self.change_point_notification = change_point_notification
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
        return 'grn:gs2:{region}:{ownerId}:adReward:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):adReward:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):adReward:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):adReward:(?P<namespaceName>.+)', grn)
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
            .with_admob(AdMob.from_dict(data.get('admob')))\
            .with_unity_ad(UnityAd.from_dict(data.get('unityAd')))\
            .with_app_lovin_maxes(None if data.get('appLovinMaxes') is None else [
                AppLovinMax.from_dict(data.get('appLovinMaxes')[i])
                for i in range(len(data.get('appLovinMaxes')))
            ])\
            .with_acquire_point_script(ScriptSetting.from_dict(data.get('acquirePointScript')))\
            .with_consume_point_script(ScriptSetting.from_dict(data.get('consumePointScript')))\
            .with_change_point_notification(NotificationSetting.from_dict(data.get('changePointNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "admob": self.admob.to_dict() if self.admob else None,
            "unityAd": self.unity_ad.to_dict() if self.unity_ad else None,
            "appLovinMaxes": None if self.app_lovin_maxes is None else [
                self.app_lovin_maxes[i].to_dict() if self.app_lovin_maxes[i] else None
                for i in range(len(self.app_lovin_maxes))
            ],
            "acquirePointScript": self.acquire_point_script.to_dict() if self.acquire_point_script else None,
            "consumePointScript": self.consume_point_script.to_dict() if self.consume_point_script else None,
            "changePointNotification": self.change_point_notification.to_dict() if self.change_point_notification else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }