from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal.Utilities import trim_str_response
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LabelCls:
	"""Label commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("label", core, parent)

	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default, field=repcap.Field.Default) -> str:
		"""SBUS<*>:I3C:FRAMe<*>:FLD<*>:LABel \n
		Snippet: value: str = driver.sbus.i3C.frame.fld.label.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default, field = repcap.Field.Default) \n
		Returns the name (label) of the specified field in the selected frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param field: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fld')
			:return: label: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		field_cmd_val = self._cmd_group.get_repcap_cmd_value(field, repcap.Field)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:I3C:FRAMe{frame_cmd_val}:FLD{field_cmd_val}:LABel?')
		return trim_str_response(response)
