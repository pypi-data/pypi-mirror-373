from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple
from uuid import UUID

from highlighter import EAVT, Entity, Observation, TaxonomyMappingRule
from highlighter.agent.capabilities.base_capability import Capability, StreamEvent
from highlighter.client.gql_client import HLClient
from highlighter.core.hl_base_model import HLModelMap


class TaxonomyMapping(Capability):
    """
    Capability for applying taxonomy-mapping rules defined in Highlighter

    Example element definition:
    {
        "name": "Taxonomy Mapping",
        "input": [{ "name": "entities", "type": "Dict[UUID, Entity]" }],
        "output": [{ "name": "entities", "type": "Dict[UUID, Entity]" }],
        "deploy": { "local": { "module": "highlighter.agent.capabilities.taxonomy_mapping",
                               "class_name": "TaxonomyMapping" } },
        "parameters": {
            "mapping_rule_ids": [
                "2891fd3c-47a7-45a8-938f-7ed42f266a7c",
                "72f53bc7-1f24-4462-87de-9943c6fef931"
            },
        }
    }

    """

    class DefaultStreamParameters(Capability.DefaultStreamParameters):
        mapping_rule_ids: List[UUID]

    def __init__(self, context):
        super().__init__(context)
        all_rules = HLClient.get_client().entityAttributeMappingRules(return_type=List[TaxonomyMappingRule])
        mapping_rule_ids, _ = self._get_parameter("mapping_rule_ids")
        self.rules = []
        for rule in all_rules:
            if str(rule.id) in mapping_rule_ids:
                validate_rule(rule)
                self.rules.append(rule)

    def process_frame(self, stream, entities: Dict[UUID, Entity]) -> Tuple[StreamEvent, Dict]:
        if len(set(x.to_entity_attribute.id for x in self.rules)) < len(self.rules):
            raise ValueError("rules shouldn't have overlapping toEntityAttribute")

        for entity in entities.values():
            for rule in self.rules:
                for annotation in entity.annotations:
                    apply_rule(rule, annotation.observations)
                apply_rule(rule, entity.global_observations)

        # 'entities' will be changed by our modifications to the underlying observations
        return StreamEvent.OKAY, {"entities": entities}


def get_value(value, attributeEnum):
    if value is None or value == "":
        if attributeEnum is None:
            return None
        return attributeEnum.id
    return value


def validate_rule(rule: TaxonomyMappingRule):

    if rule.strategy == "direct":
        for map in rule.maps:
            if len(map.predicates) != 1:
                raise ValueError("map for direct strategy should only contain one predicate")
        from_entity_attributes = set(m.predicates[0].from_entity_attribute.id for m in rule.maps)
        if len(from_entity_attributes) != 1:
            raise ValueError(
                f"direct rule should only have one from_entity_attribute, {len(from_entity_attributes)} is received"
            )

        total_number_of_predicates = sum(1 for m in rule.maps for _ in m.predicates)
        unique_values_from_entity_attribute_values = set(
            (p.from_entity_attribute.id, get_value(p.from_value, p.from_entity_attribute_enum))
            for m in rule.maps
            for p in m.predicates
        )

        if len(unique_values_from_entity_attribute_values) < total_number_of_predicates:
            raise ValueError("duplicate values detected in direct rules")

    if rule.strategy == "most_confident":
        for m in rule.maps:
            from_entity_attributes = set(p.from_entity_attribute.id for p in m.predicates)
            if len(from_entity_attributes) != 1:
                raise ValueError(
                    f"each map should have only one from_entity_attribute, {len(from_entity_attributes)}"
                )

    # a rule at least have one predicate
    if len(rule.maps) == 0:
        raise ValueError("this rule has no maps")


