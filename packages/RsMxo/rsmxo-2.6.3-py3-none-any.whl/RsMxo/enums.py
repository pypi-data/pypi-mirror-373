from enum import Enum


# noinspection SpellCheckingInspection
class AbsRel(Enum):
	"""2 Members, ABS ... REL"""
	ABS = 0
	REL = 1


# noinspection SpellCheckingInspection
class AcqMd(Enum):
	"""4 Members, AVERage ... SAMPle"""
	AVERage = 0
	ENVelope = 1
	PDETect = 2
	SAMPle = 3


# noinspection SpellCheckingInspection
class AdLogic(Enum):
	"""4 Members, AND ... OR"""
	AND = 0
	NAND = 1
	NOR = 2
	OR = 3


# noinspection SpellCheckingInspection
class Algorithm(Enum):
	"""5 Members, CFRequency ... PLLRlock"""
	CFRequency = 0
	FF = 1
	FFSTart = 2
	PLL = 3
	PLLRlock = 4


# noinspection SpellCheckingInspection
class AmplitudeMode(Enum):
	"""2 Members, CONStant ... PROFile"""
	CONStant = 0
	PROFile = 1


# noinspection SpellCheckingInspection
class AmplitudeProfileVoltageChange(Enum):
	"""2 Members, RAMP ... SINGle"""
	RAMP = 0
	SINGle = 1


# noinspection SpellCheckingInspection
class AnalogChannels(Enum):
	"""8 Members, C1 ... C8"""
	C1 = 0
	C2 = 1
	C3 = 2
	C4 = 3
	C5 = 4
	C6 = 5
	C7 = 6
	C8 = 7


# noinspection SpellCheckingInspection
class AnalogCutoffFreq(Enum):
	"""3 Members, KHZ5 ... MHZ50"""
	KHZ5 = 0
	KHZ50 = 1
	MHZ50 = 2


# noinspection SpellCheckingInspection
class AreaCombination(Enum):
	"""55 Members, ABS ... XOR"""
	ABS = 0
	ACORrrelat = 1
	ACOS = 2
	ADD = 3
	AND = 4
	ASIN = 5
	ATAN = 6
	BWC = 7
	CDR = 8
	CORRelation = 9
	COS = 10
	COSH = 11
	DERivation = 12
	DIV = 13
	ELECPOWER = 14
	EQUal = 15
	EXP = 16
	FIR = 17
	GDELay = 18
	GEQual = 19
	GREater = 20
	IFFT = 21
	IMG = 22
	INTegral = 23
	INVert = 24
	LD = 25
	LEQual = 26
	LESS = 27
	LN = 28
	LOG = 29
	MA = 30
	MAG = 31
	MUL = 32
	NAND = 33
	NOR = 34
	NOT = 35
	NXOR = 36
	OR = 37
	PHI = 38
	POW = 39
	POWRational = 40
	POWZ = 41
	RE = 42
	RECiprocal = 43
	RESCale = 44
	SIN = 45
	SINC = 46
	SINH = 47
	SQRT = 48
	SUB = 49
	TAN = 50
	TANH = 51
	TOBit = 52
	UNEQual = 53
	XOR = 54


# noinspection SpellCheckingInspection
class Arithmetics(Enum):
	"""6 Members, AVERage ... RMS"""
	AVERage = 0
	ENVelope = 1
	MAXHold = 2
	MINHold = 3
	OFF = 4
	RMS = 5


# noinspection SpellCheckingInspection
class AutoManualMode(Enum):
	"""2 Members, AUTO ... MANual"""
	AUTO = 0
	MANual = 1


# noinspection SpellCheckingInspection
class AutoUser(Enum):
	"""2 Members, AUTO ... USER"""
	AUTO = 0
	USER = 1


# noinspection SpellCheckingInspection
class AxisMode(Enum):
	"""2 Members, LIN ... LOG"""
	LIN = 0
	LOG = 1


# noinspection SpellCheckingInspection
class BitOrder(Enum):
	"""2 Members, LSBF ... MSBF"""
	LSBF = 0
	MSBF = 1


# noinspection SpellCheckingInspection
class ByteOrder(Enum):
	"""2 Members, LSBFirst ... MSBFirst"""
	LSBFirst = 0
	MSBFirst = 1


# noinspection SpellCheckingInspection
class ClockSource(Enum):
	"""16 Members, D0 ... D9"""
	D0 = 0
	D1 = 1
	D10 = 2
	D11 = 3
	D12 = 4
	D13 = 5
	D14 = 6
	D15 = 7
	D2 = 8
	D3 = 9
	D4 = 10
	D5 = 11
	D6 = 12
	D7 = 13
	D8 = 14
	D9 = 15


# noinspection SpellCheckingInspection
class Color(Enum):
	"""20 Members, BLUE ... YELLow"""
	BLUE = 0
	DAGReen = 1
	DGRay = 2
	DORange = 3
	GRAY = 4
	GREen = 5
	LBLue = 6
	LGRay = 7
	LIGReen = 8
	LORange = 9
	LPINk = 10
	LPURple = 11
	MGRay = 12
	ORANge = 13
	PINK = 14
	PURPle = 15
	RED = 16
	TURQuoise = 17
	WHITe = 18
	YELLow = 19


# noinspection SpellCheckingInspection
class ColorSignal(Enum):
	"""123 Members, C1 ... XY4"""
	C1 = 0
	C2 = 1
	C3 = 2
	C4 = 3
	C5 = 4
	C6 = 5
	C7 = 6
	C8 = 7
	D0 = 8
	D1 = 9
	D10 = 10
	D11 = 11
	D12 = 12
	D13 = 13
	D14 = 14
	D15 = 15
	D2 = 16
	D3 = 17
	D4 = 18
	D5 = 19
	D6 = 20
	D7 = 21
	D8 = 22
	D9 = 23
	FAMPlitude = 24
	FGAin = 25
	FPHase = 26
	HISTogram1 = 27
	HISTogram2 = 28
	HISTogram3 = 29
	HISTogram4 = 30
	HISTogram5 = 31
	HISTogram6 = 32
	HISTogram7 = 33
	HISTogram8 = 34
	I1R1 = 35
	I1R2 = 36
	I1R3 = 37
	I1R4 = 38
	I1R5 = 39
	I1R6 = 40
	I1R7 = 41
	I1R8 = 42
	M1 = 43
	M2 = 44
	M3 = 45
	M4 = 46
	M5 = 47
	M6 = 48
	M7 = 49
	M8 = 50
	PA1HPOWER2 = 51
	PA1QPOWER1 = 52
	PA2HPOWER2 = 53
	PA2QPOWER1 = 54
	PA3HPOWER2 = 55
	PA3QPOWER1 = 56
	PA4HPOWER2 = 57
	PA4QPOWER1 = 58
	PA5HPOWER2 = 59
	PA5QPOWER1 = 60
	PA6HPOWER2 = 61
	PA6QPOWER1 = 62
	PBUS1 = 63
	PBUS2 = 64
	PBUS3 = 65
	PBUS4 = 66
	R1 = 67
	R2 = 68
	R3 = 69
	R4 = 70
	R5 = 71
	R6 = 72
	R7 = 73
	R8 = 74
	SBUS1 = 75
	SBUS2 = 76
	SBUS3 = 77
	SBUS4 = 78
	SPECAVER1 = 79
	SPECAVER2 = 80
	SPECAVER3 = 81
	SPECAVER4 = 82
	SPECMAXH1 = 83
	SPECMAXH2 = 84
	SPECMAXH3 = 85
	SPECMAXH4 = 86
	SPECMINH1 = 87
	SPECMINH2 = 88
	SPECMINH3 = 89
	SPECMINH4 = 90
	SPECNORM1 = 91
	SPECNORM2 = 92
	SPECNORM3 = 93
	SPECNORM4 = 94
	TRK1 = 95
	TRK10 = 96
	TRK11 = 97
	TRK12 = 98
	TRK13 = 99
	TRK14 = 100
	TRK15 = 101
	TRK16 = 102
	TRK17 = 103
	TRK18 = 104
	TRK19 = 105
	TRK2 = 106
	TRK20 = 107
	TRK21 = 108
	TRK22 = 109
	TRK23 = 110
	TRK24 = 111
	TRK3 = 112
	TRK4 = 113
	TRK5 = 114
	TRK6 = 115
	TRK7 = 116
	TRK8 = 117
	TRK9 = 118
	XY1 = 119
	XY2 = 120
	XY3 = 121
	XY4 = 122


