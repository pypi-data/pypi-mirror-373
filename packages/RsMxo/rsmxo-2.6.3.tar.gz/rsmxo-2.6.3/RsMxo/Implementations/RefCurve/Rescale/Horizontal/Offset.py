from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class OffsetCls:
	"""Offset commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("offset", core, parent)

	def set(self, offset: float, refCurve=repcap.RefCurve.Default) -> None:
		"""REFCurve<*>:RESCale:HORizontal:OFFSet \n
		Snippet: driver.refCurve.rescale.horizontal.offset.set(offset = 1.0, refCurve = repcap.RefCurve.Default) \n
		Moves the waveform horizontally. Enter a value with a time unit suitable for the time scale of the diagram.
		Positive values shift the waveform to the right, negative values shift it to the left. \n
			:param offset: No help available
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
		"""
		param = Conversions.decimal_value_to_str(offset)
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		self._core.io.write(f'REFCurve{refCurve_cmd_val}:RESCale:HORizontal:OFFSet {param}')

	def get(self, refCurve=repcap.RefCurve.Default) -> float:
		"""REFCurve<*>:RESCale:HORizontal:OFFSet \n
		Snippet: value: float = driver.refCurve.rescale.horizontal.offset.get(refCurve = repcap.RefCurve.Default) \n
		Moves the waveform horizontally. Enter a value with a time unit suitable for the time scale of the diagram.
		Positive values shift the waveform to the right, negative values shift it to the left. \n
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
			:return: offset: No help available"""
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		response = self._core.io.query_str(f'REFCurve{refCurve_cmd_val}:RESCale:HORizontal:OFFSet?')
		return Conversions.str_to_float(response)
