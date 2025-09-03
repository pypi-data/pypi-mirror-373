from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DirectionCls:
	"""Direction commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("direction", core, parent)

	def set(self, edge_cnt_dirct: enums.EdgeCntDirct, measIndex=repcap.MeasIndex.Default, delay=repcap.Delay.Default) -> None:
		"""MEASurement<*>:AMPTime:DELay<*>:DIRection \n
		Snippet: driver.measurement.ampTime.delay.direction.set(edge_cnt_dirct = enums.EdgeCntDirct.FRFI, measIndex = repcap.MeasIndex.Default, delay = repcap.Delay.Default) \n
		Selects the direction for counting slopes for each source: from the beginning of the waveform, or from the end. \n
			:param edge_cnt_dirct: FRFI - FRom FIrst, counting starts with the first edge of the waveform. FRLA - FRom LAst, counting starts with the last edge of the waveform.
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:param delay: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Delay')
		"""
		param = Conversions.enum_scalar_to_str(edge_cnt_dirct, enums.EdgeCntDirct)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		delay_cmd_val = self._cmd_group.get_repcap_cmd_value(delay, repcap.Delay)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:AMPTime:DELay{delay_cmd_val}:DIRection {param}')

	# noinspection PyTypeChecker
	def get(self, measIndex=repcap.MeasIndex.Default, delay=repcap.Delay.Default) -> enums.EdgeCntDirct:
		"""MEASurement<*>:AMPTime:DELay<*>:DIRection \n
		Snippet: value: enums.EdgeCntDirct = driver.measurement.ampTime.delay.direction.get(measIndex = repcap.MeasIndex.Default, delay = repcap.Delay.Default) \n
		Selects the direction for counting slopes for each source: from the beginning of the waveform, or from the end. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:param delay: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Delay')
			:return: edge_cnt_dirct: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		delay_cmd_val = self._cmd_group.get_repcap_cmd_value(delay, repcap.Delay)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:AMPTime:DELay{delay_cmd_val}:DIRection?')
		return Conversions.str_to_scalar_enum(response, enums.EdgeCntDirct)
