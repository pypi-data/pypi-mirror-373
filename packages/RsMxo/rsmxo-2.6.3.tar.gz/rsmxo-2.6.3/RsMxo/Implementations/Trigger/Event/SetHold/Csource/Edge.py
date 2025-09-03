from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import enums
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EdgeCls:
	"""Edge commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("edge", core, parent)

	def set(self, clock_edge: enums.PulseSlope, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:SETHold:CSOurce:EDGE \n
		Snippet: driver.trigger.event.setHold.csource.edge.set(clock_edge = enums.PulseSlope.EITHer, evnt = repcap.Evnt.Default) \n
		Sets the edge of the clock signal. Edge and level define the time reference point. \n
			:param clock_edge: No help available
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
		"""
		param = Conversions.enum_scalar_to_str(clock_edge, enums.PulseSlope)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:SETHold:CSOurce:EDGE {param}')

	# noinspection PyTypeChecker
	def get(self, evnt=repcap.Evnt.Default) -> enums.PulseSlope:
		"""TRIGger:EVENt<*>:SETHold:CSOurce:EDGE \n
		Snippet: value: enums.PulseSlope = driver.trigger.event.setHold.csource.edge.get(evnt = repcap.Evnt.Default) \n
		Sets the edge of the clock signal. Edge and level define the time reference point. \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: clock_edge: No help available"""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:SETHold:CSOurce:EDGE?')
		return Conversions.str_to_scalar_enum(response, enums.PulseSlope)
