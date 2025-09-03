from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MarginCls:
	"""Margin commands group definition. 5 total commands, 2 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("margin", core, parent)

	@property
	def phase(self):
		"""phase commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_phase'):
			from .Phase import PhaseCls
			self._phase = PhaseCls(self._core, self._cmd_group)
		return self._phase

	@property
	def gain(self):
		"""gain commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_gain'):
			from .Gain import GainCls
			self._gain = GainCls(self._core, self._cmd_group)
		return self._gain

	def get_state(self) -> bool:
		"""FRANalysis:MARGin:STATe \n
		Snippet: value: bool = driver.franalysis.margin.get_state() \n
		Enables the display of the margin table for the FRA. \n
			:return: margins: No help available
		"""
		response = self._core.io.query_str('FRANalysis:MARGin:STATe?')
		return Conversions.str_to_bool(response)

	def set_state(self, margins: bool) -> None:
		"""FRANalysis:MARGin:STATe \n
		Snippet: driver.franalysis.margin.set_state(margins = False) \n
		Enables the display of the margin table for the FRA. \n
			:param margins: No help available
		"""
		param = Conversions.bool_to_str(margins)
		self._core.io.write(f'FRANalysis:MARGin:STATe {param}')

	def clone(self) -> 'MarginCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = MarginCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
