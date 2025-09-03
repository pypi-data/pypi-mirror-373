from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SkewCls:
	"""Skew commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("skew", core, parent)

	def set(self, skew: float, digital=repcap.Digital.Default) -> None:
		"""DIGital<*>:SKEW \n
		Snippet: driver.digital.skew.set(skew = 1.0, digital = repcap.Digital.Default) \n
		Sets an individual delay for each digital channel to time-align it with other digital channels.
		The skew value compensates delays that are known from the circuit specifics or caused by the different length of cables.
		The setting affects only the settings of the first MSO bus (Logic1) . You can set the skew for all buses with method
		RsMxo.Pbus.Bit.Skew.set. \n
			:param skew: No help available
			:param digital: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Digital')
		"""
		param = Conversions.decimal_value_to_str(skew)
		digital_cmd_val = self._cmd_group.get_repcap_cmd_value(digital, repcap.Digital)
		self._core.io.write(f'DIGital{digital_cmd_val}:SKEW {param}')

	def get(self, digital=repcap.Digital.Default) -> float:
		"""DIGital<*>:SKEW \n
		Snippet: value: float = driver.digital.skew.get(digital = repcap.Digital.Default) \n
		Sets an individual delay for each digital channel to time-align it with other digital channels.
		The skew value compensates delays that are known from the circuit specifics or caused by the different length of cables.
		The setting affects only the settings of the first MSO bus (Logic1) . You can set the skew for all buses with method
		RsMxo.Pbus.Bit.Skew.set. \n
			:param digital: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Digital')
			:return: skew: No help available"""
		digital_cmd_val = self._cmd_group.get_repcap_cmd_value(digital, repcap.Digital)
		response = self._core.io.query_str(f'DIGital{digital_cmd_val}:SKEW?')
		return Conversions.str_to_float(response)
