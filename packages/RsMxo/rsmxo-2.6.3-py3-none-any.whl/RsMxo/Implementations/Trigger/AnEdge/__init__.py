from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AnEdgeCls:
	"""AnEdge commands group definition. 12 total commands, 2 Subgroups, 5 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("anEdge", core, parent)

	@property
	def cutoff(self):
		"""cutoff commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_cutoff'):
			from .Cutoff import CutoffCls
			self._cutoff = CutoffCls(self._core, self._cmd_group)
		return self._cutoff

	@property
	def overload(self):
		"""overload commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_overload'):
			from .Overload import OverloadCls
			self._overload = OverloadCls(self._core, self._cmd_group)
		return self._overload

	def get_level(self) -> float:
		"""TRIGger:ANEDge:LEVel \n
		Snippet: value: float = driver.trigger.anEdge.get_level() \n
		Sets the trigger level for the external trigger source. \n
			:return: ext_trig_lev: No help available
		"""
		response = self._core.io.query_str('TRIGger:ANEDge:LEVel?')
		return Conversions.str_to_float(response)

	def set_level(self, ext_trig_lev: float) -> None:
		"""TRIGger:ANEDge:LEVel \n
		Snippet: driver.trigger.anEdge.set_level(ext_trig_lev = 1.0) \n
		Sets the trigger level for the external trigger source. \n
			:param ext_trig_lev: No help available
		"""
		param = Conversions.decimal_value_to_str(ext_trig_lev)
		self._core.io.write(f'TRIGger:ANEDge:LEVel {param}')

	# noinspection PyTypeChecker
	def get_coupling(self) -> enums.Coupling:
		"""TRIGger:ANEDge:COUPling \n
		Snippet: value: enums.Coupling = driver.trigger.anEdge.get_coupling() \n
		Sets the connection of the external trigger signal, i.e. the input impedance and a termination. The coupling determines
		what part of the signal is used for triggering. \n
			:return: coupling:
				- DC: Connection with 50 Ω termination, passes both DC and AC components of the signal.
				- DCLimit: Connection with 1 MΩ termination, passes both DC and AC components of the signal.
				- AC: Connection with 1 MΩ termination through DC capacitor, removes DC and very low-frequency components. The waveform is centered on zero volts."""
		response = self._core.io.query_str('TRIGger:ANEDge:COUPling?')
		return Conversions.str_to_scalar_enum(response, enums.Coupling)

	def set_coupling(self, coupling: enums.Coupling) -> None:
		"""TRIGger:ANEDge:COUPling \n
		Snippet: driver.trigger.anEdge.set_coupling(coupling = enums.Coupling.AC) \n
		Sets the connection of the external trigger signal, i.e. the input impedance and a termination. The coupling determines
		what part of the signal is used for triggering. \n
			:param coupling:
				- DC: Connection with 50 Ω termination, passes both DC and AC components of the signal.
				- DCLimit: Connection with 1 MΩ termination, passes both DC and AC components of the signal.
				- AC: Connection with 1 MΩ termination through DC capacitor, removes DC and very low-frequency components. The waveform is centered on zero volts."""
		param = Conversions.enum_scalar_to_str(coupling, enums.Coupling)
		self._core.io.write(f'TRIGger:ANEDge:COUPling {param}')

	# noinspection PyTypeChecker
	def get_filter_py(self) -> enums.TrigFilterMode:
		"""TRIGger:ANEDge:FILTer \n
		Snippet: value: enums.TrigFilterMode = driver.trigger.anEdge.get_filter_py() \n
		Selects the filter mode for the external trigger signal. \n
			:return: filter_py: No help available
		"""
		response = self._core.io.query_str('TRIGger:ANEDge:FILTer?')
		return Conversions.str_to_scalar_enum(response, enums.TrigFilterMode)

	def set_filter_py(self, filter_py: enums.TrigFilterMode) -> None:
		"""TRIGger:ANEDge:FILTer \n
		Snippet: driver.trigger.anEdge.set_filter_py(filter_py = enums.TrigFilterMode.LFReject) \n
		Selects the filter mode for the external trigger signal. \n
			:param filter_py: No help available
		"""
		param = Conversions.enum_scalar_to_str(filter_py, enums.TrigFilterMode)
		self._core.io.write(f'TRIGger:ANEDge:FILTer {param}')

	def get_gnd(self) -> bool:
		"""TRIGger:ANEDge:GND \n
		Snippet: value: bool = driver.trigger.anEdge.get_gnd() \n
		No command help available \n
			:return: ground: No help available
		"""
		response = self._core.io.query_str('TRIGger:ANEDge:GND?')
		return Conversions.str_to_bool(response)

	def set_gnd(self, ground: bool) -> None:
		"""TRIGger:ANEDge:GND \n
		Snippet: driver.trigger.anEdge.set_gnd(ground = False) \n
		No command help available \n
			:param ground: No help available
		"""
		param = Conversions.bool_to_str(ground)
		self._core.io.write(f'TRIGger:ANEDge:GND {param}')

	def get_nreject(self) -> bool:
		"""TRIGger:ANEDge:NREJect \n
		Snippet: value: bool = driver.trigger.anEdge.get_nreject() \n
		Enables an automatic hysteresis on the trigger level to avoid unwanted trigger events caused by noise. \n
			:return: noise_reject: No help available
		"""
		response = self._core.io.query_str('TRIGger:ANEDge:NREJect?')
		return Conversions.str_to_bool(response)

	def set_nreject(self, noise_reject: bool) -> None:
		"""TRIGger:ANEDge:NREJect \n
		Snippet: driver.trigger.anEdge.set_nreject(noise_reject = False) \n
		Enables an automatic hysteresis on the trigger level to avoid unwanted trigger events caused by noise. \n
			:param noise_reject: No help available
		"""
		param = Conversions.bool_to_str(noise_reject)
		self._core.io.write(f'TRIGger:ANEDge:NREJect {param}')

	def clone(self) -> 'AnEdgeCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = AnEdgeCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
