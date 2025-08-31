from threading import Lock
from typing import (
    Type,
    Callable,
    Any,
    overload,
    Protocol,
    Self,
)
from .configreader import ConfigLoader


class _Unset:
    __instance = None

    def __new__(cls) -> "_Unset":
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance


Unset = _Unset()

"""Sentinel used to express "no default provided" for a setting.

When a setting is declared without a default, the library records the default as
``Unset`. During configuration loading, if the key is missing and the setting's
default is `Unset`, the loader will raise a :class:`KeyError`. If a default is
provided (anything other than `Unset`), that value will be used instead.
"""


def split_key(key: str) -> list[str]:
    return key.split(".")


class __Config:
    _singleton = None
    _singleton_lock = Lock()

    def __new__(cls):
        if cls._singleton is None:
            with cls._singleton_lock:
                if (
                    cls._singleton is None
                ):  # Double check since there may be another thread is creating the singleton
                    cls._singleton = super().__new__(cls)
        return cls._singleton

    def __init__(self):
        self.registry: dict[
            type,
            tuple[
                str,
                ConfigLoader | None,
                ConfigLoader | None,
                dict[str, "Setting"],
                Callable[[Any], None] | None,
            ],
        ] = {}

    def __getitem__(self, instance: Any):
        """Another form of the `load` method.

        This method returns an object that loads the configuration for the given instance as another form of the `load` method.

        Example usage:

        ```python
        config[obj].load("config.toml", "env.toml")
        ```

        equivalent to

        ```python
        Config.load(obj, "config.toml", "env.toml")
        ```
        """

        class __SingleConfig:
            def load(self, config_file: str | None = None, env_file: str | None = None):
                """Load the configuration from files and set the settings.

                This method is equivalent to the `load` method of the `Config` class.
                If not provided, the config will be loaded from the default locations.

                Args:
                    config_file: The path to the configuration file.
                    env_file: The path to the environment file. Secret values should be loaded from this file.
                """
                Config.load(instance, config_file, env_file)

            def update(
                self,
                *,
                load_config: ConfigLoader | None = None,
                load_env: ConfigLoader | None = None,
                config_key: str = "",
                postload: Callable[[Any], None] | None = None,
            ):
                """Update the configuration set-ups for a class.

                This method is equivalent to the `update` method of the `Config` class.
                If not provided, the config will be loaded from the default locations.

                Args:
                    load_config: A callable that reads the configuration file and returns a dictionary.
                    load_env: A callable that reads the secret config values and returns a dictionary.
                    config_key: The config key to use for this class. If provided, only the parts of the config file that correspond to this key will be loaded.
                    postload: A callable that is executed after loading the configuration for the instance.
                """
                Config.update(
                    instance,
                    load_config=load_config,
                    load_env=load_env,
                    config_key=config_key,
                    postload=postload,
                )

        return __SingleConfig()

    def register[T](
        self,
        klass: Type[T],
        load_config: ConfigLoader | None = None,
        *,
        load_env: ConfigLoader | None = None,
        config_key: str = "",
        postload: Callable[[Any], None] | None = None,
    ):
        """Register a class with a config key.

        This method books the class in the registry with a optional config key. `load_config` will be used to load the config file
        and `load_env`, if provided, will be used to load secret values from a separate config file or environment variables.

        Args:
            klass: The class to register
            load_config: A callable that reads the configuration file and returns a dictionary.
            load_env: A callable that reads the secret config values and returns a dictionary.
            config_key: The config key to use for this class. If provided, only the parts of the config file that correspond to this key will be loaded.
            postload: A callable that is executed after loading the configuration for instances of this class.
        """
        self.registry[klass] = (config_key, load_config, load_env, {}, postload)

    def update[T](
        self,
        klass: Type[T],
        *,
        load_config: ConfigLoader | None = None,
        load_env: ConfigLoader | None = None,
        config_key: str = "",
        postload: Callable[[Any], None] | None = None,
    ):
        """Update the config registry of a class.

        This method updates the config registry of a class with a optional config key. `load_config` will be used to load the config file
        and `load_env`, if provided, will be used to load secret values from a separate config file or environment variables.
        A class will be registered if it isn't in the registries before.

        Args:
            klass: The class to register
            load_config: A callable that reads the configuration file and returns a dictionary.
            load_env: A callable that reads the secret config values and returns a dictionary.
            config_key: The config key to use for this class. If provided, only the parts of the config file that correspond to this key will be loaded.
            postload: A callable that is executed after loading the configuration for instances of this class.
        """

        if klass not in self.registry:
            self.register(
                klass,
                load_config,
                load_env=load_env,
                config_key=config_key,
                postload=postload,
            )
        else:
            (config_key0, load_config0, load_env0, settings, postload0) = self.registry[
                klass
            ]
            config_key1 = config_key if config_key else config_key0
            load_config1 = load_config if load_config is not None else load_config0
            load_env1 = load_env if load_env is not None else load_env0
            postload1 = postload if postload is not None else postload0
            self.registry[klass] = (
                config_key1,
                load_config1,
                load_env1,
                settings,
                postload1,
            )

    def contains[T](self, klass: Type[T], config_key: str) -> bool:
        """Check if a class is registered with a config key.

        This method checks if the class is registered with the given config key. If the class is not registered, a ValueError will be raised.

        Args:
            klass: The class to check
            config_key: The config key to use for this class. If provided, only the parts of the config file that correspond to this key will be loaded.
        """
        return klass in self.registry and self.registry[klass][0] == config_key

    def add_setting[I, V](
        self, klass: Type[I], config_key: str, setting: "Setting[I, V]"
    ):
        """Add a setting to a class.

        This method adds a setting to the class. The setting should be an instance of the Setting class.
        Old settings, if present, will be replaced.

        Args:
            klass: The class to add the setting to
            config_key: The config key to use for this setting. If provided, only the parts of the config file that correspond to this key will be loaded.
            setting: The setting to add
        """

        if klass not in self.registry:
            raise ValueError(f"Class {klass} is not registered")
        self.registry[klass][3][config_key] = setting

    def get_setting[I](self, klass: Type[I], config_key: str) -> "Setting[I, Any]":
        """Get the settings for a class with a config key.

        This method returns the settings for the class with the given config key. If the class is not registered, a ValueError will be raised.

        Args:
            klass: The class to get the settings for
            config_key: The config key to use for this class. If provided, only the parts of the config file that correspond to this key will be loaded.
        """
        if klass not in self.registry:
            raise ValueError(f"Class {klass} is not registered")
        if config_key not in self.registry[klass][3]:
            raise ValueError(
                f"Config key {config_key} is not registered for class {klass}"
            )
        return self.registry[klass][3][config_key]

    def load(
        self, instance: Any, config_file: str | None = None, env_file: str | None = None
    ):
        """Load the configuration from files and set the settings.

        If not provided, the config will be loaded from the default locations.
        After loading all settings, if a postload function was registered for the class,
        it will be called with the instance as an argument.

        Args:
            instance: The instance of the class to load the configuration for.
            config_file: The path to the configuration file.
            env_file: The path to the environment file. Secret values should be loaded from this file.
        """
        klass = type(instance)

        # Find all settings from the class hierarchy
        all_settings: dict[str, "Setting"] = {}
        config_key = ""
        load_config = None
        load_env = None
        postload = None

        # Search through the Method Resolution Order (MRO) to find all registered settings
        for cls in klass.__mro__:
            if cls in self.registry:
                (
                    cls_config_key,
                    cls_load_config,
                    cls_load_env,
                    cls_settings,
                    cls_postload,
                ) = self.registry[cls]

                # Use the most specific (first found) configuration loader and config key
                if load_config is None:
                    config_key = cls_config_key
                    load_config = cls_load_config
                    load_env = cls_load_env
                    postload = cls_postload

                # Add settings from this class (more specific settings override parent settings)
                for setting_key, setting in cls_settings.items():
                    if setting_key not in all_settings:
                        all_settings[setting_key] = setting

        if not all_settings:
            # No settings found in any parent class
            return

        if load_config is None:
            raise ValueError(
                f"Config file loader is not provided for class {klass} or any of its parent classes. Please provide one."
            )

        def __load_key(key: str, config: dict):
            current_config = config
            for key in split_key(key):
                if key not in current_config:
                    raise KeyError(f"Key {key} not found in configuration file")
                current_config = current_config[key]
            return current_config

        def __merge_config(config1: dict, config2: dict) -> dict:
            """Recursively merge two dictionaries.

            When there are overlapping keys, if both values are dictionaries, they are merged recursively.
            Otherwise, the value from config2 overwrites the value from config1.

            Args:
                config1: The base dictionary
                config2: The dictionary to merge on top of config1

            Returns:
                A new dictionary with merged values
            """
            result = config1.copy()

            for key, value in config2.items():
                if (
                    key in result
                    and isinstance(result[key], dict)
                    and isinstance(value, dict)
                ):
                    # If both values are dictionaries, merge them recursively
                    result[key] = __merge_config(result[key], value)
                else:
                    # Otherwise, overwrite the value
                    result[key] = value

            return result

        config = load_config(config_file)
        if load_env:
            env_config = load_env(env_file)
            config = __merge_config(config, env_config)
        else:
            if env_file:
                raise ValueError(
                    "The configurable doesn't accept a separate environment file"
                )

        if config_key:
            route = split_key(config_key)
            for key in route:
                if key not in config:
                    raise KeyError(f"Key {key} not found in configuration file")
                config = config[key]

        for key, setting in all_settings.items():
            keyerror = None
            try:
                value = __load_key(key, config)
            except KeyError as e:
                keyerror = e
            if setting.fset is None:
                raise NotImplementedError(
                    f"Setting {key} does not have a setter method. Please implement a setter method for this setting."
                )
            if keyerror is None:
                setting.fset(instance, value)
            else:
                if setting.default is Unset:
                    raise keyerror
                else:
                    setting.fset(instance, setting.default)

        if postload is not None:
            postload(instance)


