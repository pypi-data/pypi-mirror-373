import copy
from datetime import datetime, UTC
from typing import List

from lgt_jobs.lgt_data.models.base import DictionaryModel
from lgt_jobs.lgt_data.models.external.user_workspace import UserWorkspace
from lgt_jobs.lgt_data.models.people.profile import Profile


class DiscordUser(DictionaryModel):
    pass

    def __init__(self):
        super().__init__()
        self.created_at = datetime.now(UTC)
        self.login = ''
        self.captcha_key = ''
        self.status = None
        self.workspaces: List[UserWorkspace] = []
        self.deleted = False
        self.profile: Profile | None = None

    def to_dic(self):
        result = copy.deepcopy(self.__dict__)

        if result.get('workspaces'):
            result['workspaces'] = [ws.__dict__ for ws in result.get('workspaces')]

        if result.get('profile'):
            result['profile'] = result.get('profile').__dict__

        return result

    @classmethod
    def from_dic(cls, dic: dict):
        if not dic:
            return None

        model = cls()
        for k, v in dic.items():
            setattr(model, k, v)

        model.workspaces = [UserWorkspace.from_dic(ws) for ws in dic.get('workspaces', [])]
        model.profile = Profile.from_dic(dic.get('profile'))
        return model
