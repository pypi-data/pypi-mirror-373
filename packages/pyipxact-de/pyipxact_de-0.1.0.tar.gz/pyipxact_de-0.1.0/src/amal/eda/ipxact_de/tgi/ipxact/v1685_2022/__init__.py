"""TGI function namespace for IP-XACT 1685-2022 (category-structured).
"""
from . import abstraction_definition as _abstraction_definition  # noqa: F401
from . import abstractor as _abstractor  # noqa: F401
from . import access_handle as _access_handle  # noqa: F401
from . import access_policy as _access_policy  # noqa: F401
from . import address_space as _address_space  # noqa: F401
from . import array as _array  # noqa: F401
from . import assertion as _assertion  # noqa: F401
from . import bus_definition as _bus_definition  # noqa: F401
from . import bus_interface as _bus_interface  # noqa: F401
from . import catalog as _catalog  # noqa: F401
from . import choice as _choice  # noqa: F401
from . import clearbox as _clearbox  # noqa: F401
from . import component as _component  # noqa: F401
from . import configurable_element as _configurable_element  # noqa: F401
from . import constraint as _constraint  # noqa: F401
from . import constraint_set as _constraint_set  # noqa: F401
from . import core as _core  # noqa: F401
from . import cpu as _cpu  # noqa: F401
from . import design as _design  # noqa: F401
from . import design_configuration as _design_configuration  # noqa: F401
from . import driver as _driver  # noqa: F401
from . import element_attribute as _element_attribute  # noqa: F401
from . import file_builder as _file_builder  # noqa: F401
from . import file_set as _file_set  # noqa: F401
from . import generator as _generator  # noqa: F401
from . import generator_chain as _generator_chain  # noqa: F401
from . import indirect_interface as _indirect_interface  # noqa: F401
from . import instantiation as _instantiation  # noqa: F401
from . import memory_map as _memory_map  # noqa: F401
from . import miscellaneous as _miscellaneous  # noqa: F401
from . import module_parameter as _module_parameter  # noqa: F401
from . import name_group as _name_group  # noqa: F401
from . import parameter as _parameter  # noqa: F401
from . import port as _port  # noqa: F401
from . import port_map as _port_map  # noqa: F401
from . import power as _power  # noqa: F401
from . import register as _register  # noqa: F401
from . import register_file as _register_file  # noqa: F401
from . import slice_ as _slice  # noqa: F401
from . import top_element as _top_element  # noqa: F401
from . import type_definitions as _type_definitions  # noqa: F401
from . import vector as _vector  # noqa: F401
from . import vendor_extensions as _vendor_extensions  # noqa: F401
from . import view as _view  # noqa: F401
from .abstraction_definition import *  # noqa: F401,F403
from .abstractor import *  # noqa: F401,F403
from .access_handle import *  # noqa: F401,F403
from .access_policy import *  # noqa: F401,F403
from .address_space import *  # noqa: F401,F403
from .array import *  # noqa: F401,F403
from .assertion import *  # noqa: F401,F403
from .bus_definition import *  # noqa: F401,F403
from .bus_interface import *  # noqa: F401,F403
from .catalog import *  # noqa: F401,F403
from .choice import *  # noqa: F401,F403
from .clearbox import *  # noqa: F401,F403
from .component import *  # noqa: F401,F403
from .configurable_element import *  # noqa: F401,F403
from .constraint import *  # noqa: F401,F403
from .constraint_set import *  # noqa: F401,F403
from .core import TgiError, get_handle, resolve_handle  # noqa: F401
from .cpu import *  # noqa: F401,F403
from .design import *  # noqa: F401,F403
from .design_configuration import *  # noqa: F401,F403
from .driver import *  # noqa: F401,F403
from .element_attribute import *  # noqa: F401,F403
from .file_builder import *  # noqa: F401,F403
from .file_set import *  # noqa: F401,F403
from .generator import *  # noqa: F401,F403
from .generator_chain import *  # noqa: F401,F403
from .indirect_interface import *  # noqa: F401,F403
from .instantiation import *  # noqa: F401,F403
from .memory_map import *  # noqa: F401,F403
from .miscellaneous import *  # noqa: F401,F403
from .module_parameter import *  # noqa: F401,F403
from .name_group import *  # noqa: F401,F403
from .parameter import *  # noqa: F401,F403
from .port import *  # noqa: F401,F403
from .port_map import *  # noqa: F401,F403
from .power import *  # noqa: F401,F403
from .register import *  # noqa: F401,F403
from .register_file import *  # noqa: F401,F403
from .slice_ import *  # noqa: F401,F403
from .top_element import *  # noqa: F401,F403
from .type_definitions import *  # noqa: F401,F403
from .vector import *  # noqa: F401,F403
from .vendor_extensions import *  # noqa: F401,F403
from .view import *  # noqa: F401,F403

__all__ = [
    *_abstraction_definition.__all__,
    *_abstractor.__all__,
    *_access_handle.__all__,
    *_access_policy.__all__,
    *_address_space.__all__,
    *_array.__all__,
    *_assertion.__all__,
    *_bus_definition.__all__,
    *_bus_interface.__all__,
    *_catalog.__all__,
    *_choice.__all__,
    *_clearbox.__all__,
    *_component.__all__,
    *_configurable_element.__all__,
    *_constraint_set.__all__,
    *_constraint.__all__,
    *_cpu.__all__,
    *_design_configuration.__all__,
    *_design.__all__,
    *_driver.__all__,
    *_element_attribute.__all__,
    *_file_builder.__all__,
    *_file_set.__all__,
    *_generator_chain.__all__,
    *_generator.__all__,
    *_indirect_interface.__all__,
    *_instantiation.__all__,
    *_memory_map.__all__,
    *_miscellaneous.__all__,
    *_module_parameter.__all__,
    *_name_group.__all__,
    *_parameter.__all__,
    *_port_map.__all__,
    *_port.__all__,
    *_power.__all__,
    *_register_file.__all__,
    *_register.__all__,
    *_slice.__all__,
    *_top_element.__all__,
    *_type_definitions.__all__,
    *_vector.__all__,
    *_vendor_extensions.__all__,
    *_view.__all__,
    "get_handle",
    "resolve_handle",
    "TgiError",
]
