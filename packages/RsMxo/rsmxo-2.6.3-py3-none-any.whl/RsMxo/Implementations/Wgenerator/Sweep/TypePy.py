from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TypePyCls:
	"""TypePy commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("typePy", core, parent)

	def set(self, type_py: enums.AxisMode, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:SWEep:TYPE \n
		Snippet: driver.wgenerator.sweep.typePy.set(type_py = enums.AxisMode.LIN, waveformGen = repcap.WaveformGen.Default) \n
		Sets the type of the sweep, a linear or logarithmic change of the frequency. \n
			:param type_py: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.AxisMode)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:SWEep:TYPE {param}')

	# noinspection PyTypeChecker
	def get(self, waveformGen=repcap.WaveformGen.Default) -> enums.AxisMode:
		"""WGENerator<*>:SWEep:TYPE \n
		Snippet: value: enums.AxisMode = driver.wgenerator.sweep.typePy.get(waveformGen = repcap.WaveformGen.Default) \n
		Sets the type of the sweep, a linear or logarithmic change of the frequency. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: type_py: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:SWEep:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.AxisMode)
