from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ImaxCls:
	"""Imax commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("imax", core, parent)

	def set(self, index_max: int, frame=repcap.Frame.Default, field=repcap.Field.Default) -> None:
		"""TRIGger:SBSW:I2C:FRAMe<*>:FLD<*>:IMAX \n
		Snippet: driver.trigger.sbsw.i2C.frame.fld.imax.set(index_max = 1, frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Sets the end value of an index range for the software trigger if the operator is set to INRange. You can set the operator
		with method RsMxo.Trigger.Sbsw.I2C.Frame.Fld.Ioperator.set. \n
			:param index_max: No help available
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
		"""
		param = Conversions.decimal_value_to_str(index_max)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		self._core.io.write(f'TRIGger:SBSW:I2C:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:IMAX {param}')

	def get(self, frame=repcap.Frame.Default, field=repcap.Field.Default) -> int:
		"""TRIGger:SBSW:I2C:FRAMe<*>:FLD<*>:IMAX \n
		Snippet: value: int = driver.trigger.sbsw.i2C.frame.fld.imax.get(frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Sets the end value of an index range for the software trigger if the operator is set to INRange. You can set the operator
		with method RsMxo.Trigger.Sbsw.I2C.Frame.Fld.Ioperator.set. \n
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
			:return: index_max: No help available"""
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		response = self._core.io.query_str(f'TRIGger:SBSW:I2C:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:IMAX?')
		return Conversions.str_to_int(response)
