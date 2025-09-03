from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EnableCls:
	"""Enable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("enable", core, parent)

	def set(self, cond_enabler: bool, frame=repcap.Frame.Default, field=repcap.Field.Default) -> None:
		"""TRIGger:SBSW:SPMI:FRAMe<*>:FLD<*>:ENABle \n
		Snippet: driver.trigger.sbsw.spmi.frame.fld.enable.set(cond_enabler = False, frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Enables or disables the checking condition for the selected field of the selected frame of the software trigger. \n
			:param cond_enabler: No help available
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
		"""
		param = Conversions.bool_to_str(cond_enabler)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		self._core.io.write(f'TRIGger:SBSW:SPMI:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:ENABle {param}')

	def get(self, frame=repcap.Frame.Default, field=repcap.Field.Default) -> bool:
		"""TRIGger:SBSW:SPMI:FRAMe<*>:FLD<*>:ENABle \n
		Snippet: value: bool = driver.trigger.sbsw.spmi.frame.fld.enable.get(frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Enables or disables the checking condition for the selected field of the selected frame of the software trigger. \n
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
			:return: cond_enabler: No help available"""
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		response = self._core.io.query_str(f'TRIGger:SBSW:SPMI:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:ENABle?')
		return Conversions.str_to_bool(response)