# noinspection SpellCheckingInspection
class ColorTable(Enum):
	"""4 Members, FalseColors ... Temperature"""
	FalseColors = "'FalseColors'"
	SingleEvent = "'SingleEvent'"
	Spectrum = "'Spectrum'"
	Temperature = "'Temperature'"


# noinspection SpellCheckingInspection
class Column(Enum):
	"""4 Members, COL1 ... NONE"""
	COL1 = 0
	COL2 = 1
	COL3 = 2
	NONE = 3


# noinspection SpellCheckingInspection
class ContentType(Enum):
	"""4 Members, DIAG ... RES"""
	DIAG = 0
	NODE = 1
	NONE = 2
	RES = 3


# noinspection SpellCheckingInspection
class Coupling(Enum):
	"""3 Members, AC ... DCLimit"""
	AC = 0
	DC = 1
	DCLimit = 2


# noinspection SpellCheckingInspection
class CouplingMode(Enum):
	"""4 Members, CURSor ... ZOOM"""
	CURSor = 0
	MANual = 1
	SPECtrum = 2
	ZOOM = 3


# noinspection SpellCheckingInspection
class CrcCalculation(Enum):
	"""2 Members, SAEJ ... TLE"""
	SAEJ = 0
	TLE = 1


# noinspection SpellCheckingInspection
class CrcVersion(Enum):
	"""2 Members, LEGA ... V2010"""
	LEGA = 0
	V2010 = 1


# noinspection SpellCheckingInspection
class Cursor(Enum):
	"""4 Members, CURSOR1 ... CURSOR4"""
	CURSOR1 = 0
	CURSOR2 = 1
	CURSOR3 = 2
	CURSOR4 = 3


# noinspection SpellCheckingInspection
class CursorStyle(Enum):
	"""4 Members, LINes ... VLRHombus"""
	LINes = 0
	LRHombus = 1
	RHOMbus = 2
	VLRHombus = 3


# noinspection SpellCheckingInspection
class CursorType(Enum):
	"""3 Members, HORizontal ... VERTical"""
	HORizontal = 0
	PAIRed = 1
	VERTical = 2


# noinspection SpellCheckingInspection
class DataAlignment(Enum):
	"""2 Members, BIT ... WORD"""
	BIT = 0
	WORD = 1


# noinspection SpellCheckingInspection
class DataFormat(Enum):
	"""3 Members, ASCii ... REAL"""
	ASCii = 0
	INT = 1
	REAL = 2


# noinspection SpellCheckingInspection
class Detection(Enum):
	"""2 Members, DETected ... NDETected"""
	DETected = 0
	NDETected = 1


# noinspection SpellCheckingInspection
class DiagramStyle(Enum):
	"""2 Members, DOTS ... VECTors"""
	DOTS = 0
	VECTors = 1


# noinspection SpellCheckingInspection
class DispedHarmonics(Enum):
	"""4 Members, ALL ... STANdard"""
	ALL = 0
	EVEN = 1
	ODD = 2
	STANdard = 3


# noinspection SpellCheckingInspection
class DisplayDiff(Enum):
	"""2 Members, DIFFerential ... SINGleended"""
	DIFFerential = 0
	SINGleended = 1


# noinspection SpellCheckingInspection
class DisplayStyle(Enum):
	"""2 Members, LINE ... MARKer"""
	LINE = 0
	MARKer = 1


# noinspection SpellCheckingInspection
class Edge(Enum):
	"""3 Members, BOTH ... RISE"""
	BOTH = 0
	FALL = 1
	RISE = 2


# noinspection SpellCheckingInspection
class EdgeCntDirct(Enum):
	"""2 Members, FRFI ... FRLA"""
	FRFI = 0
	FRLA = 1


# noinspection SpellCheckingInspection
class Endianness(Enum):
	"""2 Members, BENDian ... LENDian"""
	BENDian = 0
	LENDian = 1


# noinspection SpellCheckingInspection
class EnvelopeCurve(Enum):
	"""3 Members, BOTH ... MIN"""
	BOTH = 0
	MAX = 1
	MIN = 2


# noinspection SpellCheckingInspection
class EventsMode(Enum):
	"""2 Members, SEQuence ... SINGle"""
	SEQuence = 0
	SINGle = 1


# noinspection SpellCheckingInspection
class ExportScope(Enum):
	"""5 Members, ALL ... MANual"""
	ALL = 0
	CURSor = 1
	DISPlay = 2
	GATE = 3
	MANual = 4


# noinspection SpellCheckingInspection
class ExportSource(Enum):
	"""49 Members, C1 ... SPECNORM4"""
	C1 = 0
	C2 = 1
	C3 = 2
	C4 = 3
	C5 = 4
	C6 = 5
	C7 = 6
	C8 = 7
	D0 = 8
	D1 = 9
	D10 = 10
	D11 = 11
	D12 = 12
	D13 = 13
	D14 = 14
	D15 = 15
	D2 = 16
	D3 = 17
	D4 = 18
	D5 = 19
	D6 = 20
	D7 = 21
	D8 = 22
	D9 = 23
	M1 = 24
	M2 = 25
	M3 = 26
	M4 = 27
	M5 = 28
	R1 = 29
	R2 = 30
	R3 = 31
	R4 = 32
	SPECAVER1 = 33
	SPECAVER2 = 34
	SPECAVER3 = 35
	SPECAVER4 = 36
	SPECMAXH1 = 37
	SPECMAXH2 = 38
	SPECMAXH3 = 39
	SPECMAXH4 = 40
	SPECMINH1 = 41
	SPECMINH2 = 42
	SPECMINH3 = 43
	SPECMINH4 = 44
	SPECNORM1 = 45
	SPECNORM2 = 46
	SPECNORM3 = 47
	SPECNORM4 = 48


# noinspection SpellCheckingInspection
class FileExtension(Enum):
	"""19 Members, BIN ... ZIP"""
	BIN = 0
	CMD = 1
	CSV = 2
	DMO = 3
	EXE = 4
	GEN = 5
	H5 = 6
	JPG = 7
	PNG = 8
	PTT = 9
	PY = 10
	REF = 11
	RSI = 12
	S2P = 13
	S4P = 14
	SET = 15
	SVG = 16
	XML = 17
	ZIP = 18


# noinspection SpellCheckingInspection
class FilterDesignType(Enum):
	"""3 Members, BETHomson ... WALL"""
	BETHomson = 0
	GAUSsian = 1
	WALL = 2


# noinspection SpellCheckingInspection
class FormErrorCause(Enum):
	"""5 Members, ACKDerror ... RESerror"""
	ACKDerror = 0
	CRCDerror = 1
	FSBE = 2
	NONE = 3
	RESerror = 4


# noinspection SpellCheckingInspection
class FrameType(Enum):
	"""7 Members, BADX ... TCOD"""
	BADX = 0
	DATA = 1
	EEP = 2
	EOP = 3
	FCT = 4
	NULL = 5
	TCOD = 6


