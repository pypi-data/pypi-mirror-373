from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ModeCls:
	"""Mode commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mode", core, parent)

	def set(self, mode: enums.ProbeSetupMode, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:MODE \n
		Snippet: driver.probe.setup.mode.set(mode = enums.ProbeSetupMode.AUToset, probe = repcap.Probe.Default) \n
		The micro button is located on the probe head. Pressing this button, you initiate an action on the instrument directly
		from the probe. The button is disabled during internal automatic processes, for example, during self-alignment, autoset,
		and level detection. Select the action that you want to start from the probe. \n
			:param mode:
				- RCONtinuous: Run continuous: the acquisition is running as long as the probe button is pressed.
				- RSINgle: Run single: starts a defined number of acquisitions (same as Single key) .
				- AUToset: Starts the autoset procedure.
				- AZERo: AutoZero: performs an automatic correction of the zero error.
				- OTMean: Set offset to mean: performs an automatic compensation for a DC component of the input signal.
				- SITFile: Save image to file: saves the display image in a file.
				- NOACtion: Nothing is started on pressing the micro button.
				- FTRiglevel: Sets the trigger level automatically to 0.5 * (MaxPeak – MinPeak) . The function is not available for an external trigger source.
				- PRSetup: Opens the Probes Setup dialog box.
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')"""
		param = Conversions.enum_scalar_to_str(mode, enums.ProbeSetupMode)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:MODE {param}')

	# noinspection PyTypeChecker
	def get(self, probe=repcap.Probe.Default) -> enums.ProbeSetupMode:
		"""PROBe<*>:SETup:MODE \n
		Snippet: value: enums.ProbeSetupMode = driver.probe.setup.mode.get(probe = repcap.Probe.Default) \n
		The micro button is located on the probe head. Pressing this button, you initiate an action on the instrument directly
		from the probe. The button is disabled during internal automatic processes, for example, during self-alignment, autoset,
		and level detection. Select the action that you want to start from the probe. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: mode:
				- RCONtinuous: Run continuous: the acquisition is running as long as the probe button is pressed.
				- RSINgle: Run single: starts a defined number of acquisitions (same as Single key) .
				- AUToset: Starts the autoset procedure.
				- AZERo: AutoZero: performs an automatic correction of the zero error.
				- OTMean: Set offset to mean: performs an automatic compensation for a DC component of the input signal.
				- SITFile: Save image to file: saves the display image in a file.
				- NOACtion: Nothing is started on pressing the micro button.
				- FTRiglevel: Sets the trigger level automatically to 0.5 * (MaxPeak – MinPeak) . The function is not available for an external trigger source.
				- PRSetup: Opens the Probes Setup dialog box."""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.ProbeSetupMode)
