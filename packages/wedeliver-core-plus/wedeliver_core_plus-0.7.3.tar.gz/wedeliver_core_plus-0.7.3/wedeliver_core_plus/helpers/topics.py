class Topics:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Topics, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.INTERNAL_NOTIFICATION_MESSAGE = 'internal_notification_message'
        self.SEND_MAIL = 'send_mail'
        self.SEND_SMS = 'send_sms'
        self.LOG_MODEL_CHANGES = 'log_model_changes'
        self.SEND_PUSH_NOTIFICATION = 'send_push_notification'
        self.THIRD_PARTY_ADD_BULK_TRANSACTIONS = 'third_party_add_bulk_transactions'