# noinspection SpellCheckingInspection
class FrAnalysisCalStates(Enum):
	"""4 Members, FAIL ... RUN"""
	FAIL = 0
	NOAL = 1
	PASS = 2
	RUN = 3


# noinspection SpellCheckingInspection
class FundamentalFreqEn61000(Enum):
	"""3 Members, AUTO ... F60"""
	AUTO = 0
	F50 = 1
	F60 = 2


# noinspection SpellCheckingInspection
class FundamentalFreqMil(Enum):
	"""2 Members, F400 ... F60"""
	F400 = 0
	F60 = 1


# noinspection SpellCheckingInspection
class FundamentalFreqRtca(Enum):
	"""3 Members, F400 ... WVF"""
	F400 = 0
	NVF = 1
	WVF = 2


# noinspection SpellCheckingInspection
class GeneratorChannel(Enum):
	"""2 Members, GEN1 ... GEN2"""
	GEN1 = 0
	GEN2 = 1


# noinspection SpellCheckingInspection
class GenSyncCombination(Enum):
	"""2 Members, GEN12 ... NONE"""
	GEN12 = 0
	NONE = 1


# noinspection SpellCheckingInspection
class HiLowMode(Enum):
	"""3 Members, EITHer ... LOW"""
	EITHer = 0
	HIGH = 1
	LOW = 2


# noinspection SpellCheckingInspection
class Hlx(Enum):
	"""3 Members, DONTcare ... LOW"""
	DONTcare = 0
	HIGH = 1
	LOW = 2


# noinspection SpellCheckingInspection
class HorizontalMode(Enum):
	"""2 Members, COUPled ... ORIGinal"""
	COUPled = 0
	ORIGinal = 1


# noinspection SpellCheckingInspection
class Hysteresis(Enum):
	"""3 Members, MAXimum ... ROBust"""
	MAXimum = 0
	NORMal = 1
	ROBust = 2


# noinspection SpellCheckingInspection
class InitialPhase(Enum):
	"""2 Members, DATaedge ... SAMPle"""
	DATaedge = 0
	SAMPle = 1


# noinspection SpellCheckingInspection
class InputSelection(Enum):
	"""3 Members, GHZ1 ... VARiable"""
	GHZ1 = 0
	MHZ640 = 1
	VARiable = 2


# noinspection SpellCheckingInspection
class Intersection(Enum):
	"""2 Members, MUST ... NOT"""
	MUST = 0
	NOT = 1


# noinspection SpellCheckingInspection
class IntpolMd(Enum):
	"""3 Members, LINear ... SMHD"""
	LINear = 0
	SINX = 1
	SMHD = 2


# noinspection SpellCheckingInspection
class LabelBorder(Enum):
	"""2 Members, FULL ... NOBorder"""
	FULL = 0
	NOBorder = 1


# noinspection SpellCheckingInspection
class LayoutSplitType(Enum):
	"""6 Members, BODE ... ZOOM"""
	BODE = 0
	HOR = 1
	NONE = 2
	SPEC = 3
	VERT = 4
	ZOOM = 5


# noinspection SpellCheckingInspection
class LowHigh(Enum):
	"""2 Members, HIGH ... LOW"""
	HIGH = 0
	LOW = 1


# noinspection SpellCheckingInspection
class MagnitudeUnit(Enum):
	"""7 Members, DB ... LINear"""
	DB = 0
	DBHZ = 1
	DBM = 2
	DBS = 3
	DBUV = 4
	DBV = 5
	LINear = 6


# noinspection SpellCheckingInspection
class MathSignalType(Enum):
	"""4 Members, CORR ... SOUR"""
	CORR = 0
	MEAS = 1
	NONE = 2
	SOUR = 3


# noinspection SpellCheckingInspection
class MeasDelayMode(Enum):
	"""2 Members, PERiod ... TIME"""
	PERiod = 0
	TIME = 1


# noinspection SpellCheckingInspection
class MeasRbw(Enum):
	"""3 Members, HIGH ... MID"""
	HIGH = 0
	LOW = 1
	MID = 2


# noinspection SpellCheckingInspection
class MeasType(Enum):
	"""42 Members, AMPLitude ... STDDev"""
	AMPLitude = 0
	AREA = 1
	BWIDth = 2
	CAMPlitude = 3
	CMAXimum = 4
	CMINimum = 5
	CPDelta = 6
	CRESt = 7
	CYCarea = 8
	CYCCrest = 9
	CYCMean = 10
	CYCRms = 11
	CYCStddev = 12
	DELay = 13
	DTOTrigger = 14
	EDGecount = 15
	FREQuency = 16
	FTIMe = 17
	HIGH = 18
	HOLD = 19
	LOW = 20
	MAXimum = 21
	MEAN = 22
	MINimum = 23
	NDCYcle = 24
	NOVershoot = 25
	NPULse = 26
	PDCYcle = 27
	PDELta = 28
	PERiod = 29
	PHASe = 30
	POVershoot = 31
	PPULse = 32
	PULCnt = 33
	RMS = 34
	RTIMe = 35
	SETup = 36
	SHR = 37
	SHT = 38
	SLEFalling = 39
	SLERising = 40
	STDDev = 41


# noinspection SpellCheckingInspection
class MeterBandwidth(Enum):
	"""8 Members, B100 ... B5M"""
	B100 = 0
	B10M = 1
	B1M = 2
	B200 = 3
	B20M = 4
	B2M = 5
	B500 = 6
	B5M = 7


# noinspection SpellCheckingInspection
class ModulationType(Enum):
	"""6 Members, AM ... PWM"""
	AM = 0
	ASK = 1
	FM = 2
	FSK = 3
	NONE = 4
	PWM = 5


# noinspection SpellCheckingInspection
class NormalInverted(Enum):
	"""2 Members, INVerted ... NORMal"""
	INVerted = 0
	NORMal = 1


# noinspection SpellCheckingInspection
class OnOffType(Enum):
	"""2 Members, TOFF ... TON"""
	TOFF = 0
	TON = 1


# noinspection SpellCheckingInspection
class OperatorA(Enum):
	"""8 Members, ANY ... NEQual"""
	ANY = 0
	EQUal = 1
	GETHan = 2
	GTHan = 3
	INRange = 4
	LETHan = 5
	LTHan = 6
	NEQual = 7


# noinspection SpellCheckingInspection
class OperatorB(Enum):
	"""9 Members, EQUal ... OORange"""
	EQUal = 0
	GETHan = 1
	GTHan = 2
	INRange = 3
	LETHan = 4
	LTHan = 5
	NEQual = 6
	OFF = 7
	OORange = 8


# noinspection SpellCheckingInspection
class PeriodSlope(Enum):
	"""4 Members, EITHer ... POSitive"""
	EITHer = 0
	FIRSt = 1
	NEGative = 2
	POSitive = 3


# noinspection SpellCheckingInspection
class PhaseMode(Enum):
	"""2 Members, DEGRees ... RADians"""
	DEGRees = 0
	RADians = 1


# noinspection SpellCheckingInspection
class PictureFileFormat(Enum):
	"""5 Members, BMP ... TIFF"""
	BMP = 0
	JPG = 1
	PDF = 2
	PNG = 3
	TIFF = 4


# noinspection SpellCheckingInspection
class PllOrder(Enum):
	"""2 Members, FIRSt ... SECond"""
	FIRSt = 0
	SECond = 1


# noinspection SpellCheckingInspection
class PointsMode(Enum):
	"""2 Members, DECade ... TOTal"""
	DECade = 0
	TOTal = 1


# noinspection SpellCheckingInspection
class PowerCoupling(Enum):
	"""2 Members, AC ... DC"""
	AC = 0
	DC = 1


