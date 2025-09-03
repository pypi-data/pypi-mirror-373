from .app_synchronizer import Synchronizer


class Agent:

    def __init__(self, kawa, reporter, name, application, instructions='', color=None):
        self._k = kawa
        self._reporter = reporter
        self._name = name
        self._color = color or "#ec1254"
        self._agent_id = None
        self._instructions = instructions or ''
        self._application = application

    @property
    def agent_id(self):
        return self._agent_id

    @property
    def name(self):
        return self._name

    @property
    def color(self):
        return self._color

    @property
    def instructions(self):
        return self._instructions

    @property
    def tag(self):
        return f'{self._application.tag}|{self._name}'

    def sync(self):
        self._agent_id = Agent._Synchronizer(kawa=self._k, agent=self).sync()

    class _Synchronizer(Synchronizer):
        def __init__(self, kawa, agent):
            super().__init__(
                kawa=kawa,
                icon='🤖',
                entity_description=f'Agent "{agent.name}"',
                entity_tag=agent.tag,
            )
            self._agent = agent

        def _load_state(self):
            agent = self._k.entities.agents().find_entity_by_tag(tag=self._tag)
            return agent

        def _raise_if_state_invalid(self):
            ...

        def _should_create(self):
            return not self._state

        def _create_new_entity(self):
            new_agent = self._k.commands.run_command('createAgent', {
                "displayInformation": {
                    "displayName": self._agent.name,
                    "extraInformation": {
                        "color": self._agent.color,
                        "immutableTag": self._tag,
                    }
                },
                "instructions": [self._agent.instructions],
                "commands": [],
                "knowledgeIds": [],
                "capabilities": {
                    "sendEmails": False,
                    "internetSearch": False,
                    "querySheet": True,
                    "useAttachedFiles": True
                }
            })
            self._new_agent_id = new_agent['id']

        def _update_entity(self):
            self._k.commands.run_command('updateAgent', {
                "agentId": str(self._state['id']),
                "displayInformation": {
                    "displayName": self._agent.name,
                    "extraInformation": {
                        "color": self._agent.color,
                        "immutableTag": self._tag,
                    }
                },
                "instructions": [self._agent.instructions],
                "commands": [],
                "knowledgeIds": [],
                "capabilities": {
                    "sendEmails": False,
                    "internetSearch": False,
                    "querySheet": True,
                    "useAttachedFiles": True
                }
            })

        def _build_new_state(self):
            return self._state['id'] if self._state else self._new_agent_id
