from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ThresholdCls:
	"""Threshold commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("threshold", core, parent)

	def set(self, value: float, digital=repcap.Digital.Default) -> None:
		"""DIGital<*>:THReshold \n
		Snippet: driver.digital.threshold.set(value = 1.0, digital = repcap.Digital.Default) \n
		Sets the logical threshold for the channel group to which the indicated digital channel belongs. The setting affects only
		the settings of the first MSO bus (Logic1) . You can set the threshold for all buses with method RsMxo.Pbus.Technology.
		set or PBUS<pb>:THReshold<n> See also: method RsMxo.Digital.ThCoupling.set \n
			:param value: No help available
			:param digital: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Digital')
		"""
		param = Conversions.decimal_value_to_str(value)
		digital_cmd_val = self._cmd_group.get_repcap_cmd_value(digital, repcap.Digital)
		self._core.io.write(f'DIGital{digital_cmd_val}:THReshold {param}')

	def get(self, digital=repcap.Digital.Default) -> float:
		"""DIGital<*>:THReshold \n
		Snippet: value: float = driver.digital.threshold.get(digital = repcap.Digital.Default) \n
		Sets the logical threshold for the channel group to which the indicated digital channel belongs. The setting affects only
		the settings of the first MSO bus (Logic1) . You can set the threshold for all buses with method RsMxo.Pbus.Technology.
		set or PBUS<pb>:THReshold<n> See also: method RsMxo.Digital.ThCoupling.set \n
			:param digital: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Digital')
			:return: value: No help available"""
		digital_cmd_val = self._cmd_group.get_repcap_cmd_value(digital, repcap.Digital)
		response = self._core.io.query_str(f'DIGital{digital_cmd_val}:THReshold?')
		return Conversions.str_to_float(response)