# noinspection SpellCheckingInspection
class PowerType(Enum):
	"""5 Members, EFFiciency ... SWITching"""
	EFFiciency = 0
	HARMonics = 1
	ONOFf = 2
	QUALity = 3
	SWITching = 4


# noinspection SpellCheckingInspection
class PowerUnit(Enum):
	"""2 Members, ENERgy ... POWer"""
	ENERgy = 0
	POWer = 1


# noinspection SpellCheckingInspection
class PqualFundamentalFreq(Enum):
	"""5 Members, AUTO ... USER"""
	AUTO = 0
	F400 = 1
	F50 = 2
	F60 = 3
	USER = 4


# noinspection SpellCheckingInspection
class PrintTarget(Enum):
	"""3 Members, CLIPBOARD ... PRINTER"""
	CLIPBOARD = 0
	MMEM = 1
	PRINTER = 2


# noinspection SpellCheckingInspection
class ProbeAdapterType(Enum):
	"""2 Members, NONE ... Z2T"""
	NONE = 0
	Z2T = 1


# noinspection SpellCheckingInspection
class ProbeAttUnits(Enum):
	"""3 Members, A ... W"""
	A = 0
	V = 1
	W = 2


# noinspection SpellCheckingInspection
class ProbeMeasMode(Enum):
	"""4 Members, CMODe ... PMODe"""
	CMODe = 0
	DMODe = 1
	NMODe = 2
	PMODe = 3


# noinspection SpellCheckingInspection
class ProbeRange(Enum):
	"""3 Members, AUTO ... MLOW"""
	AUTO = 0
	MHIGh = 1
	MLOW = 2


# noinspection SpellCheckingInspection
class ProbeSetupMode(Enum):
	"""12 Members, AUToset ... SITFile"""
	AUToset = 0
	AZERo = 1
	FTRiglevel = 2
	NOACtion = 3
	OTMean = 4
	PRINt = 5
	PROBemode = 6
	PRSetup = 7
	RCONtinuous = 8
	REPort = 9
	RSINgle = 10
	SITFile = 11


# noinspection SpellCheckingInspection
class ProbeTipModel(Enum):
	"""8 Members, NONE ... Z302"""
	NONE = 0
	UNKNOWN = 1
	Z101 = 2
	Z201 = 3
	Z202 = 4
	Z203 = 5
	Z301 = 6
	Z302 = 7


# noinspection SpellCheckingInspection
class ProcessState(Enum):
	"""3 Members, OFF ... STOP"""
	OFF = 0
	RUN = 1
	STOP = 2


# noinspection SpellCheckingInspection
class ProtocolType(Enum):
	"""20 Members, ARIN429 ... UART"""
	ARIN429 = 0
	CAN = 1
	EBTB = 2
	HBTO = 3
	I2C = 4
	I3C = 5
	LIN = 6
	MANC = 7
	MILS1553 = 8
	NRZC = 9
	NRZU = 10
	QSPI = 11
	RFFE = 12
	SENT = 13
	SPI = 14
	SPMI = 15
	SWIR = 16
	TBTO = 17
	TNOS = 18
	UART = 19


# noinspection SpellCheckingInspection
class PulseSlope(Enum):
	"""3 Members, EITHer ... POSitive"""
	EITHer = 0
	NEGative = 1
	POSitive = 2


# noinspection SpellCheckingInspection
class PwrHarmonicsRevision(Enum):
	"""2 Members, REV2011 ... REV2019"""
	REV2011 = 0
	REV2019 = 1


# noinspection SpellCheckingInspection
class PwrHarmonicsStandard(Enum):
	"""6 Members, ENA ... RTCA"""
	ENA = 0
	ENB = 1
	ENC = 2
	END = 3
	MIL = 4
	RTCA = 5


# noinspection SpellCheckingInspection
class RangeMode(Enum):
	"""4 Members, LONGer ... WITHin"""
	LONGer = 0
	OUTSide = 1
	SHORter = 2
	WITHin = 3


# noinspection SpellCheckingInspection
class ReferenceLevel(Enum):
	"""3 Members, LOWer ... UPPer"""
	LOWer = 0
	MIDDle = 1
	UPPer = 2


# noinspection SpellCheckingInspection
class RelativeLevels(Enum):
	"""4 Members, FIVE ... USER"""
	FIVE = 0
	TEN = 1
	TWENty = 2
	USER = 3


# noinspection SpellCheckingInspection
class RelativePolarity(Enum):
	"""2 Members, INVerse ... MATChing"""
	INVerse = 0
	MATChing = 1


# noinspection SpellCheckingInspection
class Result(Enum):
	"""2 Members, FAIL ... PASS"""
	FAIL = 0
	PASS = 1


# noinspection SpellCheckingInspection
class ResultColumn(Enum):
	"""2 Members, FREQ ... VAL"""
	FREQ = 0
	VAL = 1


# noinspection SpellCheckingInspection
class ResultFileType(Enum):
	"""4 Members, CSV ... XML"""
	CSV = 0
	HTML = 1
	PY = 2
	XML = 3


# noinspection SpellCheckingInspection
class ResultOrder(Enum):
	"""2 Members, ASC ... DESC"""
	ASC = 0
	DESC = 1


# noinspection SpellCheckingInspection
class ResultState(Enum):
	"""3 Members, FAILed ... PASSed"""
	FAILed = 0
	NOALigndata = 1
	PASSed = 2


# noinspection SpellCheckingInspection
class SbusAckBit(Enum):
	"""3 Members, ACK ... NACK"""
	ACK = 0
	EITHer = 1
	NACK = 2


# noinspection SpellCheckingInspection
class SbusArincFrameState(Enum):
	"""6 Members, CODE ... UNKN"""
	CODE = 0
	GAP = 1
	INC = 2
	OK = 3
	PAR = 4
	UNKN = 5


# noinspection SpellCheckingInspection
class SbusArincPolarity(Enum):
	"""2 Members, ALEG ... BLEG"""
	ALEG = 0
	BLEG = 1


# noinspection SpellCheckingInspection
class SbusBitState(Enum):
	"""3 Members, DC ... ZERO"""
	DC = 0
	ONE = 1
	ZERO = 2


# noinspection SpellCheckingInspection
class SbusCanFrameOverallState(Enum):
	"""3 Members, ERRor ... UNDF"""
	ERRor = 0
	OK = 1
	UNDF = 2


# noinspection SpellCheckingInspection
class SbusCanFrameState(Enum):
	"""11 Members, ACKD ... UNKNown"""
	ACKD = 0
	BTST = 1
	CRC = 2
	CRCD = 3
	EOFD = 4
	FORM = 5
	INComplete = 6
	NOACk = 7
	OK = 8
	SERRror = 9
	UNKNown = 10


# noinspection SpellCheckingInspection
class SbusCanFrameType(Enum):
	"""10 Members, CBFF ... XLFF"""
	CBFF = 0
	CBFR = 1
	CEFF = 2
	CEFR = 3
	ERRor = 4
	FBFF = 5
	FEFF = 6
	OVERload = 7
	UNDefined = 8
	XLFF = 9


# noinspection SpellCheckingInspection
class SbusCanIdentifierType(Enum):
	"""2 Members, B11 ... B29"""
	B11 = 0
	B29 = 1


# noinspection SpellCheckingInspection
class SbusCanSignalType(Enum):
	"""2 Members, CANH ... CANL"""
	CANH = 0
	CANL = 1


# noinspection SpellCheckingInspection
class SbusCanTransceiverMode(Enum):
	"""2 Members, FAST ... SIC"""
	FAST = 0
	SIC = 1


