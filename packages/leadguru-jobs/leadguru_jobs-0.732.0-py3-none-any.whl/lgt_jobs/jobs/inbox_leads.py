from abc import ABC
import logging as log
from lgt_jobs.lgt_common.slack_client.web_client import SlackWebClient
from lgt_jobs.lgt_data.models.bots.dedicated_bot import DedicatedBotModel
from lgt_jobs.lgt_data.models.chat.request import MessageRequest
from lgt_jobs.lgt_data.models.people.people import SlackMemberInformation
from lgt_jobs.lgt_data.models.user.user import UserModel
from lgt_jobs.lgt_data.mongo_repository import UserMongoRepository, DedicatedBotRepository, \
    SlackContactUserRepository, UserContactsRepository, MessageRequestsRepository
from pydantic import BaseModel
from lgt_jobs.basejobs import BaseBackgroundJob, BaseBackgroundJobData
from requests import exceptions

"""
Save inbox leads
"""


class InboxLeadsJobData(BaseBackgroundJobData, BaseModel):
    pass


class InboxLeadsJob(BaseBackgroundJob, ABC):

    @property
    def job_data_type(self) -> type:
        return InboxLeadsJobData

    def exec(self, _: InboxLeadsJobData):
        users = UserMongoRepository().get_users()
        for user in users:
            log.info(f'[InboxLeadsJob]: Loading chat for the: {user.email}')
            dedicated_bots = DedicatedBotRepository().get_all(only_valid=True, user_id=user.id)
            for dedicated_bot in dedicated_bots:
                self.create_inbox_leads(user, dedicated_bot)

    @staticmethod
    def create_inbox_leads(user: UserModel, dedicated_bot: DedicatedBotModel):
        requests_repo = MessageRequestsRepository()
        slack_client = SlackWebClient(dedicated_bot.token, dedicated_bot.cookies)
        attempt = 0
        conversations_list = []
        while attempt < 3:
            try:
                conversations_list = slack_client.get_im_list().get('channels', [])
                break
            except exceptions.JSONDecodeError as er:
                log.info(f'[InboxLeadsJob]: Loading chat failed for the: {dedicated_bot.id}. '
                         f'Attempt: {attempt}. {str(er)}')
                attempt += 1

        log.info(f'[InboxLeadsJob]: Loading chat for the: {dedicated_bot.id}. '
                 f'Count of chats: {len(conversations_list)}')
        for conversation in conversations_list:
            sender_id = conversation.get('user')
            im_id = conversation.get('id')
            if sender_id == "USLACKBOT":
                continue

            history = {}
            while attempt < 3:
                try:
                    history = slack_client.chat_history(im_id)
                    break
                except exceptions.JSONDecodeError as er:
                    log.info(f'[InboxLeadsJob]: Loading chat failed for the: {dedicated_bot.id}. '
                             f'Attempt: {attempt}. {str(er)}')
                    attempt += 1

            if not history.get('ok', False):
                log.warning(f'Failed to load chat for the: {dedicated_bot.id}. ERROR: {history.get("error", "")}')
                continue

            messages = history.get('messages', [])
            log.info(f'[InboxLeadsJob]: Count of messages: {len(messages)} with {sender_id}')
            if messages:
                user_contact = UserContactsRepository().find_one(user.id, sender_id=sender_id)
                if not user_contact:
                    people = SlackContactUserRepository().find_one(sender_id)
                    if not people:
                        slack_profile = slack_client.get_profile(sender_id).get('user')
                        InboxLeadsJob.create_people(slack_profile, dedicated_bot)

                    message_request = MessageRequest.from_slack_response(dedicated_bot, messages[0], sender_id)
                    if message_request.is_system_message:
                        continue
                    sender_request = requests_repo.find(user.id, sender_id)
                    if not sender_request:
                        log.info(f"[InboxLeadsJob]: New message request from {sender_id} for user: {user.email}")
                        requests_repo.upsert(user.id, sender_id, message_request)
                        user.notification_settings.inbox.need_to_notify = True
                        UserMongoRepository().set(user.id, notification_settings=user.notification_settings.to_dic())

    @staticmethod
    def create_people(slack_profile: dict, dedicated_bot: DedicatedBotModel):
        member_info: SlackMemberInformation = SlackMemberInformation.from_slack_response(slack_profile,
                                                                                         dedicated_bot.source)
        SlackContactUserRepository().collection().update_one({"sender_id": member_info.sender_id,
                                                              "source.source_id": dedicated_bot.source.source_id},
                                                             {"$set": member_info.to_dic()}, upsert=True)
        return SlackContactUserRepository().find_one(member_info.sender_id)
