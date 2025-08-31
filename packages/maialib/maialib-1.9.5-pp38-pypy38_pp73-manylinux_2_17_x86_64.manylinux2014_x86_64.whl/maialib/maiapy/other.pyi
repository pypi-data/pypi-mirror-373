import maialib.maiacore as mc
from enum import Enum

def setScoreEditorApp(executableFullPath: str) -> None:
    '''Set the full path to the installed score editor app

    Args:
       executableFullPath (str): Score editor full path
       Example 01: "C:/path/to/MuseScore"
       Example 02: "/Applications/MuseScore 4.app/Contents/MacOS/mscore"

    Examples of use:

    >>> import maialib as ml
    >>> # Example for Windows:
    >>> ml.setScoreEditorApp("C:/path/to/MuseScore.exe")
    >>> # Example for Mac OSX:
    >>> ml.setScoreEditorApp("/Applications/MuseScore 4.app/Contents/MacOS/mscore")
    '''
def getScoreEditorApp() -> str: ...
def openScore(score: mc.Score) -> None: ...

class SampleScore(Enum):
    Bach_Cello_Suite_1: str
    Beethoven_Symphony_5th: str
    Chopin_Fantasie_Impromptu: str
    Dvorak_Symphony_9_mov_4: str
    Mahler_Symphony_8_Finale: str
    Mozart_Requiem_Introitus: str
    Strauss_Also_Sprach_Zarathustra: str

def getSampleScorePath(sampleEnum: SampleScore) -> str:
    """Get a maialib internal XML sample file

    Args:
       sampleEnum (SampleScore): Maialib SampleScore enum value
           - Bach_Cello_Suite_1
           - Beethoven_Symphony_5th
           - Chopin_Fantasie_Impromptu
           - Dvorak_Symphony_9_mov_4
           - Mahler_Symphony_8_Finale
           - Mozart_Requiem_Introitus
           - Strauss_Also_Sprach_Zarathustra

    Kwargs:
       None

    Returns:
       A full file path (str) to the XML maialib internal sample score

    Raises:
       RuntimeError

    Examples of use:

    >>> import maialib as ml
    >>> filePath = ml.getSampleScorePath(ml.SampleScore.Bach_Cello_Suite_1)
    >>> score = ml.Score(filePath)
    >>> score.info()
    """
def getXmlSamplesDirPath() -> str:
    '''Get the maialib XML samples directory path

    Kwargs:
       None

    Returns:
       A full dir path (str) to the XML maialib internal samples score directory

    Raises:
       RuntimeError

    Examples of use:

    >>> import maialib as ml
    >>> xmlDir = ml.getXmlSamplesDirPath()
    >>> score = ml.Score(xmlDir + "Bach/cello_suite_1_violin.xml")
    >>> score.info()
    '''