# noinspection SpellCheckingInspection
class SbusCanTriggerType(Enum):
	"""7 Members, EDOF ... SYMB"""
	EDOF = 0
	ERRC = 1
	FTYP = 2
	ID = 3
	IDDT = 4
	STOF = 5
	SYMB = 6


# noinspection SpellCheckingInspection
class SbusDataFormat(Enum):
	"""10 Members, ASCII ... USIG"""
	ASCII = 0
	AUTO = 1
	BIN = 2
	DEC = 3
	HEX = 4
	OCT = 5
	SIGN = 6
	STRG = 7
	SYMB = 8
	USIG = 9


# noinspection SpellCheckingInspection
class SbusFrameCondition(Enum):
	"""2 Members, CLKTimeout ... CS"""
	CLKTimeout = 0
	CS = 1


# noinspection SpellCheckingInspection
class SbusHbtoFrameState(Enum):
	"""7 Members, ECRC ... UNCorrelated"""
	ECRC = 0
	ELENgth = 1
	EPRMble = 2
	ESFD = 3
	INComplete = 4
	OK = 5
	UNCorrelated = 6


# noinspection SpellCheckingInspection
class SbusHbtoFrameType(Enum):
	"""4 Members, FILLer ... UNKNown"""
	FILLer = 0
	IDLE = 1
	MAC = 2
	UNKNown = 3


# noinspection SpellCheckingInspection
class SbusHbtoMode(Enum):
	"""3 Members, AUTO ... SUB"""
	AUTO = 0
	MAIN = 1
	SUB = 2


# noinspection SpellCheckingInspection
class SBusI2cAddressType(Enum):
	"""5 Members, ANY ... BIT7RW"""
	ANY = 0
	AUTO = 1
	BIT10 = 2
	BIT7 = 3
	BIT7RW = 4


# noinspection SpellCheckingInspection
class SbusI2cFrameState(Enum):
	"""5 Members, ADDifferent ... UNKNown"""
	ADDifferent = 0
	INComplete = 1
	NOSTop = 2
	OK = 3
	UNKNown = 4


# noinspection SpellCheckingInspection
class SbusI2cTriggerType(Enum):
	"""7 Members, ADAT ... STOP"""
	ADAT = 0
	ADDRess = 1
	DATA = 2
	NACK = 3
	REPStart = 4
	STARt = 5
	STOP = 6


# noinspection SpellCheckingInspection
class SbusI3cFrameState(Enum):
	"""7 Members, ACK ... UNKNown"""
	ACK = 0
	CRC = 1
	INComplete = 2
	LENGth = 3
	OK = 4
	PAR = 5
	UNKNown = 6


# noinspection SpellCheckingInspection
class SbusI3cFrameType(Enum):
	"""8 Members, BRDC ... WRIT"""
	BRDC = 0
	DRCT = 1
	HDDR = 2
	HTSX = 3
	PROB = 4
	READ = 5
	UNKNown = 6
	WRIT = 7


# noinspection SpellCheckingInspection
class SbusIxcReadWriteBit(Enum):
	"""4 Members, EITHer ... WRITe"""
	EITHer = 0
	READ = 1
	UNDefined = 2
	WRITe = 3


# noinspection SpellCheckingInspection
class SbusLinFrameState(Enum):
	"""9 Members, CHCKsum ... WAKeup"""
	CHCKsum = 0
	INComplete = 1
	LNERror = 2
	OK = 3
	PRERror = 4
	STERror = 5
	SYERror = 6
	UNK = 7
	WAKeup = 8


# noinspection SpellCheckingInspection
class SBusLinStandard(Enum):
	"""4 Members, AUTO ... V2X"""
	AUTO = 0
	J2602 = 1
	V1X = 2
	V2X = 3


# noinspection SpellCheckingInspection
class SbusLinTriggerType(Enum):
	"""5 Members, ERRC ... WKFR"""
	ERRC = 0
	ID = 1
	IDDT = 2
	STARtframe = 3
	WKFR = 4


# noinspection SpellCheckingInspection
class SbusLinUartPolarity(Enum):
	"""2 Members, IDLHigh ... IDLLow"""
	IDLHigh = 0
	IDLLow = 1


# noinspection SpellCheckingInspection
class SbusMilstdFrameState(Enum):
	"""8 Members, GAP ... UNKNown"""
	GAP = 0
	INComplete = 1
	MANC = 2
	OK = 3
	PAR = 4
	RT = 5
	SYNC = 6
	UNKNown = 7


# noinspection SpellCheckingInspection
class SbusMilstdFrameType(Enum):
	"""6 Members, CMD ... UNKNown"""
	CMD = 0
	CMST = 1
	DATA = 2
	IM = 3
	STAT = 4
	UNKNown = 5


# noinspection SpellCheckingInspection
class SbusNrzcFrameState(Enum):
	"""5 Members, CRC ... PARity"""
	CRC = 0
	INComplete = 1
	LENGth = 2
	OK = 3
	PARity = 4


# noinspection SpellCheckingInspection
class SbusQspiFrameState(Enum):
	"""4 Members, INComplete ... OPCode"""
	INComplete = 0
	LENGth = 1
	OK = 2
	OPCode = 3


# noinspection SpellCheckingInspection
class SbusQspiInstruction(Enum):
	"""3 Members, DUAL ... SINGle"""
	DUAL = 0
	QUAD = 1
	SINGle = 2


# noinspection SpellCheckingInspection
class SbusQspiSclkPolarity(Enum):
	"""2 Members, FALLing ... RISing"""
	FALLing = 0
	RISing = 1


# noinspection SpellCheckingInspection
class SbusRffeReadMode(Enum):
	"""2 Members, SREAD ... STRD"""
	SREAD = 0
	STRD = 1


# noinspection SpellCheckingInspection
class SbusRffeSeqType(Enum):
	"""17 Members, ERRD ... UNKN"""
	ERRD = 0
	ERRL = 1
	ERRor = 2
	ERWL = 3
	ERWR = 4
	IRSUM = 5
	MCTR = 6
	MCTW = 7
	MOHO = 8
	MRD = 9
	MSKW = 10
	MWR = 11
	RRD = 12
	RWR = 13
	RZWR = 14
	UNDEF = 15
	UNKN = 16


# noinspection SpellCheckingInspection
class SbusRffeState(Enum):
	"""9 Members, BPERR ... VERSion"""
	BPERR = 0
	GAP = 1
	INComplete = 2
	LENGth = 3
	NORESPONSE = 4
	OK = 5
	PARity = 6
	SSC = 7
	VERSion = 8


# noinspection SpellCheckingInspection
class SbusSentFrameState(Enum):
	"""8 Members, CRC ... SYNC"""
	CRC = 0
	FORM = 1
	INComplete = 2
	LENGth = 3
	OK = 4
	PAUSe = 5
	PULSe = 6
	SYNC = 7


# noinspection SpellCheckingInspection
class SbusSentFrameType(Enum):
	"""6 Members, ELSM ... UNKNown"""
	ELSM = 0
	ESSM = 1
	PAUSe = 2
	SMSG = 3
	TRSQ = 4
	UNKNown = 5


# noinspection SpellCheckingInspection
class SbusSentIdentifierType(Enum):
	"""2 Members, B4 ... B8"""
	B4 = 0
	B8 = 1


# noinspection SpellCheckingInspection
class SbusSentMode(Enum):
	"""2 Members, LEGacy ... SPC"""
	LEGacy = 0
	SPC = 1


# noinspection SpellCheckingInspection
class SbusSentPausePulse(Enum):
	"""3 Members, NPP ... PPFL"""
	NPP = 0
	PP = 1
	PPFL = 2


