from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SlopeCls:
	"""Slope commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("slope", core, parent)

	def set(self, slope: enums.PulseSlope, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:INTerval:SLOPe \n
		Snippet: driver.trigger.event.interval.slope.set(slope = enums.PulseSlope.EITHer, evnt = repcap.Evnt.Default) \n
		Sets the edge for the trigger. You can analyze the interval between positive edges or between negative edges. \n
			:param slope: No help available
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
		"""
		param = Conversions.enum_scalar_to_str(slope, enums.PulseSlope)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:INTerval:SLOPe {param}')

	# noinspection PyTypeChecker
	def get(self, evnt=repcap.Evnt.Default) -> enums.PulseSlope:
		"""TRIGger:EVENt<*>:INTerval:SLOPe \n
		Snippet: value: enums.PulseSlope = driver.trigger.event.interval.slope.get(evnt = repcap.Evnt.Default) \n
		Sets the edge for the trigger. You can analyze the interval between positive edges or between negative edges. \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: slope: No help available"""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:INTerval:SLOPe?')
		return Conversions.str_to_scalar_enum(response, enums.PulseSlope)
