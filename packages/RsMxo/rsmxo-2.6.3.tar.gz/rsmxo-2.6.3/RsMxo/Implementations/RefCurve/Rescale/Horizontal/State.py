from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StateCls:
	"""State commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	def set(self, state: bool, refCurve=repcap.RefCurve.Default) -> None:
		"""REFCurve<*>:RESCale:HORizontal:STATe \n
		Snippet: driver.refCurve.rescale.horizontal.state.set(state = False, refCurve = repcap.RefCurve.Default) \n
		If enabled, the horizontal offset and factor are applied to the reference waveform. Stretching and offset change the
		display of the waveform independent of the horizontal settings of the source waveform and of the horizontal diagram
		settings. \n
			:param state: No help available
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
		"""
		param = Conversions.bool_to_str(state)
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		self._core.io.write(f'REFCurve{refCurve_cmd_val}:RESCale:HORizontal:STATe {param}')

	def get(self, refCurve=repcap.RefCurve.Default) -> bool:
		"""REFCurve<*>:RESCale:HORizontal:STATe \n
		Snippet: value: bool = driver.refCurve.rescale.horizontal.state.get(refCurve = repcap.RefCurve.Default) \n
		If enabled, the horizontal offset and factor are applied to the reference waveform. Stretching and offset change the
		display of the waveform independent of the horizontal settings of the source waveform and of the horizontal diagram
		settings. \n
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
			:return: state: No help available"""
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		response = self._core.io.query_str(f'REFCurve{refCurve_cmd_val}:RESCale:HORizontal:STATe?')
		return Conversions.str_to_bool(response)