# noinspection SpellCheckingInspection
class SbusSentResultDisplay(Enum):
	"""3 Members, ALL ... TRSQ"""
	ALL = 0
	SMSG = 1
	TRSQ = 2


# noinspection SpellCheckingInspection
class SbusSentSerialMessages(Enum):
	"""2 Members, DISabled ... ENABled"""
	DISabled = 0
	ENABled = 1


# noinspection SpellCheckingInspection
class SbusSpiCsPolarity(Enum):
	"""2 Members, ACTHigh ... ACTLow"""
	ACTHigh = 0
	ACTLow = 1


# noinspection SpellCheckingInspection
class SbusSpiFrameState(Enum):
	"""4 Members, INComplete ... VOID"""
	INComplete = 0
	LENGth = 1
	OK = 2
	VOID = 3


# noinspection SpellCheckingInspection
class SbusSpiTriggerType(Enum):
	"""4 Members, FRENd ... MOSI"""
	FRENd = 0
	FRSTart = 1
	MISO = 2
	MOSI = 3


# noinspection SpellCheckingInspection
class SbusSpmiFrameState(Enum):
	"""11 Members, ACKerror ... SSCerror"""
	ACKerror = 0
	ARBerror = 1
	BPERror = 2
	CMDerror = 3
	CODerror = 4
	INComplete = 5
	LENerror = 6
	NOReponse = 7
	OK = 8
	PARerror = 9
	SSCerror = 10


# noinspection SpellCheckingInspection
class SbusSpmiFrameType(Enum):
	"""20 Members, ARB ... WAK"""
	ARB = 0
	AUTH = 1
	BMRD = 2
	BSRD = 3
	ERRD = 4
	ERRL = 5
	ERWL = 6
	ERWR = 7
	INV = 8
	MARD = 9
	MAWR = 10
	REST = 11
	RRD = 12
	RWR = 13
	RZWR = 14
	SHUT = 15
	SLEP = 16
	TBOW = 17
	UNKN = 18
	WAK = 19


# noinspection SpellCheckingInspection
class SbusSwireFrameState(Enum):
	"""5 Members, AMBiguous ... PARity"""
	AMBiguous = 0
	INComplete = 1
	LENGth = 2
	OK = 3
	PARity = 4


# noinspection SpellCheckingInspection
class SbusTnosFrameState(Enum):
	"""7 Members, ECRC ... OK"""
	ECRC = 0
	EESD = 1
	ELEN = 2
	EPRMble = 3
	ESFD = 4
	INComplete = 5
	OK = 6


# noinspection SpellCheckingInspection
class SbusTnosFrameType(Enum):
	"""4 Members, BEACon ... UNKN"""
	BEACon = 0
	COMMit = 1
	MAC = 2
	UNKN = 3


# noinspection SpellCheckingInspection
class SbusUartFrameSeparation(Enum):
	"""2 Members, NONE ... TOUT"""
	NONE = 0
	TOUT = 1


# noinspection SpellCheckingInspection
class SbusUartParity(Enum):
	"""6 Members, DC ... SPC"""
	DC = 0
	EVEN = 1
	MARK = 2
	NONE = 3
	ODD = 4
	SPC = 5


# noinspection SpellCheckingInspection
class SbusUartTriggerType(Enum):
	"""6 Members, BRKC ... STPerror"""
	BRKC = 0
	DATA = 1
	PCKS = 2
	PRER = 3
	STBT = 4
	STPerror = 5


# noinspection SpellCheckingInspection
class SbusUartWordState(Enum):
	"""6 Members, BREak ... STERror"""
	BREak = 0
	INComplete = 1
	OK = 2
	PRERror = 3
	SPERror = 4
	STERror = 5


# noinspection SpellCheckingInspection
class SelectProbe(Enum):
	"""23 Members, NONE ... ZZ80"""
	NONE = 0
	USER = 1
	ZC02100 = 2
	ZC021000 = 3
	ZC03 = 4
	ZC10 = 5
	ZC20 = 6
	ZC30 = 7
	ZC3101 = 8
	ZC311 = 9
	ZC3110 = 10
	ZD002A10 = 11
	ZD002A100 = 12
	ZD003A20 = 13
	ZD003A200 = 14
	ZD01A100 = 15
	ZD01A1000 = 16
	ZD02 = 17
	ZD08 = 18
	ZH03 = 19
	ZP1X = 20
	ZS10L = 21
	ZZ80 = 22


# noinspection SpellCheckingInspection
class SelResults(Enum):
	"""2 Members, AISYnc ... ALL"""
	AISYnc = 0
	ALL = 1


# noinspection SpellCheckingInspection
class SignalSource(Enum):
	"""33 Members, C1 ... NONE"""
	C1 = 0
	C2 = 1
	C3 = 2
	C4 = 3
	C5 = 4
	C6 = 5
	C7 = 6
	C8 = 7
	D0 = 8
	D1 = 9
	D10 = 10
	D11 = 11
	D12 = 12
	D13 = 13
	D14 = 14
	D15 = 15
	D2 = 16
	D3 = 17
	D4 = 18
	D5 = 19
	D6 = 20
	D7 = 21
	D8 = 22
	D9 = 23
	M1 = 24
	M2 = 25
	M3 = 26
	M4 = 27
	M5 = 28
	M6 = 29
	M7 = 30
	M8 = 31
	NONE = 32


# noinspection SpellCheckingInspection
class SlopeType(Enum):
	"""2 Members, NEGative ... POSitive"""
	NEGative = 0
	POSitive = 1


