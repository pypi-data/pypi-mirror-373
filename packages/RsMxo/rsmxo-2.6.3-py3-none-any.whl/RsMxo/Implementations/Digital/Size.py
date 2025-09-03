from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SizeCls:
	"""Size commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("size", core, parent)

	def set(self, size: float, digital=repcap.Digital.Default) -> None:
		"""DIGital<*>:SIZE \n
		Snippet: driver.digital.size.set(size = 1.0, digital = repcap.Digital.Default) \n
		Sets the vertical size for the channel group to which the indicated digital channel belongs. \n
			:param size: Number of vertical divisions per logic channel
			:param digital: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Digital')
		"""
		param = Conversions.decimal_value_to_str(size)
		digital_cmd_val = self._cmd_group.get_repcap_cmd_value(digital, repcap.Digital)
		self._core.io.write(f'DIGital{digital_cmd_val}:SIZE {param}')

	def get(self, digital=repcap.Digital.Default) -> float:
		"""DIGital<*>:SIZE \n
		Snippet: value: float = driver.digital.size.get(digital = repcap.Digital.Default) \n
		Sets the vertical size for the channel group to which the indicated digital channel belongs. \n
			:param digital: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Digital')
			:return: size: Number of vertical divisions per logic channel"""
		digital_cmd_val = self._cmd_group.get_repcap_cmd_value(digital, repcap.Digital)
		response = self._core.io.query_str(f'DIGital{digital_cmd_val}:SIZE?')
		return Conversions.str_to_float(response)
