import maialib.maiacore as mc
import pandas as pd
import plotly

def plotPartsActivity(score: mc.Score, **kwargs) -> tuple[plotly.graph_objs._figure.Figure, pd.DataFrame]:
    '''Plots a timeline graph showing the musical activity of each score instrument

    Args:
       score (maialib.Score):  A maialib Score object loaded with a valid MusicXML file

    Kwargs:
       measureStart (int): Start measure to plot
       measureEnd (int): End measure to plot
       partNames (list): A str list that contains the filtered desired score parts to plot

    Returns:
       A list: [Plotly Figure, The plot data as a Pandas Dataframe]

    Raises:
       RuntimeError, KeyError

    Examples of use:

    >>> plotPartsActivity(myScore)
    >>> plotPartsActivity(myScore, measureStart=50)
    >>> plotPartsActivity(myScore, measureStart=50, measureEnd=100)
    >>> plotPartsActivity(myScore, measureStart=50, measureEnd=100, partNames=["Violin 1", "Cello"])
    '''
def plotPianoRoll(score: mc.Score, **kwargs) -> tuple[plotly.graph_objs._figure.Figure, pd.DataFrame]:
    '''Plots a piano roll graph showing the musical activity of each score instrument

    Args:
       score (maialib.Score):  A maialib Score object loaded with a valid MusicXML file

    Kwargs:
       measureStart (int): Start measure to plot
       measureEnd (int): End measure to plot
       partNames (list): A str list that contains the filtered desired score parts to plot

    Returns:
       A list: [Plotly Figure, The plot data as a Pandas Dataframe]

    Raises:
       RuntimeError, KeyError

    Examples of use:

    >>> plotPianoRoll(myScore)
    >>> plotPianoRoll(myScore, measureStart=50)
    >>> plotPianoRoll(myScore, measureStart=50, measureEnd=100)
    >>> plotPianoRoll(myScore, measureStart=50, measureEnd=100, partNames=["Violin 1", "Cello"])
    '''
def plotScorePitchEnvelope(score: mc.Score, **kwargs) -> tuple[plotly.graph_objs._figure.Figure, pd.DataFrame]:
    '''Plot a score pitch envelope

    Args:
       score (maialib.Score):  A maialib Score object loaded with a valid MusicXML file

    Kwargs:
       numPoints: (int): Number of interpolated points
       showHigher (bool): Plot the envelop upper limit
       showLower (bool): Plot the envelop lower limit
       showMean (bool): Plot the envelop mean curve
       showMeanOfExtremes (bool): Plot the envelop mean of extremes curve

    Returns:
       A list: [Plotly Figure, The plot data as a Pandas Dataframe]

    Raises:
       RuntimeError, KeyError

    Examples of use:

    >>> myScore = ml.Score("/path/to/score.xml")
    >>> plotScorePitchEnvelope(myScore)
    >>> plotScorePitchEnvelope(myScore, numPoints=10)
    >>> plotScorePitchEnvelope(myScore, showLower=False)
    >>> plotScorePitchEnvelope(myScore, showMean=False, showMean=True)
    '''
def plotChordsNumberOfNotes(score: mc.Score, **kwargs) -> tuple[plotly.graph_objs._figure.Figure, pd.DataFrame]:
    '''Plot chord number of notes varying in time

    Args:
       score (maialib.Score):  A maialib Score object loaded with a valid MusicXML file

    Kwargs:
       measureStart (int): Start measure to plot
       measureEnd (int): End measure to plot
       numPoints (int): Number of interpolated points

    Returns:
       A list: [Plotly Figure, The plot data as a Pandas Dataframe]

    Raises:
       RuntimeError, KeyError

    Examples of use:

    >>> myScore = ml.Score("/path/to/score.xml")
    >>> plotChordsNumberOfNotes(myScore)
    >>> plotChordsNumberOfNotes(myScore, numPoints=15)
    >>> plotChordsNumberOfNotes(myScore, measureStart=10, measureEnd=20)
    '''
