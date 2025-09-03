from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ZoneCls:
	"""Zone commands group definition. 2 total commands, 1 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("zone", core, parent)

	@property
	def expression(self):
		"""expression commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_expression'):
			from .Expression import ExpressionCls
			self._expression = ExpressionCls(self._core, self._cmd_group)
		return self._expression

	def get_history(self) -> bool:
		"""TRIGger:ZONE:HISTory \n
		Snippet: value: bool = driver.trigger.zone.get_history() \n
		Applies the zone trigger condition to the acquisitions that are stored in the history memory. Thus, you can filter the
		history of waveforms on zone conditions. \n
			:return: apply_zn_trig_history: No help available
		"""
		response = self._core.io.query_str('TRIGger:ZONE:HISTory?')
		return Conversions.str_to_bool(response)

	def set_history(self, apply_zn_trig_history: bool) -> None:
		"""TRIGger:ZONE:HISTory \n
		Snippet: driver.trigger.zone.set_history(apply_zn_trig_history = False) \n
		Applies the zone trigger condition to the acquisitions that are stored in the history memory. Thus, you can filter the
		history of waveforms on zone conditions. \n
			:param apply_zn_trig_history: No help available
		"""
		param = Conversions.bool_to_str(apply_zn_trig_history)
		self._core.io.write(f'TRIGger:ZONE:HISTory {param}')

	def clone(self) -> 'ZoneCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ZoneCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
