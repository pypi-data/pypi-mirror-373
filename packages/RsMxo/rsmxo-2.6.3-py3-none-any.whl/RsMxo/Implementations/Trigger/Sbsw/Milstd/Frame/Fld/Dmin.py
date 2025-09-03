from typing import List

from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DminCls:
	"""Dmin commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("dmin", core, parent)

	def set(self, data_min: List[int], frame=repcap.Frame.Default, field=repcap.Field.Default) -> None:
		"""TRIGger:SBSW:MILStd:FRAMe<*>:FLD<*>:DMIN \n
		Snippet: driver.trigger.sbsw.milstd.frame.fld.dmin.set(data_min = [1, 2, 3], frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Specifies the data pattern, or sets the start value of a data pattern range for the software trigger. \n
			:param data_min: No help available
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
		"""
		param = Conversions.list_to_csv_str(data_min)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		self._core.io.write(f'TRIGger:SBSW:MILStd:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:DMIN {param}')

	def get(self, frame=repcap.Frame.Default, field=repcap.Field.Default) -> List[int]:
		"""TRIGger:SBSW:MILStd:FRAMe<*>:FLD<*>:DMIN \n
		Snippet: value: List[int] = driver.trigger.sbsw.milstd.frame.fld.dmin.get(frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Specifies the data pattern, or sets the start value of a data pattern range for the software trigger. \n
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
			:return: data_min: No help available"""
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		response = self._core.io.query_bin_or_ascii_int_list(f'TRIGger:SBSW:MILStd:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:DMIN?')
		return response
