from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class OffsetCls:
	"""Offset commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("offset", core, parent)

	def set(self, vertical_offset: float, refCurve=repcap.RefCurve.Default) -> None:
		"""REFCurve<*>:OFFSet \n
		Snippet: driver.refCurve.offset.set(vertical_offset = 1.0, refCurve = repcap.RefCurve.Default) \n
		The vertical offset moves the reference waveform vertically. Enter a value with the unit of the waveform. \n
			:param vertical_offset: No help available
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
		"""
		param = Conversions.decimal_value_to_str(vertical_offset)
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		self._core.io.write(f'REFCurve{refCurve_cmd_val}:OFFSet {param}')

	def get(self, refCurve=repcap.RefCurve.Default) -> float:
		"""REFCurve<*>:OFFSet \n
		Snippet: value: float = driver.refCurve.offset.get(refCurve = repcap.RefCurve.Default) \n
		The vertical offset moves the reference waveform vertically. Enter a value with the unit of the waveform. \n
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
			:return: vertical_offset: No help available"""
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		response = self._core.io.query_str(f'REFCurve{refCurve_cmd_val}:OFFSet?')
		return Conversions.str_to_float(response)
