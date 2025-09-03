from typing import ClassVar, Dict, Type, Any
from pydantic import BaseModel, GetCoreSchemaHandler, model_serializer, field_validator
from pydantic_core import core_schema
from .extension_manager import ExtensionManager
from .expression_evaluator import ExpressionEvaluator
from .expression_policy import ExpressionEvaluationPolicy


class ExpressionEnabledModel(BaseModel):
    @field_validator("*", mode="before")
    @classmethod
    def _evaluate_expressions(cls, v, info):
        """
        Evaluate expressions in field values before validation.

        This validator is called for every field before normal validation
        and works recursively because nested ResourceConfig objects
        are validated with the same rules.

        Policy can be controlled by setting 'expression_evaluation_policy' in the
        validation context to an ExpressionEvaluationPolicy enum value.
        """
        # Get the policy from validation context
        policy = ExpressionEvaluationPolicy.EVALUATE  # default
        if info and info.context:
            policy_value = info.context.get("expression_evaluation_policy")
            if isinstance(policy_value, ExpressionEvaluationPolicy):
                policy = policy_value
            elif policy_value == "literal":
                policy = ExpressionEvaluationPolicy.LITERAL
            elif policy_value == "error":
                policy = ExpressionEvaluationPolicy.ERROR
            elif info.context.get("disable_expression_evaluation", False):
                # Backward compatibility
                policy = ExpressionEvaluationPolicy.LITERAL

        # Apply policy
        if policy == ExpressionEvaluationPolicy.LITERAL:
            return v
        elif policy == ExpressionEvaluationPolicy.ERROR:
            if ExpressionEvaluator.is_expression(v):
                raise ValueError(f"Expression found but evaluation is not allowed: {v}")
            return v
        else:  # EVALUATE
            return ExpressionEvaluator.evaluate(v)