Config = __Config()
config = __Config()


class Setting[I, V]:
    """Represents a configurable attribute.

    The setting object holds a getter and setter used to read and write an
    attribute on an instance, and an optional `default` value which will be
    applied at configuration load time when the corresponding key is missing.

    If `default` is the `Unset` sentinel the setting is treated as required
    and the loader will raise a :class:`KeyError` when the key is absent.
    """

    def __init__(
        self,
        fget: Callable[[I], V] | None = None,
        fset: Callable[[I, V], None] | None = None,
        default: _Unset | Any = Unset,
    ):
        self.fget = fget
        self.fset = fset
        self.default = default

    def __get__(self, instance: I | None, owner: Type[I]) -> V:
        if self.fget is None:
            raise NotImplementedError(
                "Setting does not have a getter method. Please implement a getter method for this setting."
            )
        if instance is None:
            raise NotImplementedError(
                "Setting does not have a getter method. Please implement a getter method for this setting."
            )
        return self.fget(instance)

    def __set__(self, instance: I, value: V) -> None:
        if self.fset is None:
            raise NotImplementedError(
                "Setting does not have a setter method. Please implement a setter method for this setting."
            )
        self.fset(instance, value)


def configurable(
    load_config: ConfigLoader,
    *,
    config_key: str = "",
    load_env: ConfigLoader | None = None,
    postload: Callable[[Any], None] | None = None,
):
    """Decorator to register a class as configurable.

    This decorator registers the class with the config key and loads the configuration from the file.
    The class should have a `__init__` method that takes no arguments.

    Args:
        config_key: The config key to use for this class. If provided, only the parts of the config file that correspond to this key will be loaded.
        load_config: A callable that reads the configuration file and returns a dictionary.
        load_env: A callable that reads the secret config values and returns a dictionary.
        postload: A callable that is executed after loading the configuration. If provided, it will also be registered as a member function of the class.
    """

    def decorator[T: Type](cls: T) -> T:
        Config.update(
            cls,
            load_config=load_config,
            load_env=load_env,
            config_key=config_key,
            postload=postload,
        )
        if postload is not None:
            cls.postload = postload
        return cls

    return decorator


