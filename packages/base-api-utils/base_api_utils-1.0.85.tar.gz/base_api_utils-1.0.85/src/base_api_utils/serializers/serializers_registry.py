class SerializersRegistry:
    _registry = {}

    @classmethod
    def register(cls, name, serializer):
        cls._registry[name] = serializer

    @classmethod
    def get(cls, name):
        return cls._registry.get(name)

    @classmethod
    def list_serializers(cls):
        return list(cls._registry.keys())


def register_serializer(entity_names=None):
    def decorator(cls):
        if entity_names:
            serializer_names = entity_names if isinstance(entity_names, list) else [entity_names]
        else:
            serializer_names = [cls.__name__.replace("Serializer", "").lower()]

        for serializer_name in serializer_names:
            SerializersRegistry.register(serializer_name, cls)

        return cls
    return decorator