class ResourceConfig(BaseModel):
    """
    Base class for polymorphic Pydantic models with smart deserialization and recursive serialization.
    - Supports type-based dispatch for model creation.
    - Recursively serializes all nested models, including polymorphic fields.
    """

    type: str
    _registry: ClassVar[Dict[str, Type["ResourceConfig"]]] = {}

    @field_validator("*", mode="before")
    @classmethod
    def _evaluate_expressions(cls, v, info):
        """
        Evaluate expressions in field values before validation.

        This validator is called for every field before normal validation
        and works recursively because nested ResourceConfig objects
        are validated with the same rules.

        Policy can be controlled by setting 'expression_evaluation_policy' in the
        validation context to an ExpressionEvaluationPolicy enum value.
        """
        # Get the policy from validation context
        policy = ExpressionEvaluationPolicy.EVALUATE  # default
        if info and info.context:
            policy_value = info.context.get("expression_evaluation_policy")
            if isinstance(policy_value, ExpressionEvaluationPolicy):
                policy = policy_value
            elif policy_value == "literal":
                policy = ExpressionEvaluationPolicy.LITERAL
            elif policy_value == "error":
                policy = ExpressionEvaluationPolicy.ERROR
            elif info.context.get("disable_expression_evaluation", False):
                # Backward compatibility
                policy = ExpressionEvaluationPolicy.LITERAL

        # Apply policy
        if policy == ExpressionEvaluationPolicy.LITERAL:
            return v
        elif policy == ExpressionEvaluationPolicy.ERROR:
            if ExpressionEvaluator.is_expression(v):
                raise ValueError(f"Expression found but evaluation is not allowed: {v}")
            return v
        else:  # EVALUATE
            # Get the target type for type-aware evaluation
            target_type = None
            if info and info.field_name and info.field_name in cls.model_fields:
                field_info = cls.model_fields[info.field_name]
                if hasattr(field_info, "annotation"):
                    annotation = field_info.annotation
                    if annotation in (int, float, bool):
                        target_type = annotation

            return ExpressionEvaluator.evaluate(v, target_type)

    @model_serializer
    def serialize_model(self) -> dict:
        """
        Custom serializer to ensure polymorphic types serialize all their fields,
        even when embedded in other Pydantic models.

        This fixes the issue where ResourceConfig subclasses lose their specific
        fields when serialized as part of other models due to Pydantic using
        the base class schema for nested serialization.
        """
        # Use the custom recursive model dump that properly handles polymorphic types
        return self._recursive_model_dump()

    def model_dump_json(self, *args, **kwargs):
        import json

        return json.dumps(self.model_dump(*args, **kwargs), *args, **kwargs)

    def model_dump(self, *args, **kwargs):
        return self._recursive_model_dump(*args, **kwargs)

    def _recursive_model_dump(self, *args, by_alias: bool | None = None, **kwargs):
        data = {}
        for name, field in self.__class__.model_fields.items():
            try:
                # Try to get the value safely
                value = getattr(self, name)
            except AttributeError:
                # If the field doesn't exist on this instance, skip it
                # This can happen when polymorphic dispatch creates inconsistent instances
                continue

            field_name = (
                field.alias if by_alias is True and field and field.alias else name
            )
            if isinstance(value, ResourceConfig):
                data[field_name] = value._recursive_model_dump(
                    *args, by_alias=by_alias, **kwargs
                )
            elif isinstance(value, BaseModel):
                data[field_name] = value.model_dump(*args, by_alias=by_alias, **kwargs)
            elif isinstance(value, list):
                data[field_name] = [
                    (
                        v._recursive_model_dump(*args, by_alias=by_alias, **kwargs)
                        if isinstance(v, ResourceConfig)
                        else (
                            v.model_dump(*args, **kwargs)
                            if isinstance(v, BaseModel)
                            else v
                        )
                    )
                    for v in value
                ]
            elif isinstance(value, dict):
                data[field_name] = {
                    k: (
                        v._recursive_model_dump(*args, by_alias=by_alias, **kwargs)
                        if isinstance(v, ResourceConfig)
                        else (
                            v.model_dump(*args, by_alias=by_alias, **kwargs)
                            if isinstance(v, BaseModel)
                            else v
                        )
                    )
                    for k, v in value.items()
                }
            else:
                data[field_name] = value
        return data

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        name = getattr(cls, "type", None) or cls.__name__
        ResourceConfig._registry[name] = cls
        if "type" not in cls.__annotations__:
            cls.__annotations__["type"] = str
        if not hasattr(cls, "model_fields") or "type" not in getattr(
            cls, "model_fields", {}
        ):
            cls.type = name

    def __new__(cls, **kwargs):
        """Handle polymorphic instantiation during direct construction."""
        # Apply polymorphic dispatch when a 'type' parameter is provided
        # and there's a registered subclass for that type
        if "type" in kwargs:
            type_name = kwargs["type"]

            # 1) fast path – already registered?
            sub = cls._registry.get(type_name)
            if sub and sub is not cls and issubclass(sub, cls):
                return sub(**kwargs)

            # 2) try to load the matching plugin lazily
            ExtensionManager.lazy_load_plugin_for_type(type_name)

            # 3) second attempt after lazy load
            sub = cls._registry.get(type_name)
            if sub and sub is not cls and issubclass(sub, cls):
                return sub(**kwargs)

        # Default behavior - create instance of the requested class
        return super().__new__(cls)

    @classmethod
    def __get_pydantic_core_schema__(cls, source: Any, handler: GetCoreSchemaHandler):
        base = handler(source)

        def _dispatch(value, next_, info):
            if isinstance(value, cls):
                return value

            # Apply polymorphic dispatch for dict inputs during model_validate
            # and model_validate_json, but not during __init__
            # __init__ is now handled by __new__ method above
            if isinstance(value, dict) and "type" in value:
                type_name = value["type"]

                # Check if there's a more specific subclass registered for this type
                sub = cls._registry.get(type_name)
                if sub and sub is not cls and issubclass(sub, cls):
                    # 1) fast path – already registered?
                    # Pass along the validation context when doing polymorphic dispatch
                    return sub.model_validate(
                        value, context=info.context if info else None
                    )

                # 2) try to load the matching plugin lazily
                ExtensionManager.lazy_load_plugin_for_type(type_name)

                # 3) second attempt after lazy load
                sub = cls._registry.get(type_name)
                if sub and sub is not cls and issubclass(sub, cls):
                    return sub.model_validate(
                        value, context=info.context if info else None
                    )

            # fallback – let pydantic handle / raise
            return next_(value)

        return core_schema.with_info_wrap_validator_function(_dispatch, base)
