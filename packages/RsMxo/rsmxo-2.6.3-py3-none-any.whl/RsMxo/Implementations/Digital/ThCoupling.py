from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ThCouplingCls:
	"""ThCoupling commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("thCoupling", core, parent)

	def set(self, state: bool, digital=repcap.Digital.Default) -> None:
		"""DIGital<*>:THCoupling \n
		Snippet: driver.digital.thCoupling.set(state = False, digital = repcap.Digital.Default) \n
		Sets the threshold and the hysteresis for all digital channels of Logic1 to the same value. \n
			:param state: No help available
			:param digital: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Digital')
		"""
		param = Conversions.bool_to_str(state)
		digital_cmd_val = self._cmd_group.get_repcap_cmd_value(digital, repcap.Digital)
		self._core.io.write(f'DIGital{digital_cmd_val}:THCoupling {param}')

	def get(self, digital=repcap.Digital.Default) -> bool:
		"""DIGital<*>:THCoupling \n
		Snippet: value: bool = driver.digital.thCoupling.get(digital = repcap.Digital.Default) \n
		Sets the threshold and the hysteresis for all digital channels of Logic1 to the same value. \n
			:param digital: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Digital')
			:return: state: No help available"""
		digital_cmd_val = self._cmd_group.get_repcap_cmd_value(digital, repcap.Digital)
		response = self._core.io.query_str(f'DIGital{digital_cmd_val}:THCoupling?')
		return Conversions.str_to_bool(response)
