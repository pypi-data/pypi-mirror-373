from usdm4.api.api_base_model import ApiBaseModelWithId


class PathError(Exception):
    pass


class DuplicateError(Exception):
    pass


class CrossReference:
    def __init__(self):
        self._by_name = {}
        self._by_id = {}

    def clear(self):
        self._by_name = {}
        self._by_id = {}

    def add(self, object: ApiBaseModelWithId, name: str) -> None:
        name = object.name if hasattr(object, "name") else name
        if name:
            self._add_to_collection(name, self._by_name, object)
        self._add_to_collection(object.id, self._by_id, object)

    def _add_to_collection(self, key_text: str, collection: dict, object):
        if key_text:
            klass = object.__class__
            key = self._key(klass, key_text)
            if key not in collection:
                collection[key] = object
            else:
                raise DuplicateError(
                    f"Duplicate cross reference detected, klass='{self._klass_name(klass)}', key='{key_text}'"
                )

    def get_by_name(self, klass, name: str) -> ApiBaseModelWithId:
        return self._get(klass, name, self._by_name)

    def get_by_id(self, klass, id: str) -> ApiBaseModelWithId:
        return self._get(klass, id, self._by_id)

    def _get(self, klass, key_text: str, collection: dict) -> ApiBaseModelWithId:
        key = self._key(klass, key_text)
        if key in collection:
            return collection[key]
        else:
            return None

    def get_by_path(self, klass, name, path):
        instance = self.get_by_name(klass, name)
        if instance:
            parts = path.split("/")
            attribute = parts[0].replace("@", "")
            if len(parts) == 1:
                return instance, attribute
            elif len(parts) % 2 == 1:
                for index in range(1, len(parts), 2):
                    try:
                        instance = getattr(instance, attribute)
                    except AttributeError:
                        raise PathError(
                            f"Failed to translate reference path '{path}', attribute '{attribute}' was not found"
                        )
                    attribute = parts[index + 1].replace("@", "")
                    if not parts[index] == instance.__class__.__name__:
                        raise PathError(
                            f"Failed to translate reference path '{path}', class mismtach, expecting '{parts[index]}', found '{instance.__class__.__name__}'"
                        )
                if instance and attribute:
                    if not self.get_by_id(instance.__class__, instance.id):
                        self.add(instance.id, instance)
                    return instance, attribute
                else:
                    raise PathError(
                        f"Failed to translate reference path '{path}', path was not found"
                    )
            else:
                raise PathError(
                    f"Failed to translate reference path '{path}', format error"
                )
        else:
            raise PathError(
                f"Failed to translate reference path '{path}', could not find start instance '{klass}', '{name}'"
            )

    def _key(self, klass, text: str) -> str:
        klass_name = self._klass_name(klass)
        return f"{klass_name}.{text}"

    def _klass_name(self, klass):
        return klass if isinstance(klass, str) else klass.__name__
