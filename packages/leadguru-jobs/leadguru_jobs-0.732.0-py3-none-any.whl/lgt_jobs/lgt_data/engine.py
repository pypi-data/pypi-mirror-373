from __future__ import annotations
import os
from collections import OrderedDict
from datetime import datetime, UTC
from bson import ObjectId
from mongoengine import connect, Document, DateTimeField, StringField, IntField, ObjectIdField, ListField
from typing import Dict, Tuple, Optional
from lgt_jobs.lgt_data.mongo_repository import to_object_id

connect(host=os.environ.get('MONGO_CONNECTION_STRING', 'mongodb://127.0.0.1:27017/'), db="lgt_admin", alias="lgt_admin")


class GlobalUserConfiguration(Document):
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)
    created_by = ObjectIdField(required=False)
    updated_by = ObjectIdField(required=False)
    dedicated_bots_days_to_remove = IntField(required=True)

    meta = {"db_alias": "lgt_admin"}

    @staticmethod
    def get_config() -> GlobalUserConfiguration:
        items = list(GlobalUserConfiguration.objects())
        if not items:
            # create default config
            GlobalUserConfiguration(
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                dedicated_bots_days_to_remove=10
            ).save()
            items = list(GlobalUserConfiguration.objects())
        return items[-1]


class UserTrackAction(Document):
    user_id = ObjectIdField(required=True)
    action = StringField(required=True)
    metadata = StringField(required=False)
    created_at = DateTimeField(required=True)
    meta = {"indexes": ["user_id"], "db_alias": "lgt_admin"}

    @staticmethod
    def get_aggregated(from_date: datetime = None, to_date: datetime = None) \
            -> Dict[str, Tuple[datetime, datetime]]:
        pipeline = [
            {
                "$group": {
                    "_id": "$user_id",
                    "last_action_at": {"$max": "$created_at"},
                    "first_action_at": {"$min": "$created_at"}
                }
            }]

        if from_date:
            beginning_of_the_day = datetime(from_date.year, from_date.month, from_date.day, 0, 0, 0, 0)
            pipeline.insert(0, {"$match": {"created_at": {"$gte": beginning_of_the_day}}})

        if to_date:
            end_of_the_day = datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59, 999)
            pipeline.insert(0, {"$match": {"created_at": {"$lte": end_of_the_day}}})

        result = list(UserTrackAction.objects.aggregate(*pipeline))

        return {str(item.get("_id")): (item["first_action_at"], item["last_action_at"]) for item in result}

    @staticmethod
    def track(user_id: str | ObjectId, action: str, metadata: Optional[str] = None):
        UserTrackAction(
            user_id=to_object_id(user_id),
            created_at=datetime.now(UTC),
            action=action,
            metadata=metadata
        ).save()

    @staticmethod
    def get_global_user_actions(user_id: str = None, from_date: datetime = None,
                                to_date: datetime = None, actions: list = None) -> \
            Dict[str, Dict[str, Dict[str, int]]]:
        pipeline = [
            {
                '$addFields': {
                    'created_at_formatted': {
                        '$dateToString': {
                            'format': '%Y-%m-%d',
                            'date': '$created_at'
                        }
                    }
                }
            }, {
                '$group': {
                    '_id': '$created_at_formatted',
                    'count': {
                        '$sum': 1
                    }
                }
            }
        ]

        if actions:
            pipeline.insert(0, {'$match': {'action': {'$in': actions}}})

        if user_id:
            pipeline.insert(0, {"$match": {"user_id": to_object_id(user_id)}})

        if from_date:
            beginning_of_the_day = datetime(from_date.year, from_date.month, from_date.day, 0, 0, 0, 0)
            pipeline.insert(0, {"$match": {"created_at": {"$gte": beginning_of_the_day}}})

        if to_date:
            end_of_the_day = datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59, 999)
            pipeline.insert(0, {"$match": {"created_at": {"$lte": end_of_the_day}}})

        analytics = list(UserTrackAction.objects.aggregate(*pipeline))
        analytics_dic = OrderedDict()
        for item in analytics:
            analytics_dic[item["_id"]] = item["count"]

        return analytics_dic

    @staticmethod
    def get_daily_user_actions(user_id: str = None, from_date: datetime = None,
                               to_date: datetime = None, actions: list = None) -> \
            Dict[str, Dict[str, Dict[str, int]]]:
        pipeline = [
            {
                '$match': {
                    '$and': [
                        {'action': {'$ne': 'login'}},
                        {'action': {'$ne': 'chat.message'}}
                    ]
                }
            },
            {
                '$group': {
                    '_id': {
                        'date': {
                            '$dateFromParts': {
                                'day': {
                                    '$dayOfMonth': '$created_at'
                                },
                                'month': {
                                    '$month': '$created_at'
                                },
                                'year': {
                                    '$year': '$created_at'
                                }
                            }
                        },
                        'action': '$action',
                        'user_id': '$user_id'
                    },
                    'count': {
                            '$sum': 1
                    }
                }
            }
        ]

        if actions:
            pipeline.insert(0, {'$match': {'action': {'$in': actions}}})

        if user_id:
            pipeline.insert(0, {"$match": {"user_id": to_object_id(user_id)}})

        if from_date:
            beginning_of_the_day = datetime(from_date.year, from_date.month, from_date.day, 0, 0, 0, 0)
            pipeline.insert(0, {"$match": {"created_at": {"$gte": beginning_of_the_day}}})

        if to_date:
            end_of_the_day = datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59, 999)
            pipeline.insert(0, {"$match": {"created_at": {"$lte": end_of_the_day}}})

        analytics = list(UserTrackAction.objects.aggregate(*pipeline))

        result = {}
        for item in analytics:
            date = item["_id"]["date"].strftime('%Y-%m-%d')
            user_id = str(item["_id"]["user_id"])
            if date not in result:
                result[date] = {}
            if user_id not in result[date]:
                result[date][user_id] = {}
            result[date][user_id][item["_id"]["action"]] = item["count"]

        return result


class DelayedJob(Document):
    created_at = DateTimeField(required=True)
    scheduled_at = DateTimeField(required=True)
    job_type = StringField(required=True)
    data = StringField(required=True)
    jib = StringField(required=True)
    executed_at: DateTimeField(required=False)

    meta = {"indexes": ["-scheduled_at", "jib"], "db_alias": "lgt_admin"}


class UserCreditStatementDocument(Document):
    meta = {"indexes": [("user_id", "created_at"),
                        ("user_id", "created_at", "action")], "db_alias": "lgt_admin"}

    user_id = ObjectIdField(required=True)
    created_at = DateTimeField(required=True)
    balance = IntField(required=True)
    action = StringField(required=True)
    lead_id = StringField(required=False)
    attributes = ListField(field=StringField(), required=False)

