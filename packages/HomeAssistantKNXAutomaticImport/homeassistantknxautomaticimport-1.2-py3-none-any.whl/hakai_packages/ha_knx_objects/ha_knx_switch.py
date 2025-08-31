from hakai_packages.ha_knx_objects_common import HAKNXDevice, KNXDeviceParameterType
from hakai_packages.knx_project_objects import KNXDPTType
from hakai_packages.knx_utils import Quoted

# pylint: disable=R0801

class HAKNXSwitch(HAKNXDevice):
    keyname = 'switch'
    keywords = ['switch', 'commutateur', 'prise', 'interrupteur', 'socket']
    parameters = [
        {
            'name': 'address',
            'required': True,
            'type': KNXDeviceParameterType.GA,
            'configuration': {
                'dpts': [
                KNXDPTType.constructor_from_ints(1,None)
                ],
                'keywords': ['on', 'off', 'switch', 'commutation']
            },
            'param_class': Quoted
        },
        {
            'name': 'state_address',
            'required': False,
            'type': KNXDeviceParameterType.GA,
            'configuration': {
                'dpts': [
                KNXDPTType.constructor_from_ints(1,None)
                ],
                'keywords': ['etat', 'state', 'statut']
            },
            'param_class': Quoted
        },
        {
            'name': 'respond_to_read',
            'required': False,
            'type': KNXDeviceParameterType.RTR,
            'configuration': {
                'param_for_address': 'address',
                'param_for_state_address': 'state_address'
            },
            'param_class': bool
        }
    ]
