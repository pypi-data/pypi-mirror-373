from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StateCls:
	"""State commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	def set(self, state: bool, digital=repcap.Digital.Default) -> None:
		"""DIGital<*>:STATe \n
		Snippet: driver.digital.state.set(state = False, digital = repcap.Digital.Default) \n
		Enables or disables the indicated digital channel, displays it, and enables the Logic 1 if the bus was disabled.
		If another active bus already uses the selected digital channel, the instrument disables the other bus to avoid conflicts.
		For Logic 1, the DIG::STAT command has the same effect as method RsMxo.Pbus.State.set. To enable digital channels for
		buses 2, 3 and 4, use the method RsMxo.Pbus.Bit.State.set command. \n
			:param state: No help available
			:param digital: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Digital')
		"""
		param = Conversions.bool_to_str(state)
		digital_cmd_val = self._cmd_group.get_repcap_cmd_value(digital, repcap.Digital)
		self._core.io.write(f'DIGital{digital_cmd_val}:STATe {param}')

	def get(self, digital=repcap.Digital.Default) -> bool:
		"""DIGital<*>:STATe \n
		Snippet: value: bool = driver.digital.state.get(digital = repcap.Digital.Default) \n
		Enables or disables the indicated digital channel, displays it, and enables the Logic 1 if the bus was disabled.
		If another active bus already uses the selected digital channel, the instrument disables the other bus to avoid conflicts.
		For Logic 1, the DIG::STAT command has the same effect as method RsMxo.Pbus.State.set. To enable digital channels for
		buses 2, 3 and 4, use the method RsMxo.Pbus.Bit.State.set command. \n
			:param digital: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Digital')
			:return: state: No help available"""
		digital_cmd_val = self._cmd_group.get_repcap_cmd_value(digital, repcap.Digital)
		response = self._core.io.query_str(f'DIGital{digital_cmd_val}:STATe?')
		return Conversions.str_to_bool(response)