# noinspection SpellCheckingInspection
class Source(Enum):
	"""184 Members, C1 ... XY4"""
	C1 = 0
	C2 = 1
	C3 = 2
	C4 = 3
	C5 = 4
	C6 = 5
	C7 = 6
	C8 = 7
	D0 = 8
	D1 = 9
	D10 = 10
	D11 = 11
	D12 = 12
	D13 = 13
	D14 = 14
	D15 = 15
	D2 = 16
	D3 = 17
	D4 = 18
	D5 = 19
	D6 = 20
	D7 = 21
	D8 = 22
	D9 = 23
	DREF0 = 24
	DREF1 = 25
	DREF10 = 26
	DREF11 = 27
	DREF12 = 28
	DREF13 = 29
	DREF14 = 30
	DREF15 = 31
	DREF2 = 32
	DREF3 = 33
	DREF4 = 34
	DREF5 = 35
	DREF6 = 36
	DREF7 = 37
	DREF8 = 38
	DREF9 = 39
	FAMPlitude = 40
	FGAin = 41
	FPHase = 42
	HISTogram1 = 43
	HISTogram2 = 44
	HISTogram3 = 45
	HISTogram4 = 46
	HISTogram5 = 47
	HISTogram6 = 48
	HISTogram7 = 49
	HISTogram8 = 50
	M1 = 51
	M2 = 52
	M3 = 53
	M4 = 54
	M5 = 55
	M6 = 56
	M7 = 57
	M8 = 58
	NONE = 59
	O2C1 = 60
	O2C2 = 61
	O2C3 = 62
	O2C4 = 63
	O2C5 = 64
	O2C6 = 65
	O2C7 = 66
	O2C8 = 67
	O2R1 = 68
	O2R2 = 69
	O2R3 = 70
	O2R4 = 71
	O2R5 = 72
	O2R6 = 73
	O2R7 = 74
	O2R8 = 75
	PA1HPOWER1 = 76
	PA1IPOWER = 77
	PA1OPOWER1 = 78
	PA1OPOWER2 = 79
	PA1OPOWER3 = 80
	PA1QPOWER1 = 81
	PA1SPOWER1 = 82
	PA1TOPOWER = 83
	PA2HPOWER1 = 84
	PA2IPOWER = 85
	PA2OPOWER1 = 86
	PA2OPOWER2 = 87
	PA2OPOWER3 = 88
	PA2QPOWER1 = 89
	PA2SPOWER1 = 90
	PA2TOPOWER = 91
	PA3HPOWER1 = 92
	PA3IPOWER = 93
	PA3OPOWER1 = 94
	PA3OPOWER2 = 95
	PA3OPOWER3 = 96
	PA3QPOWER1 = 97
	PA3SPOWER1 = 98
	PA3TOPOWER = 99
	PA4HPOWER1 = 100
	PA4IPOWER = 101
	PA4OPOWER1 = 102
	PA4OPOWER2 = 103
	PA4OPOWER3 = 104
	PA4QPOWER1 = 105
	PA4SPOWER1 = 106
	PA4TOPOWER = 107
	PA5HPOWER1 = 108
	PA5IPOWER = 109
	PA5OPOWER1 = 110
	PA5OPOWER2 = 111
	PA5OPOWER3 = 112
	PA5QPOWER1 = 113
	PA5SPOWER1 = 114
	PA5TOPOWER = 115
	PA6HPOWER1 = 116
	PA6IPOWER = 117
	PA6OPOWER1 = 118
	PA6OPOWER2 = 119
	PA6OPOWER3 = 120
	PA6QPOWER1 = 121
	PA6SPOWER1 = 122
	PA6TOPOWER = 123
	PBUS1 = 124
	PBUS2 = 125
	PBUS3 = 126
	PBUS4 = 127
	R1 = 128
	R2 = 129
	R3 = 130
	R4 = 131
	R5 = 132
	R6 = 133
	R7 = 134
	R8 = 135
	SBUS1 = 136
	SBUS2 = 137
	SBUS3 = 138
	SBUS4 = 139
	SPECAVER1 = 140
	SPECAVER2 = 141
	SPECAVER3 = 142
	SPECAVER4 = 143
	SPECMAXH1 = 144
	SPECMAXH2 = 145
	SPECMAXH3 = 146
	SPECMAXH4 = 147
	SPECMINH1 = 148
	SPECMINH2 = 149
	SPECMINH3 = 150
	SPECMINH4 = 151
	SPECNORM1 = 152
	SPECNORM2 = 153
	SPECNORM3 = 154
	SPECNORM4 = 155
	TRK1 = 156
	TRK10 = 157
	TRK11 = 158
	TRK12 = 159
	TRK13 = 160
	TRK14 = 161
	TRK15 = 162
	TRK16 = 163
	TRK17 = 164
	TRK18 = 165
	TRK19 = 166
	TRK2 = 167
	TRK20 = 168
	TRK21 = 169
	TRK22 = 170
	TRK23 = 171
	TRK24 = 172
	TRK3 = 173
	TRK4 = 174
	TRK5 = 175
	TRK6 = 176
	TRK7 = 177
	TRK8 = 178
	TRK9 = 179
	XY1 = 180
	XY2 = 181
	XY3 = 182
	XY4 = 183


# noinspection SpellCheckingInspection
class SourceDetailed(Enum):
	"""47 Members, C1 ... Z2V4"""
	C1 = 0
	C2 = 1
	C3 = 2
	C4 = 3
	C5 = 4
	C6 = 5
	C7 = 6
	C8 = 7
	D0 = 8
	D1 = 9
	D10 = 10
	D11 = 11
	D12 = 12
	D13 = 13
	D14 = 14
	D15 = 15
	D2 = 16
	D3 = 17
	D4 = 18
	D5 = 19
	D6 = 20
	D7 = 21
	D8 = 22
	D9 = 23
	EXTernanalog = 24
	GENerator = 25
	LINE = 26
	SBUS1 = 27
	SBUS2 = 28
	SBUS3 = 29
	SBUS4 = 30
	Z1I1 = 31
	Z1I2 = 32
	Z1I3 = 33
	Z1I4 = 34
	Z1V1 = 35
	Z1V2 = 36
	Z1V3 = 37
	Z1V4 = 38
	Z2I1 = 39
	Z2I2 = 40
	Z2I3 = 41
	Z2I4 = 42
	Z2V1 = 43
	Z2V2 = 44
	Z2V3 = 45
	Z2V4 = 46


# noinspection SpellCheckingInspection
class SourceInt(Enum):
	"""2 Members, EXTernal ... INTernal"""
	EXTernal = 0
	INTernal = 1


# noinspection SpellCheckingInspection
class StopBits(Enum):
	"""3 Members, B1 ... B2"""
	B1 = 0
	B15 = 1
	B2 = 2


# noinspection SpellCheckingInspection
class Technology(Enum):
	"""11 Members, CUSTom ... VM13"""
	CUSTom = 0
	MANual = 1
	V0 = 2
	V09 = 3
	V125 = 4
	V15 = 5
	V165 = 6
	V20 = 7
	V25 = 8
	V38 = 9
	VM13 = 10


# noinspection SpellCheckingInspection
class TekPredefProbe(Enum):
	"""25 Members, NONE ... TCP202"""
	NONE = 0
	P5205A50 = 1
	P5205A500 = 2
	P5210A100 = 3
	P5210A1000 = 4
	P6205 = 5
	P6241 = 6
	P6243 = 7
	P6245 = 8
	P6246A1 = 9
	P6246A10 = 10
	P6247A1 = 11
	P6247A10 = 12
	P6248A1 = 13
	P6248A10 = 14
	P6249 = 15
	P6250A5 = 16
	P6250A50 = 17
	P6251A5 = 18
	P6251A50 = 19
	P6701B = 20
	P6703B = 21
	P6711 = 22
	P6713 = 23
	TCP202 = 24


# noinspection SpellCheckingInspection
class TimebaseRollMode(Enum):
	"""2 Members, AUTO ... OFF"""
	AUTO = 0
	OFF = 1


# noinspection SpellCheckingInspection
class TreferenceType(Enum):
	"""4 Members, CLOCk ... SCDR"""
	CLOCk = 0
	HCDR = 1
	RCDR = 2
	SCDR = 3


# noinspection SpellCheckingInspection
class TrigFilterMode(Enum):
	"""3 Members, LFReject ... RFReject"""
	LFReject = 0
	OFF = 1
	RFReject = 2


# noinspection SpellCheckingInspection
class TriggerAction(Enum):
	"""4 Members, NOACtion ... VIOLation"""
	NOACtion = 0
	SUCCess = 1
	TRIGger = 2
	VIOLation = 3


# noinspection SpellCheckingInspection
class TriggerEventType(Enum):
	"""18 Members, ANEDge ... WINDow"""
	ANEDge = 0
	ANTV = 1
	CDR = 2
	EDGE = 3
	GLITch = 4
	INTerval = 5
	IQMagnitude = 6
	NFC = 7
	PATTern = 8
	RUNT = 9
	SERPattern = 10
	SETHold = 11
	SLEWrate = 12
	STATe = 13
	TIMeout = 14
	TV = 15
	WIDTh = 16
	WINDow = 17


# noinspection SpellCheckingInspection
class TriggerGlitchMode(Enum):
	"""2 Members, LONGer ... SHORter"""
	LONGer = 0
	SHORter = 1


# noinspection SpellCheckingInspection
class TriggerHoldoffMode(Enum):
	"""5 Members, AUTO ... TIME"""
	AUTO = 0
	EVENts = 1
	OFF = 2
	RANDom = 3
	TIME = 4


# noinspection SpellCheckingInspection
class TriggerMode(Enum):
	"""3 Members, AUTO ... NORMal"""
	AUTO = 0
	FREerun = 1
	NORMal = 2