def apply_rule(rule: TaxonomyMappingRule, observations: HLModelMap):
    """Apply taxonomy mapping rule"""

    from_attribute_ids = []
    rule.maps = sorted(rule.maps, key=lambda m: m.sort_order)
    for m in rule.maps:
        for p in m.predicates:
            if p.from_entity_attribute.id not in from_attribute_ids:
                from_attribute_ids.append(p.from_entity_attribute.id)

    if rule.strategy == "direct":
        d = {}
        for m in rule.maps:
            for p in m.predicates:
                d[(p.from_entity_attribute.id, get_value(p.from_value, p.from_entity_attribute_enum))] = (
                    get_value(m.to_value, m.to_entity_attribute_enum)
                )
                break

        for observation in observations:
            value = observation.value.id if hasattr(observation.value, "id") else observation.value
            value = str(value) if isinstance(value, UUID) else value
            result = d.get((str(observation.attribute_id), value))
            if result is not None:
                observation.attribute_id = rule.to_entity_attribute.id
                observation.value = result
                break

    elif rule.strategy == "rank":
        d = {}
        for m in rule.maps:
            for p in m.predicates:
                d[(p.from_entity_attribute.id, get_value(p.from_value, p.from_entity_attribute_enum))] = (
                    get_value(m.to_value, m.to_entity_attribute_enum)
                )
                break

        found = False
        for attribute_id in from_attribute_ids:
            if found:
                break
            for observation in observations:
                if observation.attribute_id == attribute_id:
                    value = (
                        str(observation.value) if isinstance(observation.value, UUID) else observation.value
                    )
                    to_value = d.get((str(observation.attribute_id), value))
                    if to_value is not None:
                        observation.attribute_id = rule.to_entity_attribute.id
                        observation.value = to_value
                        found = True
                        break

    elif rule.strategy == "matched":
        d = {}
        for m in rule.maps:
            values = [None] * len(from_attribute_ids)
            for p in m.predicates:
                idx = from_attribute_ids.index(p.from_entity_attribute.id)
                values[idx] = get_value(p.from_value, p.from_entity_attribute_enum)
            d[tuple(values)] = get_value(m.to_value, m.to_entity_attribute_enum)

        _, value, _ = get_value_and_confidence_from_observations(observations, from_attribute_ids)

        for key, _value in d.items():
            found = True
            for left, right in zip(key, value):
                if (left != right) and left is not None:
                    found = False
                    break
            if found:
                observations.add(
                    Observation(
                        entity_id=observations.values()[0].entity_id,
                        attribute_id=rule.to_entity_attribute.id,
                        value=_value,
                        datum_source=observations.values()[0].datum_source,
                        occurred_at=datetime.now(timezone.utc),
                    )
                )
                break

    elif rule.strategy == "most_confident":
        d = {}
        for m in rule.maps:
            for p in m.predicates:
                d[(p.from_entity_attribute.id, get_value(p.from_value, p.from_entity_attribute_enum))] = (
                    get_value(m.to_value, m.to_entity_attribute_enum)
                )
                break

        obs, value, confidence = get_value_and_confidence_from_observations(observations, from_attribute_ids)
        idxes_by_confidence = sorted(list(range(len(confidence))), key=lambda x: -confidence[x])
        sorted_values = [value[i] for i in idxes_by_confidence]
        sorted_attrs = [from_attribute_ids[i] for i in idxes_by_confidence]
        sorted_obs = [obs[i] for i in idxes_by_confidence]
        for idx, attr, value, obs in zip(idxes_by_confidence, sorted_attrs, sorted_values, sorted_obs):
            value = str(value) if isinstance(value, UUID) else value
            result = d.get((attr, value))
            if result is not None:
                obs.attribute_id = rule.to_entity_attribute.id
                obs.value = result
                break

    else:
        raise ValueError(f"Unknown rule strategy {rule.strategy} and no default value provided")

    if (rule.default_value not in [None, ""]) or (rule.default_entity_attribute_enum is not None):
        observations.add(
            Observation(
                entity_id=observations.values()[0].entity_id,
                attribute_id=rule.to_entity_attribute.id,
                value=get_value(rule.default_value, rule.default_entity_attribute_enum),
                datum_source=observations.values()[0].datum_source,
                occurred_at=datetime.now(timezone.utc),
            )
        )

    # Remove unmapped observations
    for observation in observations:
        if observation.attribute_id in from_attribute_ids:
            observations.remove(observation)
            Observation.remove_by_id(observation.id)


def get_value_and_confidence_from_observations(
    observations: Iterable[Observation], attr_ids: List[str]
) -> Tuple[List[Observation], List[Any], List[float]]:
    obs, value, confidence = [None] * len(attr_ids), [None] * len(attr_ids), [0.0] * len(attr_ids)
    for idx, attr_id in enumerate(attr_ids):
        for observation in observations:
            if observation.attribute_id == attr_id:
                value[idx] = observation.value
                value[idx] = getattr(value[idx], "id", value[idx])
                confidence[idx] = observation.datum_source.confidence
                obs[idx] = observation
                break
    return obs, value, confidence
