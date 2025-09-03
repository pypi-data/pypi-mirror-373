from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TriggerCls:
	"""Trigger commands group definition. 593 total commands, 11 Subgroups, 5 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("trigger", core, parent)

	@property
	def sbsw(self):
		"""sbsw commands group. 17 Sub-classes, 0 commands."""
		if not hasattr(self, '_sbsw'):
			from .Sbsw import SbswCls
			self._sbsw = SbswCls(self._core, self._cmd_group)
		return self._sbsw

	@property
	def sbhw(self):
		"""sbhw commands group. 5 Sub-classes, 0 commands."""
		if not hasattr(self, '_sbhw'):
			from .Sbhw import SbhwCls
			self._sbhw = SbhwCls(self._core, self._cmd_group)
		return self._sbhw

	@property
	def findLevel(self):
		"""findLevel commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_findLevel'):
			from .FindLevel import FindLevelCls
			self._findLevel = FindLevelCls(self._core, self._cmd_group)
		return self._findLevel

	@property
	def force(self):
		"""force commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_force'):
			from .Force import ForceCls
			self._force = ForceCls(self._core, self._cmd_group)
		return self._force

	@property
	def actions(self):
		"""actions commands group. 1 Sub-classes, 6 commands."""
		if not hasattr(self, '_actions'):
			from .Actions import ActionsCls
			self._actions = ActionsCls(self._core, self._cmd_group)
		return self._actions

	@property
	def anEdge(self):
		"""anEdge commands group. 2 Sub-classes, 5 commands."""
		if not hasattr(self, '_anEdge'):
			from .AnEdge import AnEdgeCls
			self._anEdge = AnEdgeCls(self._core, self._cmd_group)
		return self._anEdge

	@property
	def event(self):
		"""event commands group. 14 Sub-classes, 0 commands."""
		if not hasattr(self, '_event'):
			from .Event import EventCls
			self._event = EventCls(self._core, self._cmd_group)
		return self._event

	@property
	def holdoff(self):
		"""holdoff commands group. 0 Sub-classes, 7 commands."""
		if not hasattr(self, '_holdoff'):
			from .Holdoff import HoldoffCls
			self._holdoff = HoldoffCls(self._core, self._cmd_group)
		return self._holdoff

	@property
	def mevents(self):
		"""mevents commands group. 1 Sub-classes, 2 commands."""
		if not hasattr(self, '_mevents'):
			from .Mevents import MeventsCls
			self._mevents = MeventsCls(self._core, self._cmd_group)
		return self._mevents

	@property
	def noise(self):
		"""noise commands group. 6 Sub-classes, 0 commands."""
		if not hasattr(self, '_noise'):
			from .Noise import NoiseCls
			self._noise = NoiseCls(self._core, self._cmd_group)
		return self._noise

	@property
	def zone(self):
		"""zone commands group. 1 Sub-classes, 1 commands."""
		if not hasattr(self, '_zone'):
			from .Zone import ZoneCls
			self._zone = ZoneCls(self._core, self._cmd_group)
		return self._zone

	# noinspection PyTypeChecker
	def get_filter_mode(self) -> enums.TrigFilterMode:
		"""TRIGger:FILTermode \n
		Snippet: value: enums.TrigFilterMode = driver.trigger.get_filter_mode() \n
		Selects the filter mode for the trigger channel. \n
			:return: trig_filter_md: No help available
		"""
		response = self._core.io.query_str('TRIGger:FILTermode?')
		return Conversions.str_to_scalar_enum(response, enums.TrigFilterMode)

	def set_filter_mode(self, trig_filter_md: enums.TrigFilterMode) -> None:
		"""TRIGger:FILTermode \n
		Snippet: driver.trigger.set_filter_mode(trig_filter_md = enums.TrigFilterMode.LFReject) \n
		Selects the filter mode for the trigger channel. \n
			:param trig_filter_md: No help available
		"""
		param = Conversions.enum_scalar_to_str(trig_filter_md, enums.TrigFilterMode)
		self._core.io.write(f'TRIGger:FILTermode {param}')

	def get_lf_reject(self) -> float:
		"""TRIGger:LFReject \n
		Snippet: value: float = driver.trigger.get_lf_reject() \n
		Sets the limit frequency limit for the highpass filter of the trigger signal. Frequencies lower than this value are
		rejected, higher frequencies pass the filter. \n
			:return: trig_cpl_lf_reject_bw: No help available
		"""
		response = self._core.io.query_str('TRIGger:LFReject?')
		return Conversions.str_to_float(response)

	def set_lf_reject(self, trig_cpl_lf_reject_bw: float) -> None:
		"""TRIGger:LFReject \n
		Snippet: driver.trigger.set_lf_reject(trig_cpl_lf_reject_bw = 1.0) \n
		Sets the limit frequency limit for the highpass filter of the trigger signal. Frequencies lower than this value are
		rejected, higher frequencies pass the filter. \n
			:param trig_cpl_lf_reject_bw: No help available
		"""
		param = Conversions.decimal_value_to_str(trig_cpl_lf_reject_bw)
		self._core.io.write(f'TRIGger:LFReject {param}')

	# noinspection PyTypeChecker
	def get_mode(self) -> enums.TriggerMode:
		"""TRIGger:MODE \n
		Snippet: value: enums.TriggerMode = driver.trigger.get_mode() \n
		Sets the trigger mode which determines the behavior of the instrument with and without a trigger event. \n
			:return: trigger_mode:
				- AUTO: The instrument triggers repeatedly after a time interval if the trigger conditions are not fulfilled. If a real trigger occurs, it takes precedence. The time interval depends on the time base.
				- NORMal: The instrument acquires a waveform only if a trigger occurs.
				- FREerun: The instrument triggers after a very short time interval - faster than in AUTO mode. Real triggers are ignored."""
		response = self._core.io.query_str('TRIGger:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.TriggerMode)

	def set_mode(self, trigger_mode: enums.TriggerMode) -> None:
		"""TRIGger:MODE \n
		Snippet: driver.trigger.set_mode(trigger_mode = enums.TriggerMode.AUTO) \n
		Sets the trigger mode which determines the behavior of the instrument with and without a trigger event. \n
			:param trigger_mode:
				- AUTO: The instrument triggers repeatedly after a time interval if the trigger conditions are not fulfilled. If a real trigger occurs, it takes precedence. The time interval depends on the time base.
				- NORMal: The instrument acquires a waveform only if a trigger occurs.
				- FREerun: The instrument triggers after a very short time interval - faster than in AUTO mode. Real triggers are ignored."""
		param = Conversions.enum_scalar_to_str(trigger_mode, enums.TriggerMode)
		self._core.io.write(f'TRIGger:MODE {param}')

	def get_rf_reject(self) -> float:
		"""TRIGger:RFReject \n
		Snippet: value: float = driver.trigger.get_rf_reject() \n
		Sets the limit frequency limit for the lowpass filter of the trigger signal. Frequencies higher than this value are
		rejected, lower frequencies pass the filter. \n
			:return: trig_cpl_hf_reject_bw: No help available
		"""
		response = self._core.io.query_str('TRIGger:RFReject?')
		return Conversions.str_to_float(response)

	def set_rf_reject(self, trig_cpl_hf_reject_bw: float) -> None:
		"""TRIGger:RFReject \n
		Snippet: driver.trigger.set_rf_reject(trig_cpl_hf_reject_bw = 1.0) \n
		Sets the limit frequency limit for the lowpass filter of the trigger signal. Frequencies higher than this value are
		rejected, lower frequencies pass the filter. \n
			:param trig_cpl_hf_reject_bw: No help available
		"""
		param = Conversions.decimal_value_to_str(trig_cpl_hf_reject_bw)
		self._core.io.write(f'TRIGger:RFReject {param}')

	def get_scoupling(self) -> bool:
		"""TRIGger:SCOupling \n
		Snippet: value: bool = driver.trigger.get_scoupling() \n
		No command help available \n
			:return: trig_lev_src_cpl: No help available
		"""
		response = self._core.io.query_str('TRIGger:SCOupling?')
		return Conversions.str_to_bool(response)

	def set_scoupling(self, trig_lev_src_cpl: bool) -> None:
		"""TRIGger:SCOupling \n
		Snippet: driver.trigger.set_scoupling(trig_lev_src_cpl = False) \n
		No command help available \n
			:param trig_lev_src_cpl: No help available
		"""
		param = Conversions.bool_to_str(trig_lev_src_cpl)
		self._core.io.write(f'TRIGger:SCOupling {param}')

	def clone(self) -> 'TriggerCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = TriggerCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
