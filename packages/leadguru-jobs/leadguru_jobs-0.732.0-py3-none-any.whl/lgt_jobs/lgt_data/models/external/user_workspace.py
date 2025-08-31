class UserWorkspace:
    pass

    def __init__(self):
        super().__init__()
        self.id = ''
        self.name = ''
        self.url = ''
        self.domain = ''
        self.active_users = ''
        self.profile_photos = []
        self.associated_user = ''
        self.magic_login_url = ''
        self.magic_login_code = ''
        self.user_email = ''
        self.user_type = ''
        self.variant = ''
        self.token = ''
        self.icon = ''
        self.two_factor_required = False

    @classmethod
    def from_dic(cls, dic: dict):
        if not dic:
            return None

        model: UserWorkspace = cls()
        for k, v in dic.items():
            setattr(model, k, v)

        model.icon = dic.get('icon_88', "")
        return model