class Descriptor[I, V](Protocol):
    def __init__(self, method: Callable[[I], V]) -> None: ...

    def __set_name__(self, owner: Type[I], name: str) -> None: ...

    @overload
    def __get__(self, instance: None, owner: Type[I]) -> "Descriptor": ...

    @overload
    def __get__(self, instance: I, owner: Type[I]) -> V: ...

    def __get__(self, instance: I | None, owner: Type[I]) -> "V | Descriptor": ...

    def __set__(self, instance: I, value: V) -> None: ...

    def setter(self, fset: Callable[[I, V], None]) -> "Descriptor[I, V]":
        """Decorator to register a method as a setting setter.

        Note that due to unknown reasons, the setter must be of a different name of the getter, or otherwise
        the type checkers (at least the one used by VSCode) will report a obscured method name error. This is
        different from the built-in `property.setter` decorator.

        Args:
            fset: The setter method to register as a setting setter.
        """
        ...


def mangle_attr(the_self, attr):
    """Mangle attribute name according to Python's name mangling rules.

    Args:
        the_self: The instance or class to mangle the attribute for.
        attr: The attribute name to mangle.

    Returns:
        The mangled attribute name.
    """
    # return public attrs unchanged
    if not attr.startswith("__") or attr.endswith("__") or "." in attr:
        return attr
    # if source is an object, get the class
    if not hasattr(the_self, "__bases__"):
        the_self = the_self.__class__
    # mangle attr
    return f"_{the_self.__name__.lstrip('_')}{attr}"


