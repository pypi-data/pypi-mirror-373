def frozen_attrs(*attrs):
    def decorator(cls):
        original_setattr = cls.__setattr__

        def new_setattr(self, name, value):
            if name in attrs and hasattr(self, name):
                raise AttributeError(
                    f"The attribute '{name}' is read-only and cannot be modified."
                )
            return original_setattr(self, name, value)

        cls.__setattr__ = new_setattr
        return cls

    return decorator
