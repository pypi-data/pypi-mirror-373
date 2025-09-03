from abc import ABC, abstractmethod
import time


class Synchronizer(ABC):

    def __init__(self, kawa, icon, entity_description, entity_tag=None):
        self._k = kawa
        self._icon = icon
        self._entity_description = entity_description
        self._tag = entity_tag
        self._state = None
        self._step_id = 0

    def sync(self):
        start = time.time()
        self._step('Start Synchronization')

        self._step('Loading State')
        self._state = self._load_state()

        self._step('Checking State')
        self._raise_if_state_invalid()

        if self._should_create():
            self._step('Creating a new object')
            self._create_new_entity()
        else:
            self._step('Updating existing object')
            self._update_entity()

        new_state = self._build_new_state()
        end = time.time()
        self._step(f'Synchronization done in {end - start:.1f}s')

        return new_state

    def _step(self, step):
        self._step_id += 1
        if self._step_id == 1:
            tag = f' (🏷️{self._tag})' if self._tag else ''
            print(f'{self._icon} {self._entity_description}{tag}:')
        print(f'   {step}')

    @abstractmethod
    def _load_state(self):
        ...

    @abstractmethod
    def _raise_if_state_invalid(self):
        ...

    @abstractmethod
    def _should_create(self):
        ...

    @abstractmethod
    def _create_new_entity(self):
        ...

    @abstractmethod
    def _update_entity(self):
        ...

    @abstractmethod
    def _build_new_state(self):
        ...
