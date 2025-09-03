from typing import Optional

from _qwak_proto.qwak.feature_store.entities.entity_pb2 import EntitySpec
from qwak.clients.feature_store import FeatureRegistryClient


class Entity:
    """
    An entity is an object which features sets can be associated with.

    Features created via the feature store are tied to a specific business entity.
    For example registered users, transactions, or merchants.

    Example of an Entity definition:

    .. code-block:: python

        from qwak.feature_store import Entity

        customer = Entity(
            name='organization_id',
            description='An organization which is a customer of our platform',
        )
    """

    def __init__(self, name: str, description: str, key: Optional[str] = None):
        """
        Create a new Entity

        :param name: The name of the entity, must be unique
        :param description: Short human-readable description of the entity
        :param key: The actual key this entity is referring to. Used when user provides a key instead of
                    entity configuration. Currently only a single key is supported.
        """
        self.name = name
        self.description = description
        self.key: Optional[str] = key

    def _to_proto(self):
        return EntitySpec(
            name=self.name,
            keys=[self.name if not self.key else self.key],
            description=self.description,
            value_type=1,  # string
        )

    @classmethod
    def _from_proto(cls, proto):
        entity_spec: EntitySpec = proto.entity_spec

        # entity spec keys is a repeated str but only single key is supported
        keys_repr: str = ",".join(entity_spec.keys)

        return cls(
            name=entity_spec.name,
            description=entity_spec.description,
            key=keys_repr,
        )

    def register(self):
        """
        Explicitly register this entity to Qwak's Feature Store
        """

        registry = FeatureRegistryClient()
        existing_entity = registry.get_entity_by_name(self.name)
        if existing_entity:
            registry.update_entity(
                existing_entity.entity.entity_definition.entity_id,
                self._to_proto(),
            )
        else:
            registry.create_entity(self._to_proto())
