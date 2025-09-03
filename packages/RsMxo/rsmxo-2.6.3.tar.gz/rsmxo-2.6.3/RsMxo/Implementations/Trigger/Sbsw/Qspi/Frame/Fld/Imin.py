from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class IminCls:
	"""Imin commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("imin", core, parent)

	def set(self, index_min: int, frame=repcap.Frame.Default, field=repcap.Field.Default) -> None:
		"""TRIGger:SBSW:QSPI:FRAMe<*>:FLD<*>:IMIN \n
		Snippet: driver.trigger.sbsw.qspi.frame.fld.imin.set(index_min = 1, frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Specifies the index, or sets the start value of an index range for the software trigger. \n
			:param index_min: No help available
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
		"""
		param = Conversions.decimal_value_to_str(index_min)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		self._core.io.write(f'TRIGger:SBSW:QSPI:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:IMIN {param}')

	def get(self, frame=repcap.Frame.Default, field=repcap.Field.Default) -> int:
		"""TRIGger:SBSW:QSPI:FRAMe<*>:FLD<*>:IMIN \n
		Snippet: value: int = driver.trigger.sbsw.qspi.frame.fld.imin.get(frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Specifies the index, or sets the start value of an index range for the software trigger. \n
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
			:return: index_min: No help available"""
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		response = self._core.io.query_str(f'TRIGger:SBSW:QSPI:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:IMIN?')
		return Conversions.str_to_int(response)
