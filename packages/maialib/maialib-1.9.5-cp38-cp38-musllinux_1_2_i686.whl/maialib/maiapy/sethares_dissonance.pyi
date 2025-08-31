import pandas as pd
import plotly
import plotly.graph_objects as go
from maialib import maiacore as mc
from typing import Callable

def plotSetharesDissonanceCurve(fundamentalFreq: float = 440, numPartials: int = 6, ratioLowLimit: float = 1.0, ratioHighLimit: float = 2.3, ratioStepIncrement: float = 0.001, amplCallback: Callable[[list[float]], list[float]] | None = None, partialsDecayExpRate: float = 0.88) -> tuple[go.Figure, pd.DataFrame]:
    """
    Generate and return the sensory dissonance curve (Sethares) for a harmonic spectrum.

    Parameters
    ----------
    fundamentalFreq : float, default=440
        Base frequency (f₀) in Hz on which the partials are built.

    numPartials : int, default=6
        Number of harmonics (partials) to include.

    ratioLowLimit : float, default=1.0
        Lower bound of the frequency ratio axis (intervals).

    ratioHighLimit : float, default=2.3
        Upper bound of the frequency ratio axis.

    ratioStepIncrement : float, default=0.001
        Step size between successive frequency ratios in the dissonance curve.

    amplCallback : Optional[Callable[[List[float]], List[float]]], default=None
        Optional function that receives a list of partial frequencies and returns
        corresponding amplitudes. If None, amplitudes decay exponentially by
        `partialsDecayExpRate`.

    partialsDecayExpRate : float, default=0.88
        Exponential decay rate for harmonics when `amplCallback` is None:
        amplitude_i = (partialsDecayExpRate)**i.

    Returns
    -------
    fig : go.Figure
        Plotly figure of the sensory dissonance curve with a log-scaled frequency ratio
        axis. Includes vertical lines for musically notable intervals (e.g., 3/2, 5/4).

    df : pandas.DataFrame
        DataFrame with columns:
            - 'ratio': frequency ratio values
            - 'dissonance': sensory dissonance computed for each ratio
            - 'freqs': frequency pair vectors used for calculation
            - 'amps': amplitude pair vectors used in calculation

    Behavior
    --------
    1. Constructs frequency vector `freqs` with integer multiples of `fundamentalFreq`.
    2. Computes amplitude vector `amps` via `amplCallback`, or using exponential decay.
    3. Validates matching lengths for `freqs` and `amps`, raising ValueError if mismatched.
    4. Constructs a `ratios` array from `ratioLowLimit` to `ratioHighLimit`.
    5. For each ratio r:
       - Concatenates `freqs` with r × `freqs`; likewise for amplitudes.
       - Applies `_dissmeasure` to compute sensory dissonance, frequency pairs, and amplitude pairs.
    6. Builds a Plotly figure plotting dissonance vs. ratio and overlays lines at common musical intervals.
    7. Returns the figure and a pandas DataFrame for further analysis.

    Exceptions
    ----------
    ValueError:
        Raised if the output of `amplCallback` (if provided) does not match `numPartials` in length.
    """
def plotScoreSetharesDissonance(score: mc.Score, plotType: str = 'line', lineShape: str = 'linear', numPartialsPerNote: int = 6, useMinModel: bool = True, partialsDecayExpRate: float = 0.88, amplCallback: Callable[[list[float]], list[float]] | None = None, dissCallback: Callable[[list[float]], float] | None = None, **kwargs) -> tuple[go.Figure, pd.DataFrame]:
    '''Plot 2D line graph of the Sethares Dissonance over time

    Args:
       score (maialib.Score): A maialib Score object loaded with a valid MusicXML file
       plotType (str): Can be \'line\' or \'scatter\'
       lineShape (str): Can be \'linear\' or \'spline\'
       numPartialsPerNote (int): Amount of spectral partials for each note
       useMinModel (bool): Sethares dissonance values can be computed using the \'minimal amplitude\' model
                    or the \'product amplitudes\' model. The \'min\' model is a more recent approach
       partialsDecayExpRate (float): Partials decay exponential rate (default: 0.88)
       amplCallback: Custom user function callback to generate the amplitude of each spectrum partial
       dissCallback: Custom user function callback to receive all paired partial dissonances and computes 
                     a single total dissonance value output
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
    >>> ml.plotScoreSetharesDissonance(myScore)
    >>> ml.plotScoreSetharesDissonance(myScore, numPoints=15)
    >>> ml.plotScoreSetharesDissonance(myScore, measureStart=10, measureEnd=20)
    '''
def plotChordDyadsSetharesDissonanceHeatmap(chord: mc.Chord, numPartialsPerNote: int = 6, useMinModel: bool = True, amplCallback: Callable[[list[float]], list[float]] | None = None, partialsDecayExpRate: float = 0.88, dissonanceThreshold: float = 0.1, dissonanceDecimalPoint: int = 2, showValues: bool = False, valuesDecimalPlaces: int = 2) -> tuple[plotly.graph_objs._figure.Figure, pd.DataFrame]:
    '''Plot chord dyads Sethares dissonance heatmap

    Args:
       chord (maialib.Chord):  A maialib Chord

    Kwargs:
       numPartialsPerNote (int): Amount of spectral partials for each note
       useMinModel (bool): Sethares dissonance values can be computed using the \'minimal amplitude\' model
                    or the \'product amplitudes\' model. The \'min\' model is a more recent approach
       amplCallback: Custom user function callback to generate the amplitude of each spectrum partial
       partialsDecayExpRate (float): Partials decay exponential rate (default: 0.88)
       dissonanceThreshold (float): Dissonance threshold to skip small dissonance values
       dissonanceDecimalPoint (int): Round chord dissonance value in the plot title
       showValues (bool): If True, show numerical values inside heatmap cells
       valuesDecimalPlaces (int): Number of decimal places to display in cell values

    Returns:
       A list: [Plotly Figure, The plot data as a Pandas Dataframe]

    Raises:
       RuntimeError, KeyError

    Examples of use:

    >>> import maialib as ml
    >>> myChord = ml.Chord(["C3", "E3", "G3"])
    >>> fig, df = plotChordDyadsSetharesDissonanceHeatmap(myChord)
    >>> fig.show()
    '''
