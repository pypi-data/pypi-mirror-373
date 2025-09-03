from typing import List

from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DmaxCls:
	"""Dmax commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("dmax", core, parent)

	def set(self, data_max: List[int], frame=repcap.Frame.Default, field=repcap.Field.Default) -> None:
		"""TRIGger:SBSW:SPMI:FRAMe<*>:FLD<*>:DMAX \n
		Snippet: driver.trigger.sbsw.spmi.frame.fld.dmax.set(data_max = [1, 2, 3], frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Sets the end value of a data pattern range for the software trigger, if the operator is set to INRange or OORANGe.
		You can set the operator with method RsMxo.Trigger.Sbsw.Spmi.Frame.Fld.Doperator.set. \n
			:param data_max: No help available
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
		"""
		param = Conversions.list_to_csv_str(data_max)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		self._core.io.write(f'TRIGger:SBSW:SPMI:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:DMAX {param}')

	def get(self, frame=repcap.Frame.Default, field=repcap.Field.Default) -> List[int]:
		"""TRIGger:SBSW:SPMI:FRAMe<*>:FLD<*>:DMAX \n
		Snippet: value: List[int] = driver.trigger.sbsw.spmi.frame.fld.dmax.get(frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Sets the end value of a data pattern range for the software trigger, if the operator is set to INRange or OORANGe.
		You can set the operator with method RsMxo.Trigger.Sbsw.Spmi.Frame.Fld.Doperator.set. \n
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
			:return: data_max: No help available"""
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		response = self._core.io.query_bin_or_ascii_int_list(f'TRIGger:SBSW:SPMI:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:DMAX?')
		return response
