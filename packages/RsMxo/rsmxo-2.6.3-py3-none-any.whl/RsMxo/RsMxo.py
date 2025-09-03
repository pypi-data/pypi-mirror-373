from typing import ClassVar, List

from .Internal.Core import Core
from .Internal.InstrumentErrors import RsInstrException
from .Internal.CommandsGroup import CommandsGroup
from .Internal.VisaSession import VisaSession
from datetime import datetime, timedelta


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RsMxo:
	"""2816 total commands, 45 Subgroups, 1 group commands"""
	_driver_options = "SupportedInstrModels = MXO, SupportedIdnPatterns = MXO, SimulationIdnString = 'Rohde&Schwarz,MXO,100001,2.6.3.0060'"
	_global_logging_relative_timestamp: ClassVar[datetime] = None
	_global_logging_target_stream: ClassVar = None

	def __init__(self, resource_name: str, id_query: bool = True, reset: bool = False, options: str = None, direct_session: object = None):
		"""Initializes new RsMxo session. \n
		Parameter options tokens examples:
			- ``Simulate=True`` - starts the session in simulation mode. Default: ``False``
			- ``SelectVisa=socket`` - uses no VISA implementation for socket connections - you do not need any VISA-C installation
			- ``SelectVisa=rs`` - forces usage of RohdeSchwarz Visa
			- ``SelectVisa=ivi`` - forces usage of National Instruments Visa
			- ``QueryInstrumentStatus = False`` - same as ``driver.utilities.instrument_status_checking = False``. Default: ``True``
			- ``WriteDelay = 20, ReadDelay = 5`` - Introduces delay of 20ms before each write and 5ms before each read. Default: ``0ms`` for both
			- ``OpcWaitMode = OpcQuery`` - mode for all the opc-synchronised write/reads. Other modes: StbPolling, StbPollingSlow, StbPollingSuperSlow. Default: ``StbPolling``
			- ``AddTermCharToWriteBinBLock = True`` - Adds one additional LF to the end of the binary data (some instruments require that). Default: ``False``
			- ``AssureWriteWithTermChar = True`` - Makes sure each command/query is terminated with termination character. Default: Interface dependent
			- ``TerminationCharacter = "\\r"`` - Sets the termination character for reading. Default: ``\\n`` (LineFeed or LF)
			- ``DataChunkSize = 10E3`` - Maximum size of one write/read segment. If transferred data is bigger, it is split to more segments. Default: ``1E6`` bytes
			- ``OpcTimeout = 10000`` - same as driver.utilities.opc_timeout = 10000. Default: ``30000ms``
			- ``VisaTimeout = 5000`` - same as driver.utilities.visa_timeout = 5000. Default: ``10000ms``
			- ``ViClearExeMode = Disabled`` - viClear() execution mode. Default: ``execute_on_all``
			- ``OpcQueryAfterWrite = True`` - same as driver.utilities.opc_query_after_write = True. Default: ``False``
			- ``StbInErrorCheck = False`` - if true, the driver checks errors with *STB? If false, it uses SYST:ERR?. Default: ``True``
			- ``ScpiQuotes = double'. - for SCPI commands, you can define how strings are quoted. With single or double quotes. Possible values: single | double | {char}. Default: ``single``
			- ``LoggingMode = On`` - Sets the logging status right from the start. Default: ``Off``
			- ``LoggingName = 'MyDevice'`` - Sets the name to represent the session in the log entries. Default: ``'resource_name'``
			- ``LogToGlobalTarget = True`` - Sets the logging target to the class-property previously set with RsMxo.set_global_logging_target() Default: ``False``
			- ``LoggingToConsole = True`` - Immediately starts logging to the console. Default: False
			- ``LoggingToUdp = True`` - Immediately starts logging to the UDP port. Default: False
			- ``LoggingUdpPort = 49200`` - UDP port to log to. Default: 49200
		:param resource_name: VISA resource name, e.g. 'TCPIP::192.168.2.1::INSTR'
		:param id_query: if True, the instrument's model name is verified against the models supported by the driver and eventually throws an exception.
		:param reset: Resets the instrument (sends *RST command) and clears its status sybsystem.
		:param options: string tokens alternating the driver settings.
		:param direct_session: Another driver object or pyVisa object to reuse the session instead of opening a new session."""
		self._core = Core(resource_name, id_query, reset, RsMxo._driver_options, options, direct_session)
		self._core.driver_version = '2.6.3.0060'
		self._options = options
		self._add_all_global_repcaps()
		self._custom_properties_init()
		self.utilities.default_instrument_setup()
		# noinspection PyTypeChecker
		self._cmd_group = CommandsGroup("ROOT", self._core, None)

	@classmethod
	def from_existing_session(cls, session: object, options: str = None) -> 'RsMxo':
		"""Creates a new RsMxo object with the entered 'session' reused. \n
		:param session: can be another driver or a direct pyvisa session.
		:param options: string tokens alternating the driver settings."""
		# noinspection PyTypeChecker
		resource_name = None
		if hasattr(session, 'resource_name'):
			resource_name = getattr(session, 'resource_name')
		return cls(resource_name, False, False, options, session)
		
	@classmethod
	def set_global_logging_target(cls, target) -> None:
		"""Sets global common target stream that each instance can use. To use it, call the following: io.utilities.logger.set_logging_target_global().
		If an instance uses global logging target, it automatically uses the global relative timestamp (if set).
		You can set the target to None to invalidate it."""
		cls._global_logging_target_stream = target

	@classmethod
	def get_global_logging_target(cls):
		"""Returns global common target stream."""
		return cls._global_logging_target_stream

	@classmethod
	def set_global_logging_relative_timestamp(cls, timestamp: datetime) -> None:
		"""Sets global common relative timestamp for log entries. To use it, call the following: io.utilities.logger.set_relative_timestamp_global()"""
		cls._global_logging_relative_timestamp = timestamp

	@classmethod
	def set_global_logging_relative_timestamp_now(cls) -> None:
		"""Sets global common relative timestamp for log entries to this moment.
		To use it, call the following: io.utilities.logger.set_relative_timestamp_global()."""
		cls._global_logging_relative_timestamp = datetime.now()

	@classmethod
	def clear_global_logging_relative_timestamp(cls) -> None:
		"""Clears the global relative timestamp. After this, all the instances using the global relative timestamp continue logging with the absolute timestamps."""
		# noinspection PyTypeChecker
		cls._global_logging_relative_timestamp = None

	@classmethod
	def get_global_logging_relative_timestamp(cls) -> datetime or None:
		"""Returns global common relative timestamp for log entries."""
		return cls._global_logging_relative_timestamp

	def __str__(self) -> str:
		if self._core.io:
			return f"RsMxo session '{self._core.io.resource_name}'"
		else:
			return f"RsMxo with session closed"

	def get_total_execution_time(self) -> timedelta:
		"""Returns total time spent by the library on communicating with the instrument.
		This time is always shorter than get_total_time(), since it does not include gaps between the communication.
		You can reset this counter with reset_time_statistics()."""
		return self._core.io.total_execution_time

	def get_total_time(self) -> timedelta:
		"""Returns total time spent by the library on communicating with the instrument.
		This time is always shorter than get_total_time(), since it does not include gaps between the communication.
		You can reset this counter with reset_time_statistics()."""
		return datetime.now() - self._core.io.total_time_startpoint

	def reset_time_statistics(self) -> None:
		"""Resets all execution and total time counters. Affects the results of get_total_time() and get_total_execution_time()"""
		self._core.io.reset_time_statistics()

	@staticmethod
	def assert_minimum_version(min_version: str) -> None:
		"""Asserts that the driver version fulfills the minimum required version you have entered.
		This way you make sure your installed driver is of the entered version or newer."""
		min_version_list = min_version.split('.')
		curr_version_list = '2.6.3.0060'.split('.')
		count_min = len(min_version_list)
		count_curr = len(curr_version_list)
		count = count_min if count_min < count_curr else count_curr
		for i in range(count):
			minimum = int(min_version_list[i])
			curr = int(curr_version_list[i])
			if curr > minimum:
				break
			if curr < minimum:
				raise RsInstrException(f"Assertion for minimum RsMxo version failed. Current version: '2.6.3.0060', minimum required version: '{min_version}'")

	@staticmethod
	def list_resources(expression: str = '?*::INSTR', visa_select: str = None) -> List[str]:
		"""Finds all the resources defined by the expression
			- '?*' - matches all the available instruments
			- 'USB::?*' - matches all the USB instruments
			- 'TCPIP::192?*' - matches all the LAN instruments with the IP address starting with 192
		:param expression: see the examples in the function
		:param visa_select: optional parameter selecting a specific VISA. Examples: '@ivi', '@rs'
		"""
		rm = VisaSession.get_resource_manager(visa_select)
		resources = rm.list_resources(expression)
		rm.close()
		# noinspection PyTypeChecker
		return resources

	def close(self) -> None:
		"""Closes the active RsMxo session."""
		self._core.io.close()

	def get_session_handle(self) -> object:
		"""Returns the underlying session handle."""
		return self._core.get_session_handle()

	def _add_all_global_repcaps(self) -> None:
		"""Adds all the repcaps defined as global to the instrument's global repcaps dictionary."""

	def _custom_properties_init(self) -> None:
		"""Adds all the interfaces that are custom for the driver."""
		from .CustomFiles.utilities import Utilities
		self.utilities = Utilities(self._core)
		from .CustomFiles.events import Events
		self.events = Events(self._core)
		
	def _sync_to_custom_properties(self, cloned: 'RsMxo') -> None:
		"""Synchronises the state of all the custom properties to the entered object."""
		cloned.utilities.sync_from(self.utilities)
		cloned.events.sync_from(self.events)

	@property
	def display(self):
		"""display commands group. 11 Sub-classes, 1 commands."""
		if not hasattr(self, '_display'):
			from .Implementations.Display import DisplayCls
			self._display = DisplayCls(self._core, self._cmd_group)
		return self._display

	@property
	def calculate(self):
		"""calculate commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_calculate'):
			from .Implementations.Calculate import CalculateCls
			self._calculate = CalculateCls(self._core, self._cmd_group)
		return self._calculate

	@property
	def layout(self):
		"""layout commands group. 10 Sub-classes, 0 commands."""
		if not hasattr(self, '_layout'):
			from .Implementations.Layout import LayoutCls
			self._layout = LayoutCls(self._core, self._cmd_group)
		return self._layout

	@property
	def measurement(self):
		"""measurement commands group. 24 Sub-classes, 1 commands."""
		if not hasattr(self, '_measurement'):
			from .Implementations.Measurement import MeasurementCls
			self._measurement = MeasurementCls(self._core, self._cmd_group)
		return self._measurement

	@property
	def refCurve(self):
		"""refCurve commands group. 14 Sub-classes, 4 commands."""
		if not hasattr(self, '_refCurve'):
			from .Implementations.RefCurve import RefCurveCls
			self._refCurve = RefCurveCls(self._core, self._cmd_group)
		return self._refCurve

	@property
	def export(self):
		"""export commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_export'):
			from .Implementations.Export import ExportCls
			self._export = ExportCls(self._core, self._cmd_group)
		return self._export

	@property
	def franalysis(self):
		"""franalysis commands group. 14 Sub-classes, 5 commands."""
		if not hasattr(self, '_franalysis'):
			from .Implementations.Franalysis import FranalysisCls
			self._franalysis = FranalysisCls(self._core, self._cmd_group)
		return self._franalysis

	@property
	def hardCopy(self):
		"""hardCopy commands group. 2 Sub-classes, 5 commands."""
		if not hasattr(self, '_hardCopy'):
			from .Implementations.HardCopy import HardCopyCls
			self._hardCopy = HardCopyCls(self._core, self._cmd_group)
		return self._hardCopy

	@property
	def service(self):
		"""service commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_service'):
			from .Implementations.Service import ServiceCls
			self._service = ServiceCls(self._core, self._cmd_group)
		return self._service

	@property
	def userDefined(self):
		"""userDefined commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_userDefined'):
			from .Implementations.UserDefined import UserDefinedCls
			self._userDefined = UserDefinedCls(self._core, self._cmd_group)
		return self._userDefined

	@property
	def power(self):
		"""power commands group. 7 Sub-classes, 0 commands."""
		if not hasattr(self, '_power'):
			from .Implementations.Power import PowerCls
			self._power = PowerCls(self._core, self._cmd_group)
		return self._power

	@property
	def wgenerator(self):
		"""wgenerator commands group. 14 Sub-classes, 1 commands."""
		if not hasattr(self, '_wgenerator'):
			from .Implementations.Wgenerator import WgeneratorCls
			self._wgenerator = WgeneratorCls(self._core, self._cmd_group)
		return self._wgenerator

	@property
	def system(self):
		"""system commands group. 7 Sub-classes, 2 commands."""
		if not hasattr(self, '_system'):
			from .Implementations.System import SystemCls
			self._system = SystemCls(self._core, self._cmd_group)
		return self._system

	@property
	def run(self):
		"""run commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_run'):
			from .Implementations.Run import RunCls
			self._run = RunCls(self._core, self._cmd_group)
		return self._run

	@property
	def massMemory(self):
		"""massMemory commands group. 7 Sub-classes, 10 commands."""
		if not hasattr(self, '_massMemory'):
			from .Implementations.MassMemory import MassMemoryCls
			self._massMemory = MassMemoryCls(self._core, self._cmd_group)
		return self._massMemory

	@property
	def channel(self):
		"""channel commands group. 20 Sub-classes, 0 commands."""
		if not hasattr(self, '_channel'):
			from .Implementations.Channel import ChannelCls
			self._channel = ChannelCls(self._core, self._cmd_group)
		return self._channel

	@property
	def digital(self):
		"""digital commands group. 10 Sub-classes, 0 commands."""
		if not hasattr(self, '_digital'):
			from .Implementations.Digital import DigitalCls
			self._digital = DigitalCls(self._core, self._cmd_group)
		return self._digital

	@property
	def trfs(self):
		"""trfs commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_trfs'):
			from .Implementations.Trfs import TrfsCls
			self._trfs = TrfsCls(self._core, self._cmd_group)
		return self._trfs

	@property
	def treference(self):
		"""treference commands group. 11 Sub-classes, 0 commands."""
		if not hasattr(self, '_treference'):
			from .Implementations.Treference import TreferenceCls
			self._treference = TreferenceCls(self._core, self._cmd_group)
		return self._treference

	@property
	def sbus(self):
		"""sbus commands group. 27 Sub-classes, 0 commands."""
		if not hasattr(self, '_sbus'):
			from .Implementations.Sbus import SbusCls
			self._sbus = SbusCls(self._core, self._cmd_group)
		return self._sbus

	@property
	def trigger(self):
		"""trigger commands group. 11 Sub-classes, 5 commands."""
		if not hasattr(self, '_trigger'):
			from .Implementations.Trigger import TriggerCls
			self._trigger = TriggerCls(self._core, self._cmd_group)
		return self._trigger

	@property
	def formatPy(self):
		"""formatPy commands group. 1 Sub-classes, 2 commands."""
		if not hasattr(self, '_formatPy'):
			from .Implementations.FormatPy import FormatPyCls
			self._formatPy = FormatPyCls(self._core, self._cmd_group)
		return self._formatPy

	@property
	def saveset(self):
		"""saveset commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_saveset'):
			from .Implementations.Saveset import SavesetCls
			self._saveset = SavesetCls(self._core, self._cmd_group)
		return self._saveset

	@property
	def sessions(self):
		"""sessions commands group. 2 Sub-classes, 1 commands."""
		if not hasattr(self, '_sessions'):
			from .Implementations.Sessions import SessionsCls
			self._sessions = SessionsCls(self._core, self._cmd_group)
		return self._sessions

	@property
	def meter(self):
		"""meter commands group. 1 Sub-classes, 2 commands."""
		if not hasattr(self, '_meter'):
			from .Implementations.Meter import MeterCls
			self._meter = MeterCls(self._core, self._cmd_group)
		return self._meter

	@property
	def selftests(self):
		"""selftests commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_selftests'):
			from .Implementations.Selftests import SelftestsCls
			self._selftests = SelftestsCls(self._core, self._cmd_group)
		return self._selftests

	@property
	def generator(self):
		"""generator commands group. 2 Sub-classes, 2 commands."""
		if not hasattr(self, '_generator'):
			from .Implementations.Generator import GeneratorCls
			self._generator = GeneratorCls(self._core, self._cmd_group)
		return self._generator

	@property
	def acquire(self):
		"""acquire commands group. 5 Sub-classes, 12 commands."""
		if not hasattr(self, '_acquire'):
			from .Implementations.Acquire import AcquireCls
			self._acquire = AcquireCls(self._core, self._cmd_group)
		return self._acquire

	@property
	def calibration(self):
		"""calibration commands group. 1 Sub-classes, 3 commands."""
		if not hasattr(self, '_calibration'):
			from .Implementations.Calibration import CalibrationCls
			self._calibration = CalibrationCls(self._core, self._cmd_group)
		return self._calibration

	@property
	def cursor(self):
		"""cursor commands group. 28 Sub-classes, 0 commands."""
		if not hasattr(self, '_cursor'):
			from .Implementations.Cursor import CursorCls
			self._cursor = CursorCls(self._core, self._cmd_group)
		return self._cursor

	@property
	def mtest(self):
		"""mtest commands group. 11 Sub-classes, 0 commands."""
		if not hasattr(self, '_mtest'):
			from .Implementations.Mtest import MtestCls
			self._mtest = MtestCls(self._core, self._cmd_group)
		return self._mtest

	@property
	def zone(self):
		"""zone commands group. 8 Sub-classes, 0 commands."""
		if not hasattr(self, '_zone'):
			from .Implementations.Zone import ZoneCls
			self._zone = ZoneCls(self._core, self._cmd_group)
		return self._zone

	@property
	def gate(self):
		"""gate commands group. 8 Sub-classes, 0 commands."""
		if not hasattr(self, '_gate'):
			from .Implementations.Gate import GateCls
			self._gate = GateCls(self._core, self._cmd_group)
		return self._gate

	@property
	def probe(self):
		"""probe commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_probe'):
			from .Implementations.Probe import ProbeCls
			self._probe = ProbeCls(self._core, self._cmd_group)
		return self._probe

	@property
	def trProbe(self):
		"""trProbe commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_trProbe'):
			from .Implementations.TrProbe import TrProbeCls
			self._trProbe = TrProbeCls(self._core, self._cmd_group)
		return self._trProbe

	@property
	def refLevel(self):
		"""refLevel commands group. 5 Sub-classes, 0 commands."""
		if not hasattr(self, '_refLevel'):
			from .Implementations.RefLevel import RefLevelCls
			self._refLevel = RefLevelCls(self._core, self._cmd_group)
		return self._refLevel

	@property
	def status(self):
		"""status commands group. 1 Sub-classes, 1 commands."""
		if not hasattr(self, '_status'):
			from .Implementations.Status import StatusCls
			self._status = StatusCls(self._core, self._cmd_group)
		return self._status

	@property
	def timebase(self):
		"""timebase commands group. 2 Sub-classes, 4 commands."""
		if not hasattr(self, '_timebase'):
			from .Implementations.Timebase import TimebaseCls
			self._timebase = TimebaseCls(self._core, self._cmd_group)
		return self._timebase

	@property
	def xy(self):
		"""xy commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_xy'):
			from .Implementations.Xy import XyCls
			self._xy = XyCls(self._core, self._cmd_group)
		return self._xy

	@property
	def sense(self):
		"""sense commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_sense'):
			from .Implementations.Sense import SenseCls
			self._sense = SenseCls(self._core, self._cmd_group)
		return self._sense

	@property
	def hdefinition(self):
		"""hdefinition commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_hdefinition'):
			from .Implementations.Hdefinition import HdefinitionCls
			self._hdefinition = HdefinitionCls(self._core, self._cmd_group)
		return self._hdefinition

	@property
	def pbus(self):
		"""pbus commands group. 16 Sub-classes, 1 commands."""
		if not hasattr(self, '_pbus'):
			from .Implementations.Pbus import PbusCls
			self._pbus = PbusCls(self._core, self._cmd_group)
		return self._pbus

	@property
	def synchronize(self):
		"""synchronize commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_synchronize'):
			from .Implementations.Synchronize import SynchronizeCls
			self._synchronize = SynchronizeCls(self._core, self._cmd_group)
		return self._synchronize

	@property
	def autoScale(self):
		"""autoScale commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_autoScale'):
			from .Implementations.AutoScale import AutoScaleCls
			self._autoScale = AutoScaleCls(self._core, self._cmd_group)
		return self._autoScale

	@property
	def triggerInvoke(self):
		"""triggerInvoke commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_triggerInvoke'):
			from .Implementations.TriggerInvoke import TriggerInvokeCls
			self._triggerInvoke = TriggerInvokeCls(self._core, self._cmd_group)
		return self._triggerInvoke

	def stop(self) -> None:
		"""STOP \n
		Snippet: driver.stop() \n
		Stops the running acquisition. \n
		"""
		self._core.io.write(f'STOP')

	def stop_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""STOP \n
		Snippet: driver.stop_and_wait() \n
		Stops the running acquisition. \n
		Same as stop, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'STOP', opc_timeout_ms)

	def clone(self) -> 'RsMxo':
		"""Creates a deep copy of the RsMxo object. Also copies:
			- All the existing Global repeated capability values
			- All the default group repeated capabilities setting \n
		Does not check the *IDN? response, and does not perform Reset.
		After cloning, you can set all the repeated capabilities settings independentely from the original group.
		Calling close() on the new object does not close the original VISA session"""
		cloned = RsMxo.from_existing_session(self.get_session_handle(), self._options)
		self._cmd_group.synchronize_repcaps(cloned)
		
		self._sync_to_custom_properties(cloned)
		return cloned

	def restore_all_repcaps_to_default(self) -> None:
		"""Sets all the Group and Global repcaps to their initial values"""
		self._cmd_group.restore_repcaps()