# noinspection SpellCheckingInspection
class TriggerMultiEventsType(Enum):
	"""9 Members, AB ... AZ"""
	AB = 0
	ABR = 1
	ABRZ = 2
	ABZ = 3
	AONLy = 4
	AORB = 5
	AORBZ = 6
	ASB = 7
	AZ = 8


# noinspection SpellCheckingInspection
class TriggerOutSource(Enum):
	"""3 Members, POST ... WAIT"""
	POST = 0
	TRIG = 1
	WAIT = 2


# noinspection SpellCheckingInspection
class TriggerPatternMode(Enum):
	"""3 Members, OFF ... WIDTh"""
	OFF = 0
	TIMeout = 1
	WIDTh = 2


# noinspection SpellCheckingInspection
class TriggerPatternSource(Enum):
	"""3 Members, AAD ... DIGital"""
	AAD = 0
	ANALog = 1
	DIGital = 2


# noinspection SpellCheckingInspection
class TriggerRuntRangeMode(Enum):
	"""5 Members, ANY ... WITHin"""
	ANY = 0
	LONGer = 1
	OUTSide = 2
	SHORter = 3
	WITHin = 4


# noinspection SpellCheckingInspection
class TriggerSlewRangeMode(Enum):
	"""4 Members, GTHan ... OUTRange"""
	GTHan = 0
	INSRange = 1
	LTHan = 2
	OUTRange = 3


# noinspection SpellCheckingInspection
class TriggerWinRangeMode(Enum):
	"""4 Members, ENTer ... WITHin"""
	ENTer = 0
	EXIT = 1
	OUTSide = 2
	WITHin = 3


# noinspection SpellCheckingInspection
class TxRx(Enum):
	"""2 Members, RX ... TX"""
	RX = 0
	TX = 1


# noinspection SpellCheckingInspection
class TypePy(Enum):
	"""4 Members, BLEFt ... TRIGht"""
	BLEFt = 0
	BRIGht = 1
	TLEFt = 2
	TRIGht = 3


# noinspection SpellCheckingInspection
class Unit(Enum):
	"""115 Members, A ... WS"""
	A = 0
	A_DIV = 1
	A_S = 2
	A_SQRT_HZ = 3
	A_V = 4
	AS = 5
	BAUD = 6
	BER = 7
	BIT = 8
	BIT_S = 9
	BYTS = 10
	C = 11
	DB = 12
	DB_DIV = 13
	DB_GHZ = 14
	DB_HZ = 15
	DBA = 16
	DBA_DIV = 17
	DBA_HZ = 18
	DBC = 19
	DBC_HZ = 20
	DBHZ = 21
	DBM = 22
	DBM_DIV = 23
	DBM_HZ = 24
	DBMA = 25
	DBMV = 26
	DBMV_HZ = 27
	DBMV_M_HZ = 28
	DBMV_MHZ = 29
	DBMW = 30
	DBPT = 31
	DBPT_HZ = 32
	DBPW = 33
	DBPW_HZ = 34
	DBS = 35
	DBUA = 36
	DBUA_HZ = 37
	DBUA_M = 38
	DBUA_M_HZ = 39
	DBUA_M_MHZ = 40
	DBUA_MHZ = 41
	DBUA_SQRT_HZ = 42
	DBUV = 43
	DBUV_DIV = 44
	DBUV_HZ = 45
	DBUV_M = 46
	DBUV_M_MHZ = 47
	DBUV_MHZ = 48
	DBUV_SQRT_HZ = 49
	DBV = 50
	DBV_DIV = 51
	DBV_HZ = 52
	DBW = 53
	DEG = 54
	DEG_DIV = 55
	DIV = 56
	F = 57
	FF_GHZ = 58
	H = 59
	HZ = 60
	HZ_DIV = 61
	HZ_S = 62
	IRE = 63
	J = 64
	K = 65
	M = 66
	MBIT_S = 67
	MSYMB_S = 68
	MV = 69
	MW = 70
	NONE = 71
	OHM = 72
	PCT = 73
	PER_DIV = 74
	PER_SEC = 75
	PH_GHZ = 76
	PPM = 77
	PX = 78
	RAD = 79
	S = 80
	S_DIV = 81
	S_S = 82
	SIEMENS = 83
	SYMB = 84
	SYMB_S = 85
	UA_HZ = 86
	UA_M_HZ = 87
	UI = 88
	USER = 89
	UV = 90
	UV_HZ = 91
	UV_M_HZ = 92
	V = 93
	V_A = 94
	V_DIV = 95
	V_S = 96
	V_SQRT_HZ = 97
	V_V = 98
	V_W = 99
	VA = 100
	VA_LIN = 101
	VA_LOG = 102
	VAR = 103
	VPP = 104
	VPP_DIV = 105
	VS = 106
	VV = 107
	W = 108
	W_DIV = 109
	W_HZ = 110
	W_S = 111
	W_V = 112
	WORD = 113
	WS = 114


# noinspection SpellCheckingInspection
class UserActivityTout(Enum):
	"""15 Members, OFF ... T5Minutes"""
	OFF = 0
	T10Minutes = 1
	T15Minutes = 2
	T1Hour = 3
	T1Minute = 4
	T20Minutes = 5
	T25Minutes = 6
	T2Hours = 7
	T2Minutes = 8
	T30Minutes = 9
	T3Hours = 10
	T3Minutes = 11
	T45Minutes = 12
	T4Hours = 13
	T5Minutes = 14


# noinspection SpellCheckingInspection
class UserLevel(Enum):
	"""2 Members, UREF ... USIGnal"""
	UREF = 0
	USIGnal = 1


# noinspection SpellCheckingInspection
class VerticalMode(Enum):
	"""2 Members, COUPled ... INDependent"""
	COUPled = 0
	INDependent = 1


# noinspection SpellCheckingInspection
class WgenFunctionType(Enum):
	"""14 Members, ARBitrary ... SQUare"""
	ARBitrary = 0
	CARDiac = 1
	DC = 2
	EXPFall = 3
	EXPRise = 4
	GAUSs = 5
	HAVer = 6
	LORNtz = 7
	PULSe = 8
	PWM = 9
	RAMP = 10
	SINC = 11
	SINusoid = 12
	SQUare = 13


# noinspection SpellCheckingInspection
class WgenLoad(Enum):
	"""2 Members, FIFTy ... HIZ"""
	FIFTy = 0
	HIZ = 1


# noinspection SpellCheckingInspection
class WgenOperationMode(Enum):
	"""4 Members, ARBGenerator ... SWEep"""
	ARBGenerator = 0
	FUNCgen = 1
	MODulation = 2
	SWEep = 3


# noinspection SpellCheckingInspection
class WgenRunMode(Enum):
	"""2 Members, REPetitive ... SINGle"""
	REPetitive = 0
	SINGle = 1


# noinspection SpellCheckingInspection
class WgenSignalType(Enum):
	"""4 Members, RAMP ... SQUare"""
	RAMP = 0
	SAWTooth = 1
	SINusoid = 2
	SQUare = 3


# noinspection SpellCheckingInspection
class WgenWaveformSource(Enum):
	"""3 Members, ARBitrary ... SCOPe"""
	ARBitrary = 0
	ERINjection = 1
	SCOPe = 2


# noinspection SpellCheckingInspection
class WindowFunction(Enum):
	"""7 Members, BLACkharris ... RECTangular"""
	BLACkharris = 0
	FLATTOP2 = 1
	GAUSsian = 2
	HAMMing = 3
	HANN = 4
	KAISerbessel = 5
	RECTangular = 6


# noinspection SpellCheckingInspection
class WindowPosition(Enum):
	"""6 Members, BOTT ... TOP"""
	BOTT = 0
	FREE = 1
	LEFT = 2
	NONE = 3
	RIGH = 4
	TOP = 5
