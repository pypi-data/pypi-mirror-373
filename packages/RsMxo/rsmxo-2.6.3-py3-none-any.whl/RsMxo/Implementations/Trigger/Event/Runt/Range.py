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

	def set(self, mode: enums.TriggerRuntRangeMode, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:RUNT:RANGe \n
		Snippet: driver.trigger.event.runt.range.set(mode = enums.TriggerRuntRangeMode.ANY, evnt = repcap.Evnt.Default) \n
		Defines the time limit of the runt pulse in relation to the method RsMxo.Trigger.Event.Runt.Width.set and method RsMxo.
		Trigger.Event.Runt.Delta.set settings. \n
			:param mode:
				- ANY: Triggers on all runts fulfilling the level condition, without time limitation.
				- LONGer: Triggers on runts longer than the given runt width.
				- SHORter: Triggers on runts shorter than the given runt width.
				- WITHin: Triggers if the runt length is inside a given time range. The range is defined by runt width and ±Delta.
				- OUTSide: Triggers if the runt length is outside a given time range. The range is defined by runt width and ±Delta.
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')"""
		param = Conversions.enum_scalar_to_str(mode, enums.TriggerRuntRangeMode)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:RUNT:RANGe {param}')

	# noinspection PyTypeChecker
	def get(self, evnt=repcap.Evnt.Default) -> enums.TriggerRuntRangeMode:
		"""TRIGger:EVENt<*>:RUNT:RANGe \n
		Snippet: value: enums.TriggerRuntRangeMode = driver.trigger.event.runt.range.get(evnt = repcap.Evnt.Default) \n
		Defines the time limit of the runt pulse in relation to the method RsMxo.Trigger.Event.Runt.Width.set and method RsMxo.
		Trigger.Event.Runt.Delta.set settings. \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: mode:
				- ANY: Triggers on all runts fulfilling the level condition, without time limitation.
				- LONGer: Triggers on runts longer than the given runt width.
				- SHORter: Triggers on runts shorter than the given runt width.
				- WITHin: Triggers if the runt length is inside a given time range. The range is defined by runt width and ±Delta.
				- OUTSide: Triggers if the runt length is outside a given time range. The range is defined by runt width and ±Delta."""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:RUNT:RANGe?')
		return Conversions.str_to_scalar_enum(response, enums.TriggerRuntRangeMode)
