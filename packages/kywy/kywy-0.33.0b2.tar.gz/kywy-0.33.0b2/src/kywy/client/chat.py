class KawaChat:

    def __init__(self, kawa_client, copilot_type: str, conversation_id: str):
        self._k = kawa_client
        self._chat_url_prefix = self._k.kawa_api_url + '/chat'
        self._conversation_id = conversation_id
        self._copilot_type = copilot_type

    def append_message(self, layout_id: str, message: str):
        url = '{}/append-message-to-conversation'.format(self._chat_url_prefix)
        return self._k.post(url, {
            'conversationId': self._conversation_id,
            'messageType': 'USER',
            'context': {
                'layoutId': layout_id
            },
            'content': [{
                'type': 'TEXT',
                'value': message
            }]
        })

    def get_answer_to_message(self, message_id: str):
        url = ('{}/{}/get-answer-to-message'.format(self._chat_url_prefix, self._copilot_type))
        return self._k.post(url, {
            'conversationId': self._conversation_id,
            'messageId': message_id,
        })
