from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PolarityCls:
	"""Polarity commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("polarity", core, parent)

	def set(self, polarity: enums.PulseSlope, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:WIDTh:POLarity \n
		Snippet: driver.trigger.event.width.polarity.set(polarity = enums.PulseSlope.EITHer, evnt = repcap.Evnt.Default) \n
		Sets the polarity of a pulse, which is the direction of the first pulse slope. \n
			:param polarity: No help available
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
		"""
		param = Conversions.enum_scalar_to_str(polarity, enums.PulseSlope)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:WIDTh:POLarity {param}')

	# noinspection PyTypeChecker
	def get(self, evnt=repcap.Evnt.Default) -> enums.PulseSlope:
		"""TRIGger:EVENt<*>:WIDTh:POLarity \n
		Snippet: value: enums.PulseSlope = driver.trigger.event.width.polarity.get(evnt = repcap.Evnt.Default) \n
		Sets the polarity of a pulse, which is the direction of the first pulse slope. \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: polarity: No help available"""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:WIDTh:POLarity?')
		return Conversions.str_to_scalar_enum(response, enums.PulseSlope)
