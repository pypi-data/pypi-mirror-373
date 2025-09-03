from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HistogramCls:
	"""Histogram commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("histogram", core, parent)

	def set(self, disp_histg: bool, measIndex=repcap.MeasIndex.Default, refLevel=repcap.RefLevel.Default) -> None:
		"""MEASurement<*>:DISPlay:REFLevel<*>:HISTogram \n
		Snippet: driver.measurement.display.refLevel.histogram.set(disp_histg = False, measIndex = repcap.MeasIndex.Default, refLevel = repcap.RefLevel.Default) \n
		No command help available \n
			:param disp_histg: No help available
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
		"""
		param = Conversions.bool_to_str(disp_histg)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:DISPlay:REFLevel{refLevel_cmd_val}:HISTogram {param}')

	def get(self, measIndex=repcap.MeasIndex.Default, refLevel=repcap.RefLevel.Default) -> bool:
		"""MEASurement<*>:DISPlay:REFLevel<*>:HISTogram \n
		Snippet: value: bool = driver.measurement.display.refLevel.histogram.get(measIndex = repcap.MeasIndex.Default, refLevel = repcap.RefLevel.Default) \n
		No command help available \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
			:return: disp_histg: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:DISPlay:REFLevel{refLevel_cmd_val}:HISTogram?')
		return Conversions.str_to_bool(response)
