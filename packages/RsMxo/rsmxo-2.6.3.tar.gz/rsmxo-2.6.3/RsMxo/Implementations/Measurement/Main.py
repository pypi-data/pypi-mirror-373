from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MainCls:
	"""Main commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("main", core, parent)

	def set(self, meas_type: enums.MeasType, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<mg>:MAIN \n
		Snippet: driver.measurement.main.set(meas_type = enums.MeasType.AMPLitude, measIndex = repcap.MeasIndex.Default) \n
		Defines the measurement type to be performed. To query the result, use method RsMxo.Measurement.Result.Actual.get_. \n
			:param meas_type:
				- Amplitude/time measurements: HIGH | LOW | AMPLitude | MAXimum | MINimum | PDELta | MEAN | RMS | STDDev | CRESt | POVershoot | NOVershoot | AREA | RTIMe | FTIMe | PPULse | NPULse | PERiod | FREQuency | PDCYcle | NDCYcle | CYCarea | CYCMean | CYCRms | CYCStddev | CYCCrest | CAMPlitude | CMAXimum | CMINimum | CPDelta | PULCnt | DELay | PHASe | BWIDth | EDGecount | SETup | HOLD | SHT | SHR | DTOTrigger | SLERising | SLEFalling
				- Jitter measurements: CCJitter | NCJitter | CCWidth | CCDutycycle | TIE | UINTerval | DRATe | SKWDelay | SKWPhaseRequire option R&S MXO5-K12.
				- Measurements for serial protocols: F2F | T2F | F2T | FLDValue | MBITrate | SBITrate | BIDLe | GAP | FCNT | FEC | FER | CFERRequire option R&S MXO5-K500.
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')"""
		param = Conversions.enum_scalar_to_str(meas_type, enums.MeasType)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:MAIN {param}')
