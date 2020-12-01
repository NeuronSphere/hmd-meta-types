Overview
========

HMD Meta Types is designed to provide Python classes that are derived from ``.hms`` type definition files. It also provides an Extension mechanism to provide runtime specfic functionality to those classes.
This allows for a consistent class creation process no matter how the definition files are loaded. The loaded definition file is passed, along with any Extension decorated classes, to the ``build_type_class`` function.
It will return a class derived from the ``MetaType`` metaclass and of the base metatype classes, e.g. ``Noun``.
The class will have all the attributes listed in the definition file as ``Attribute`` instances, and any methods/operations defined on the provided ``Extension`` classes.
It will have common functionality defined on ``MetaType`` and/or metatype base classes, e.g. the class is iterable throught the attributes just as you can iterate over a Python dict's keys.

Direct use of any classes from this library other than ``build_type_class``, and the ``Extension``, ``operation`` decorators is highly discouraged. Furthermore, ``build_type_class`` should almost exclusively be used in ``Loader`` classes that read definition files from a source.
Most users will be creating classes that are decorated with ``@Extension``, which marks the class as an extension and adds the methods necessary to apply it when building the class.
Any class decorated as an Extension will have it's entire class body, excluding dunder methods, merged into the derived class.