def find_mangled_attr(instance, attr_name):
    """Find a mangled attribute by searching through the inheritance hierarchy.

    This function searches for a mangled attribute starting with the instance's class
    and moving up the inheritance hierarchy until it finds the attribute or exhausts
    all parent classes.

    Args:
        instance: The instance to search for the attribute on.
        attr_name: The unmangle attribute name (e.g., "__field_name").

    Returns:
        The value of the found attribute.

    Raises:
        AttributeError: If the attribute is not found in any class in the hierarchy.
    """
    # return public attrs unchanged
    if not attr_name.startswith("__") or attr_name.endswith("__") or "." in attr_name:
        return getattr(instance, attr_name)

    # Get the class hierarchy (MRO - Method Resolution Order)
    cls = instance.__class__
    for klass in cls.__mro__:
        mangled_name = f"_{klass.__name__.lstrip('_')}{attr_name}"
        if hasattr(instance, mangled_name):
            return getattr(instance, mangled_name)

    # If not found in any class, raise AttributeError
    raise AttributeError(
        f"'{cls.__name__}' object has no attribute '{attr_name}' (searched through inheritance hierarchy)"
    )


class __setting:
    _singleton = None
    _singleton_lock = Lock()

    def __new__(cls):
        if cls._singleton is None:
            with cls._singleton_lock:
                if cls._singleton is None:
                    cls._singleton = super().__new__(cls)
        return cls._singleton

    def __init__(self):
        pass

    def __call__[T, S](
        self, config_key: str, *, default: _Unset | Any = Unset
    ) -> Callable[[Callable[[T], S]], Descriptor[T, S]]:
        """Return a decorator that makes a method into a configurable setting.

        Parameters
        - config_key: dotted key in the config dict to load for this setting.
        - default: optional default used when the key is absent. If not provided
          (the sentinel `Unset`), the loader treats the setting as required and
          will raise `KeyError` when loading if the key is missing.

        Returns
        - A decorator that transforms a method into a descriptor exposing the
          setting's getter and setter and registers it with the global `Config`.
        """

        class __decorator[I, V]:
            # XXX: Could we refine `default` to a more specific type?
            def __init__(self, method: Callable[[I], V], default: _Unset | Any = Unset):
                self.method = method
                name = self.method.__name__
                attr_name = f"__{name}"

                def fget(the_self: Any) -> V:
                    return find_mangled_attr(the_self, attr_name)

                def fset(the_self: Any, value: V) -> None:
                    setattr(the_self, mangle_attr(the_self, attr_name), value)

                s = Setting(fget=fget, fset=fset, default=default)
                self.setting: Setting[Any, V] = s

            def __set_name__(self, owner: Type[I], name: str):
                # The `setting` decorator will be invoked before the `configurable` decorator.
                #  We must guarantee the existence of the registry.
                Config.update(owner)
                Config.add_setting(owner, config_key, self.setting)

            @overload
            def __get__(self, instance: I, owner: Type[I]) -> V:
                if self.setting.fget is None:
                    raise NotImplementedError(
                        f"Setting {self.method.__name__} does not have a getter method. Please implement a getter method for this setting."
                    )
                return self.setting.fget(instance)

            @overload
            def __get__(self, instance: None, owner: Type[Any]) -> "__decorator":
                raise NotImplementedError(
                    f"Setting {self.method.__name__} does not have a getter method. Please implement a getter method for this setting."
                )

            def __get__(self, instance: I | None, owner: Type[I]) -> "V | __decorator":
                if instance is None:
                    raise ValueError(
                        "Setting getter cannot be called on the class itself. Please call it on an instance of the class."
                    )
                if self.setting.fget is None:
                    raise NotImplementedError(
                        f"Setting {self.method.__name__} does not have a getter method. Please implement a getter method for this setting."
                    )
                return self.setting.fget(instance)

            def __set__(self: Self, instance: I, value: V):
                if self.setting.fset is None:
                    raise NotImplementedError(
                        f"Setting {self.method.__name__} does not have a setter method. Please implement a setter method for this setting."
                    )
                self.setting.fset(instance, value)

            def setter(self: Self, fset: Callable[[I, V], None]) -> "__decorator[I, V]":
                raise NotImplementedError(
                    f"Setting {self.method.__name__} already has a setter method. You cannot add another!"
                )

        # The wrapper is only to please the type checker
        def __wrapper(method: Callable[[T], S]) -> __decorator[T, S]:
            return __decorator(method, default=default)

        return __wrapper

    def getter[T, S](
        self, config_key: str, *, default: _Unset | Any = Unset
    ) -> Callable[[Callable[[T], S]], Descriptor[T, S]]:
        """Decorator to register a method as a setting getter."""

        class __getter[I, V]:
            def __init__(
                self, method: Callable[[I], V], *, default: _Unset | V = Unset
            ):
                self.method = method
                s = Setting(fget=self.method, fset=None, default=default)
                self.setting = s

            def __set_name__(self, owner: Type[I], name: str):
                Config.update(owner)
                if Config.contains(owner, config_key):
                    raise ValueError(
                        f"Config key {config_key} is already registered for class {owner}"
                    )
                Config.add_setting(owner, config_key, self.setting)

            @overload
            def __get__(self, instance: I, owner: Type[I]) -> V:
                if self.setting.fget is None:
                    raise NotImplementedError(
                        f"Setting {self.method.__name__} does not have a getter method. Please implement a getter method for this setting."
                    )
                return self.setting.fget(instance)

            @overload
            def __get__(self, instance: None, owner: Type[I]) -> "__getter":
                raise NotImplementedError(
                    f"Setting {self.method.__name__} does not have a getter method. Please implement a getter method for this setting."
                )

            def __get__(self, instance: I | None, owner: Type[I]) -> "V | __getter":
                if instance is None:
                    raise ValueError(
                        "Setting getter cannot be called on the class itself. Please call it on an instance of the class."
                    )
                if self.setting.fget is None:
                    raise NotImplementedError(
                        f"Setting {self.method.__name__} does not have a getter method. Please implement a getter method for this setting."
                    )
                return self.setting.fget(instance)

            def __set__(self, instance: I, value: V):
                if self.setting.fset is None:
                    raise NotImplementedError(
                        f"Setting {self.method.__name__} does not have a setter method. Please implement a setter method for this setting."
                    )
                self.setting.fset(instance, value)

            def setter(self, fset: Callable[[I, V], None]) -> "__getter[I, V]":
                self.setting.fset = fset
                return self

        def __wrapper(method: Callable[[T], S]) -> __getter[T, S]:
            return __getter(method, default=default)

        return __wrapper


setting = __setting()
