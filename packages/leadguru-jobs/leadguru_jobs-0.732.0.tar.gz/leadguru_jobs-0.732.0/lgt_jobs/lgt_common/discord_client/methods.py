from enum import Enum


class DiscordMethods(str, Enum):
    USER_GUILDS = 'users/@me/guilds'
    USER_DMS = 'users/@me/channels'
    USER = 'users/@me'
    USER_PROFILE = 'users/@me/profile'
    LOGIN = 'auth/login'

    @staticmethod
    def guild_channels(guild_id: str):
        return f'guilds/{guild_id}/channels'

    @staticmethod
    def guild_user(guild_id: str):
        return f'guilds/{guild_id}/members/@me'

    @staticmethod
    def guild_bio(guild_id: str):
        return f'guilds/{guild_id}/profile/@me'

    @staticmethod
    def channels_invites(channel_id: str):
        return f'channels/{channel_id}/invites'
