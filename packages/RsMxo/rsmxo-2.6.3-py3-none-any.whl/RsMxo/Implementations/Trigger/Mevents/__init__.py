from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MeventsCls:
	"""Mevents commands group definition. 7 total commands, 1 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mevents", core, parent)

	@property
	def sequence(self):
		"""sequence commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_sequence'):
			from .Sequence import SequenceCls
			self._sequence = SequenceCls(self._core, self._cmd_group)
		return self._sequence

	# noinspection PyTypeChecker
	def get_mode(self) -> enums.EventsMode:
		"""TRIGger:MEVents:MODE \n
		Snippet: value: enums.EventsMode = driver.trigger.mevents.get_mode() \n
		Selects, if you want to trigger on a single event, or on a series of events. \n
			:return: class_py: No help available
		"""
		response = self._core.io.query_str('TRIGger:MEVents:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.EventsMode)

	def set_mode(self, class_py: enums.EventsMode) -> None:
		"""TRIGger:MEVents:MODE \n
		Snippet: driver.trigger.mevents.set_mode(class_py = enums.EventsMode.SEQuence) \n
		Selects, if you want to trigger on a single event, or on a series of events. \n
			:param class_py: No help available
		"""
		param = Conversions.enum_scalar_to_str(class_py, enums.EventsMode)
		self._core.io.write(f'TRIGger:MEVents:MODE {param}')

	# noinspection PyTypeChecker
	def get_aevents(self) -> enums.TriggerMultiEventsType:
		"""TRIGger:MEVents:AEVents \n
		Snippet: value: enums.TriggerMultiEventsType = driver.trigger.mevents.get_aevents() \n
		Selects the type of the trigger sequence. \n
			:return: type_py: AONLy = single event, same as method RsMxo.Trigger.Mevents.mode ABR = sequence A → B → R AZ = sequence A → Zone trigger ASB = sequence A → Serial bus
		"""
		response = self._core.io.query_str('TRIGger:MEVents:AEVents?')
		return Conversions.str_to_scalar_enum(response, enums.TriggerMultiEventsType)

	def set_aevents(self, type_py: enums.TriggerMultiEventsType) -> None:
		"""TRIGger:MEVents:AEVents \n
		Snippet: driver.trigger.mevents.set_aevents(type_py = enums.TriggerMultiEventsType.AB) \n
		Selects the type of the trigger sequence. \n
			:param type_py: AONLy = single event, same as method RsMxo.Trigger.Mevents.mode ABR = sequence A → B → R AZ = sequence A → Zone trigger ASB = sequence A → Serial bus
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.TriggerMultiEventsType)
		self._core.io.write(f'TRIGger:MEVents:AEVents {param}')

	def clone(self) -> 'MeventsCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = MeventsCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
