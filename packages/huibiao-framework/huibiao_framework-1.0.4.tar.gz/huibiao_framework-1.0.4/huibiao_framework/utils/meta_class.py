import os


class ConstantClassMeta(type):
    """
    对子类也生效的元类
    """

    def __setattr__(cls, name, value):
        # 检查属性是否已存在且非特殊属性
        if hasattr(cls, name) and not name.startswith("__"):
            raise AttributeError(
                f"The property '{name}' of the constant class {cls.__name__} is not allowed to be modified."
            )

    def __call__(cls, *args, **kwargs):
        raise TypeError(f"The constant class {cls.__name__} cannot be instantiated.")


class ConstantClass(metaclass=ConstantClassMeta):
    pass


class OsAttrMeta(type(ConstantClass), type):
    def __new__(cls, name, bases, attrs):
        for attr in attrs["__annotations__"]:
            raw_value = os.getenv(attr.upper(), attrs.get(attr, None))
            expected_type = attrs["__annotations__"][attr]

            # 根据类型提示转换值
            if expected_type is bool and isinstance(raw_value, str):
                # 将 "false" 转换为 False，"true" 转换为 True
                raw_value = raw_value.lower()
                if raw_value == "true":
                    raw_value = True
                elif raw_value == "false":
                    raw_value = False
                else:
                    raise ValueError(
                        f"Invalid value for boolean attribute '{attr}': {raw_value}"
                    )

            # 如果环境变量不存在，则保持默认值（如果存在）
            attrs[attr] = raw_value if raw_value is not None else attrs.get(attr)

        return super().__new__(cls, name, bases, attrs)
