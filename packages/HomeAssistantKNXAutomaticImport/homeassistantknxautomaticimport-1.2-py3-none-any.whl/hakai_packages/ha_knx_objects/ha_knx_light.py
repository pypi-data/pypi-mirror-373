from hakai_packages.ha_knx_objects_common import HAKNXDevice, KNXDeviceParameterType
from hakai_packages.knx_project_objects import KNXDPTType
from hakai_packages.knx_utils import Quoted

# pylint: disable=R0801

class HAKNXLight(HAKNXDevice):
    keyname = 'light'
    keywords = ['light', 'lumiere']
    parameters = [
        {
            'name': 'address',
            'required': True,
            'type': KNXDeviceParameterType.GA,
            'configuration': {
                'dpts': [
                KNXDPTType.constructor_from_ints(1,1)
                ],
                'keywords': ['on', 'off', 'switch']
            },
            'param_class': Quoted
        },
        {
            'name': 'state_address',
            'required': False,
            'type': KNXDeviceParameterType.GA,
            'configuration': {
                'dpts': [
                KNXDPTType.constructor_from_ints(1,1)
                ],
                'keywords': ['etat', 'state']
            },
            'param_class': Quoted
        }
    ]
