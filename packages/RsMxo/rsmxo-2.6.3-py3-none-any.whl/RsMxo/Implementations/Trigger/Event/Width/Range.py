from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RangeCls:
	"""Range commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("range", core, parent)

	def set(self, range_mode: enums.RangeMode, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:WIDTh:RANGe \n
		Snippet: driver.trigger.event.width.range.set(range_mode = enums.RangeMode.LONGer, evnt = repcap.Evnt.Default) \n
		Selects how the range of a pulse width is defined. \n
			:param range_mode: No help available
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
		"""
		param = Conversions.enum_scalar_to_str(range_mode, enums.RangeMode)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:WIDTh:RANGe {param}')

	# noinspection PyTypeChecker
	def get(self, evnt=repcap.Evnt.Default) -> enums.RangeMode:
		"""TRIGger:EVENt<*>:WIDTh:RANGe \n
		Snippet: value: enums.RangeMode = driver.trigger.event.width.range.get(evnt = repcap.Evnt.Default) \n
		Selects how the range of a pulse width is defined. \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: range_mode: No help available"""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:WIDTh:RANGe?')
		return Conversions.str_to_scalar_enum(response, enums.RangeMode)
