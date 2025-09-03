from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ActionsCls:
	"""Actions commands group definition. 16 total commands, 1 Subgroups, 6 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("actions", core, parent)

	@property
	def out(self):
		"""out commands group. 1 Sub-classes, 5 commands."""
		if not hasattr(self, '_out'):
			from .Out import OutCls
			self._out = OutCls(self._core, self._cmd_group)
		return self._out

	# noinspection PyTypeChecker
	def get_beep(self) -> enums.TriggerAction:
		"""TRIGger:ACTions:BEEP \n
		Snippet: value: enums.TriggerAction = driver.trigger.actions.get_beep() \n
		Generates a beep sound if the command is set to TRIGger. \n
			:return: beep: No help available
		"""
		response = self._core.io.query_str('TRIGger:ACTions:BEEP?')
		return Conversions.str_to_scalar_enum(response, enums.TriggerAction)

	def set_beep(self, beep: enums.TriggerAction) -> None:
		"""TRIGger:ACTions:BEEP \n
		Snippet: driver.trigger.actions.set_beep(beep = enums.TriggerAction.NOACtion) \n
		Generates a beep sound if the command is set to TRIGger. \n
			:param beep: No help available
		"""
		param = Conversions.enum_scalar_to_str(beep, enums.TriggerAction)
		self._core.io.write(f'TRIGger:ACTions:BEEP {param}')

	# noinspection PyTypeChecker
	def get_screenshot(self) -> enums.TriggerAction:
		"""TRIGger:ACTions:SCReenshot \n
		Snippet: value: enums.TriggerAction = driver.trigger.actions.get_screenshot() \n
		Saves a screenshot at each trigger if the command is set to TRIGger. To configure the screenshot settings, use the
		commands described in 'Screenshots'. \n
			:return: save_screenshot: No help available
		"""
		response = self._core.io.query_str('TRIGger:ACTions:SCReenshot?')
		return Conversions.str_to_scalar_enum(response, enums.TriggerAction)

	def set_screenshot(self, save_screenshot: enums.TriggerAction) -> None:
		"""TRIGger:ACTions:SCReenshot \n
		Snippet: driver.trigger.actions.set_screenshot(save_screenshot = enums.TriggerAction.NOACtion) \n
		Saves a screenshot at each trigger if the command is set to TRIGger. To configure the screenshot settings, use the
		commands described in 'Screenshots'. \n
			:param save_screenshot: No help available
		"""
		param = Conversions.enum_scalar_to_str(save_screenshot, enums.TriggerAction)
		self._core.io.write(f'TRIGger:ACTions:SCReenshot {param}')

	# noinspection PyTypeChecker
	def get_wfm_save(self) -> enums.TriggerAction:
		"""TRIGger:ACTions:WFMSave \n
		Snippet: value: enums.TriggerAction = driver.trigger.actions.get_wfm_save() \n
		Saves the waveform data to file at each trigger if the command is set to TRIGger.
			INTRO_CMD_HELP: To define the path and file names, use the EXPort:WAVeform:AUTonaming:* commands: \n
			- method RsMxo.Export.Waveform.AutoNaming.name
			- method RsMxo.Export.Waveform.AutoNaming.path
			- method RsMxo.Export.Waveform.AutoNaming.typePy  \n
			:return: save_wfm: No help available
		"""
		response = self._core.io.query_str('TRIGger:ACTions:WFMSave?')
		return Conversions.str_to_scalar_enum(response, enums.TriggerAction)

	def set_wfm_save(self, save_wfm: enums.TriggerAction) -> None:
		"""TRIGger:ACTions:WFMSave \n
		Snippet: driver.trigger.actions.set_wfm_save(save_wfm = enums.TriggerAction.NOACtion) \n
		Saves the waveform data to file at each trigger if the command is set to TRIGger.
			INTRO_CMD_HELP: To define the path and file names, use the EXPort:WAVeform:AUTonaming:* commands: \n
			- method RsMxo.Export.Waveform.AutoNaming.name
			- method RsMxo.Export.Waveform.AutoNaming.path
			- method RsMxo.Export.Waveform.AutoNaming.typePy  \n
			:param save_wfm: No help available
		"""
		param = Conversions.enum_scalar_to_str(save_wfm, enums.TriggerAction)
		self._core.io.write(f'TRIGger:ACTions:WFMSave {param}')

	# noinspection PyTypeChecker
	def get_stop(self) -> enums.TriggerAction:
		"""TRIGger:ACTions:STOP \n
		Snippet: value: enums.TriggerAction = driver.trigger.actions.get_stop() \n
		Stops the running acquisition if the command is set to TRIGger. \n
			:return: stop_acq: No help available
		"""
		response = self._core.io.query_str('TRIGger:ACTions:STOP?')
		return Conversions.str_to_scalar_enum(response, enums.TriggerAction)

	def set_stop(self, stop_acq: enums.TriggerAction) -> None:
		"""TRIGger:ACTions:STOP \n
		Snippet: driver.trigger.actions.set_stop(stop_acq = enums.TriggerAction.NOACtion) \n
		Stops the running acquisition if the command is set to TRIGger. \n
			:param stop_acq: No help available
		"""
		param = Conversions.enum_scalar_to_str(stop_acq, enums.TriggerAction)
		self._core.io.write(f'TRIGger:ACTions:STOP {param}')

	# noinspection PyTypeChecker
	def get_log_date(self) -> enums.TriggerAction:
		"""TRIGger:ACTions:LOGDate \n
		Snippet: value: enums.TriggerAction = driver.trigger.actions.get_log_date() \n
		No command help available \n
			:return: log_date: No help available
		"""
		response = self._core.io.query_str('TRIGger:ACTions:LOGDate?')
		return Conversions.str_to_scalar_enum(response, enums.TriggerAction)

	def set_log_date(self, log_date: enums.TriggerAction) -> None:
		"""TRIGger:ACTions:LOGDate \n
		Snippet: driver.trigger.actions.set_log_date(log_date = enums.TriggerAction.NOACtion) \n
		No command help available \n
			:param log_date: No help available
		"""
		param = Conversions.enum_scalar_to_str(log_date, enums.TriggerAction)
		self._core.io.write(f'TRIGger:ACTions:LOGDate {param}')

	# noinspection PyTypeChecker
	def get_report(self) -> enums.TriggerAction:
		"""TRIGger:ACTions:REPort \n
		Snippet: value: enums.TriggerAction = driver.trigger.actions.get_report() \n
		No command help available \n
			:return: report: No help available
		"""
		response = self._core.io.query_str('TRIGger:ACTions:REPort?')
		return Conversions.str_to_scalar_enum(response, enums.TriggerAction)

	def set_report(self, report: enums.TriggerAction) -> None:
		"""TRIGger:ACTions:REPort \n
		Snippet: driver.trigger.actions.set_report(report = enums.TriggerAction.NOACtion) \n
		No command help available \n
			:param report: No help available
		"""
		param = Conversions.enum_scalar_to_str(report, enums.TriggerAction)
		self._core.io.write(f'TRIGger:ACTions:REPort {param}')

	def clone(self) -> 'ActionsCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ActionsCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
