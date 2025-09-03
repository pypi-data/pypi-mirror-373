#!/usr/bin/env python

from typing import Any, Callable, Dict, Final, List, Optional, Tuple, Union

from pyoverinspect.overinspect import get_fct_parameter_names

from .tool_functions import get_uuid

DICTFLAT_VERSION: Final[List[str]] = ['0', '1', '9']
DICTFLAT_FULL_VERSION: Final[str] = '.'.join(DICTFLAT_VERSION)


RENAME_ALL: Final[str] = '__\x01__all__'
CHANGE_ROOT: Final[str] = '__\x01__root__'
INNER_SUFFIX: Final[str] = '__inner'
ID_FIELD_NAME: Final[str] = '__id'
REF_FIELD_PREFIX: Final[str] = '__ref__'
CONTEXT_DEPTH: Final[str] = '__\x01__depth'
CONTEXT_PATH: Final[str] = '__\x01__path'
CONTEXT_ELEMENT: Final[str] = '__\x01__element'


class DictFlat():

    def __init__(self,
                 flat_dict_key: str = '',
                 sep: str = '.',
                 id_field_name: str = ID_FIELD_NAME,
                 ref_field_prefix: str = REF_FIELD_PREFIX,
                 rename: Optional[Dict[str, Union[str, Callable]]] = None,
                 drop: Optional[Union[str, List[str]]] = None,
                 change: Optional[Dict[str, Callable]] = None,
                 object_prefix: Optional[str] = None,
                 root_key: str = '',
                 list_2_object: Optional[Dict[str, Dict]] = None,
                 dict_of_dicts_2_dict: Optional[Dict[str, Dict]] = None,
                 fct_build_id: Optional[Callable] = None,
                 inner_suffix: str = INNER_SUFFIX,
                 simple_keys: bool = False,
                 context: Optional[Dict] = None) -> None:

        self.flat_dict_key: str = flat_dict_key
        self.sep: str = sep
        self.id_field_name: str = id_field_name
        self.ref_field_prefix: str = ref_field_prefix
        if not rename:
            rename = None
        self.rename: Optional[Dict[str, Union[str, Callable]]] = rename
        if not drop:
            drop = None
        elif not isinstance(drop, list):
            drop = [drop]
        self.drop: Optional[List[str]] = drop
        self.change: Optional[Dict[str, Callable]] = change
        self.object_prefix: Optional[str] = object_prefix
        self.root_key: str = root_key
        self.list_2_dict: Optional[Dict[str, Dict]] = list_2_object
        self.dd_2_dict: Optional[Dict[str, Dict]] = dict_of_dicts_2_dict
        self.fct_build_id: Optional[Callable] = fct_build_id
        self.inner_suffix: str = inner_suffix
        self.inner_sep_suffix: Final[str] = '%s%s' % (self.sep, self.inner_suffix)
        self.inner_sep_suffix_len: Final[int] = len(self.inner_sep_suffix)
        self.simple_key: bool = simple_keys
        if context is None:
            self.context: Dict[str, Any] = {}
        else:
            self.context: Dict[str, Any] = context
        self.context[CONTEXT_DEPTH] = 0

    def __init_flat_dict_list(self, global_dict_key: str) -> None:
        """Initialize the list of flatten dicts if the global result dict if not already initialized

        Args:
            flat_dict_key (str): The flatten dict key
        """
        if self.flat_dict_result.get(global_dict_key, None) is None:
            self.flat_dict_result[global_dict_key] = []

    def __make_dict_name(self,
                         dict_name) -> str:
        return '%s%s' % (self.ref_field_prefix, dict_name)

    def __build_id(self, d: Dict, path: str) -> Any:
        if not self.fct_build_id:
            return get_uuid()
        else:
            fct: Callable = self.fct_build_id
            if 'context' in get_fct_parameter_names(fct):
                return fct(d=d, path=path, context=self.context)
            else:
                return fct(d=d, path=path)

    def __build_new_flat_dict(self,
                              d: Dict,
                              path: str,
                              father_path: Optional[str] = None,
                              father_id: Any = None) -> Dict[str, Any]:
        """Initialize a new flatten dict and add it to the list

        Args:
            flat_dict_key (str): The global result dict key.
            father_dict_name (Optional[str], optional): The father dict key name. Defaults to None.
            father_dict_id (Optional[str], optional): The father dict key id. Defaults to None.

        Returns:
            Dict[str, Any]: The new flatten dict
        """
        new_dict: Dict[str, Any] = {
            self.id_field_name: self.__build_id(d=d, path=path)
        }

        if father_path and father_id:
            new_dict[self.__make_dict_name(dict_name=father_path)] = father_id

        self.flat_dict_result[path].append(new_dict)

        return new_dict

    def __build_new_path(self,
                         field_name: str,
                         path: Optional[str] = None) -> str:
        new_path: Optional[str] = None
        if path is None or self.simple_key:
            new_path = field_name
        else:
            new_path = '%s%s%s' % (path, self.sep, field_name)
        return new_path

    def __is_drop(self, value_path: str) -> bool:
        return bool(self.drop) and value_path in self.drop

    def __change_value(self, cur_value: Any, value_path: str) -> Any:
        new_value: Any = cur_value
        if self.change and value_path in self.change:
            fct_change_value: Callable = self.change[value_path]
            if 'context' in get_fct_parameter_names(fct_change_value):
                new_value = fct_change_value(fieldname=value_path, value=cur_value, context=self.context)
            else:
                new_value = fct_change_value(fieldname=value_path, value=cur_value)
        return new_value

    def __rename_path(self, path: str) -> str:
        new_path: str = path
        if self.rename:
            if RENAME_ALL in self.rename:
                fct: Union[str, Callable] = self.rename[RENAME_ALL]
                if isinstance(fct, Callable):
                    if new_path.endswith(self.inner_sep_suffix):
                        new_path = fct(new_path[:-self.inner_sep_suffix_len]) + self.inner_sep_suffix
                    else:
                        if 'context' in get_fct_parameter_names(fct):
                            new_path = fct(new_path, context=self.context)
                        else:
                            new_path = fct(new_path)
            if new_path in self.rename:
                fct_or_str: Union[str, Callable] = self.rename[new_path]
                if isinstance(fct_or_str, str):
                    new_path = fct_or_str
                else:
                    if 'context' in get_fct_parameter_names(fct_or_str):
                        new_path = fct_or_str(new_path, context=self.context)
                    else:
                        new_path = fct_or_str(new_path)
        return new_path

    def __flat_list_or_tuple(self,
                             lt: Union[List, Tuple],
                             path: str,
                             father_path: Optional[str] = None,
                             father_id: Any = None) -> None:

        extra: Dict = {}
        counter_flag: bool = False
        counter_field: str = ""
        if self.list_2_dict and path in self.list_2_dict:
            l2d_def: Dict = self.list_2_dict[path]
            counter_field = l2d_def.get('counter_field', 'idx')
            starts_at: int = l2d_def.get('starts_at', 1)
            if counter_field and starts_at is not None:
                extra[counter_field] = starts_at
                counter_flag = True

        for elt in lt:

            self.context[CONTEXT_ELEMENT] = elt
            self.context[CONTEXT_PATH] = path

            if not isinstance(elt, dict):
                # List element is not a dictionnary -> convert it to dictionnary

                # Rename ?
                rename_path: str = self.__rename_path('%s%s' % (path, self.inner_sep_suffix))

                elt: Dict = {rename_path: elt}

            self.__flat_dict(
                d={
                    **elt,
                    **extra,
                },
                path=path,
                father_path=father_path,
                father_id=father_id
            )

            self.context[CONTEXT_ELEMENT] = elt
            self.context[CONTEXT_PATH] = path

            if counter_flag:
                extra[counter_field] += 1

    def __flat_dd_2_d(self, elt_value: Dict, value_path: str) -> Dict:

        if self.dd_2_dict and value_path in self.dd_2_dict:
            dd2d_def: Dict = self.dd_2_dict[value_path]

            reverse: bool = dd2d_def.get('reverse', False)
            obj_sep: bool = dd2d_def.get('sep', self.sep)

            new_object: Dict[str, Any] = {}
            for object_id in elt_value:
                the_object: Dict = elt_value[object_id]
                if isinstance(the_object, dict):
                    for object_key in the_object:
                        if reverse:
                            new_object['%s%s%s' % (object_key, obj_sep, object_id)] = the_object[object_key]
                        else:
                            new_object['%s%s%s' % (object_id, obj_sep, object_key)] = the_object[object_key]
                else:
                    new_object['%s' % object_id] = the_object

            return new_object
        return elt_value

    def __flat_dict(self,
                    d: Dict,
                    path: str,
                    father_path: Optional[str] = None,
                    father_id: Any = None) -> None:

        if not d:
            return

        self.context[CONTEXT_DEPTH] += 1
        self.context[CONTEXT_PATH] = path

        self.__init_flat_dict_list(path)

        current_dict: Dict[str, Any] = self.__build_new_flat_dict(
            d=d,
            path=path,
            father_path=father_path,
            father_id=father_id
        )
        current_dict_id: Any = current_dict[self.id_field_name]

        for elt_name in d:

            self.context[CONTEXT_ELEMENT] = elt_name

            # Get value
            elt_value: Any = d[elt_name]

            # Create the full value path
            value_path: str = self.__build_new_path(elt_name, path)

            # Rename ?
            value_path: str = self.__rename_path(value_path)

            # Drop ?
            if self.__is_drop(value_path=value_path):
                continue

            # Change value ?
            new_elt_value: Any = self.__change_value(cur_value=elt_value, value_path=value_path)

            if isinstance(new_elt_value, dict):

                new_elt_value = self.__flat_dd_2_d(new_elt_value, value_path)

                # Inner dictionnary
                self.__flat_dict(
                    d=new_elt_value,
                    path=value_path,
                    father_path=path,
                    father_id=current_dict_id
                )

                self.context[CONTEXT_ELEMENT] = elt_name
                self.context[CONTEXT_PATH] = path

            elif isinstance(new_elt_value, (list, tuple)):
                # Inner list or tuple
                self.__flat_list_or_tuple(
                    lt=new_elt_value,
                    path=value_path,
                    father_path=path,
                    father_id=current_dict_id
                )

                self.context[CONTEXT_ELEMENT] = elt_name
                self.context[CONTEXT_PATH] = path

            else:
                # Other types

                # Rename ?
                new_elt_name: str = self.__rename_path(elt_name)

                current_dict[new_elt_name] = new_elt_value

        self.context[CONTEXT_DEPTH] -= 1
        self.context[CONTEXT_PATH] = None
        self.context[CONTEXT_ELEMENT] = None

    def flat(self, d: Dict) -> Dict[str, List[Dict]]:
        self.flat_dict_result: Dict = {}
        self.context[CONTEXT_DEPTH] = 0
        self.context[CONTEXT_PATH] = None
        self.context[CONTEXT_ELEMENT] = None

        # Change root dict value ?
        self.__change_value(cur_value=d, value_path=CHANGE_ROOT)

        self.__flat_dict(d=d, path=self.root_key)
        return self.flat_dict_result
