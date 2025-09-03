from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FormatPyCls:
	"""FormatPy commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("formatPy", core, parent)

	def set(self, data_format: enums.SbusDataFormat, pwrBus=repcap.PwrBus.Default) -> None:
		"""PBUS<*>:DATA:FORMat \n
		Snippet: driver.pbus.data.formatPy.set(data_format = enums.SbusDataFormat.ASCII, pwrBus = repcap.PwrBus.Default) \n
		Sets the data format of bus values, which are displayed in the decode table and on the comb bus display. It also sets the
		format for the number representation for remote data transfer with method RsMxo.Pbus.Data.Values.get_. \n
			:param data_format: No help available
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
		"""
		param = Conversions.enum_scalar_to_str(data_format, enums.SbusDataFormat)
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		self._core.io.write(f'PBUS{pwrBus_cmd_val}:DATA:FORMat {param}')

	# noinspection PyTypeChecker
	def get(self, pwrBus=repcap.PwrBus.Default) -> enums.SbusDataFormat:
		"""PBUS<*>:DATA:FORMat \n
		Snippet: value: enums.SbusDataFormat = driver.pbus.data.formatPy.get(pwrBus = repcap.PwrBus.Default) \n
		Sets the data format of bus values, which are displayed in the decode table and on the comb bus display. It also sets the
		format for the number representation for remote data transfer with method RsMxo.Pbus.Data.Values.get_. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:return: data_format: No help available"""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		response = self._core.io.query_str(f'PBUS{pwrBus_cmd_val}:DATA:FORMat?')
		return Conversions.str_to_scalar_enum(response, enums.SbusDataFormat)
