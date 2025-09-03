from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class BitcountCls:
	"""Bitcount commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("bitcount", core, parent)

	def set(self, bitcount: int, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default, field=repcap.Field.Default) -> None:
		"""SBUS<*>:NRZC:FORMat:FRAMe<*>:FLD<*>:BITCount \n
		Snippet: driver.sbus.nrzc.formatPy.frame.fld.bitcount.set(bitcount = 1, serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Specifies the bit count, hence length, of the selected field in the selected frame. \n
			:param bitcount: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
		"""
		param = Conversions.decimal_value_to_str(bitcount)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:NRZC:FORMat:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:BITCount {param}')

	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default, field=repcap.Field.Default) -> int:
		"""SBUS<*>:NRZC:FORMat:FRAMe<*>:FLD<*>:BITCount \n
		Snippet: value: int = driver.sbus.nrzc.formatPy.frame.fld.bitcount.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Specifies the bit count, hence length, of the selected field in the selected frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
			:return: bitcount: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:NRZC:FORMat:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:BITCount?')
		return Conversions.str_to_int(response)
