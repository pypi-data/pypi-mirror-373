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

	def set(self, state: bool, xyAxis=repcap.XyAxis.Default) -> None:
		"""XY<*>[:STATe] \n
		Snippet: driver.xy.state.set(state = False, xyAxis = repcap.XyAxis.Default) \n
		Activates an XY-waveform. \n
			:param state: No help available
			:param xyAxis: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Xy')
		"""
		param = Conversions.bool_to_str(state)
		xyAxis_cmd_val = self._cmd_group.get_repcap_cmd_value(xyAxis, repcap.XyAxis)
		self._core.io.write(f'XY{xyAxis_cmd_val}:STATe {param}')

	def get(self, xyAxis=repcap.XyAxis.Default) -> bool:
		"""XY<*>[:STATe] \n
		Snippet: value: bool = driver.xy.state.get(xyAxis = repcap.XyAxis.Default) \n
		Activates an XY-waveform. \n
			:param xyAxis: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Xy')
			:return: state: No help available"""
		xyAxis_cmd_val = self._cmd_group.get_repcap_cmd_value(xyAxis, repcap.XyAxis)
		response = self._core.io.query_str(f'XY{xyAxis_cmd_val}:STATe?')
		return Conversions.str_to_bool(response)
