import csv
from match_results import *

RPF_names   = ["recall", "precision", "F1"]
RPF_colours = ["#666", "steelblue", "red"]

class ScoreResults:
  """ScoreResults is a helper class that allows easy communication of the results.
  In particular, it stores the gold and actual results for the match, and calculates
  the true positives, false positives and false negatives.  
  """
  def __init__(self, scorer, match_results, matcher):
    """Save the matcher, the gold and actual results.  Further, save the collections
    so that the papers can be easily reconstructed later.  Finally, calculate
    _tp, _fp, _fn as the true positives, false positives and false negatives (respectively),
    expressed as sets of (paper1.id, paper2.id)."""
    self.match_results = match_results
    self.matcher = matcher
    self.collection1 = scorer.collection1
    self.collection2 = scorer.collection2
    gold = scorer._gold
    actual = set(match_results.pairs)
    self._gold = gold
    self._actual = actual
    self._tp = actual & gold
    self._fp = actual - gold
    self._fn = gold - actual

  def __str__(self):
    """Show some basic statics about the match results."""
    return """\
Matcher:   {!r}
Gold:      {} relations
Actual:    {} relations
Recall:    {:.2f}%
Precision: {:.2f}%
F1:        {:.2f}%""".format(self.matcher, len(self._gold), len(self._actual), 100*self.recall, 100*self.precision, 100*self.F1)

  def __repr__(self):
    """As a side-effect, produce a bokeh chart showing the recall, precision and F1 score,
    but actually return nothing."""
    from bokeh.plotting import figure, show
    from bokeh.models import LabelSet, ColumnDataSource, Range1d
    data = dict()
    data["indices"] = range(1,4)
    data["values"]  = [self.recall*100, self.precision*100, self.F1*100]
    data["labels"]  = ["%.2f%%" % x for x in data["values"]]
    data["names"]   = RPF_names
    data["colours"] = RPF_colours
    source = ColumnDataSource(data=data)
    fig = figure(title=repr(self.matcher), x_range=Range1d(0, 102), y_range=RPF_names, plot_height=140, plot_width=900, toolbar_location=None)
    fig.hbar(y="indices", height=0.8, right="values", line_color=None, fill_color="colours", source=source)
    labels = LabelSet(x="values", y="indices", text="labels", level='glyph', text_align="right", x_offset=-6, y_offset=-10, render_mode='canvas', text_color="white", source=source)
    fig.add_layout(labels)
    show(fig)
    return ""

  def __add__(self, matcher):
    """Return a new ScoreResults object which is the combination with
    a Matcher object to restrict the results to those which also match matcher."""
    results = self.match_results + matcher
    return ScoreResults(self, results, self.matcher + matcher)

  def __sub__(self, matcher):
    """Return a new ScoreResults object which is the combination with
    a Matcher object to restrict the results to those which don't match matcher."""
    results = self.match_results + -matcher
    return ScoreResults(self, results, self.matcher - matcher)

  def __or__(self, score_results_or_matcher):
    """Return a new ScoreResults object which is the combination with either 
    a ScoreResults object, or a Matcher object to extend the results."""
    if not isinstance(score_results_or_matcher, ScoreResults):
      matcher = score_results_or_matcher
      scorer = Eval(None, self.collection1, self.collection2, self._gold)
      score_results = scorer.calc(matcher)
    else: 
      score_results = score_results_or_matcher
    results = self.match_results | score_results.match_results
    return ScoreResults(self, results, self.matcher | score_results.matcher)

  def _lookup(self, attr):
    """A helper function which takes an attribute such as "_fp", 
    (expressed as a set of [paper1,paper2] pairs) and turns it into a
    MatchResults object.  This allows the object to be interrogated
    to better understand the results."""
    if hasattr(self, "__" + attr):
      return getattr(self, "__" + attr)
    v = getattr(self, "_" + attr)
    result = MatchResults.fromKeys(v, self.collection1, self.collection2)
    setattr(self, "__" + attr, result)
    return result

  @property
  def gold(self):
    """The gold standard result, expressed as a MatchResults object."""
    return self._lookup("gold")

  @property
  def actual(self):
    """Actual result of the matching, expressed as a MatchResults object."""
    return self._lookup("actual")

  @property
  def tp(self):
    """True positives, expressed as a MatchResults object."""
    return self._lookup("tp")

  @property
  def fp(self):
    """False positives, expressed as a MatchResults object."""
    return self._lookup("fp")

  @property
  def fn(self):
    """False negatives, expressed as a MatchResults object."""
    return self._lookup("fn")

  @property
  def recall(self):
    return len(self._tp)/(1.0*len(self._gold))

  @property
  def precision(self):
    return len(self._tp)/(1.0*len(self._actual))

  @property
  def F1(self):
    return self.F(1.0)

  def F(self, beta):
    """Return the F_beta score."""
    precision = self.precision
    recall = self.recall
    return (1+beta*beta) * (precision * recall) / (beta*beta*precision + recall)


class Eval:
  """Eval houses the gold standard match and the two paper collections.
  It is used to calculate the effectiveness of matches"""

  def __init__(self, filename, collection1, collection2, gold=None):
    """If gold is None, construct an Eval object by reading the file specified by filename.
    Otherwise use the matches given by gold.  In either case, limit the values in gold
    to those that possible in the product collection1 x collection2.  If collection1 and
    collection2 have not been subsetted, this won't make a difference, but it means that
    smaller datasets can be considered.  For example, a training or development dataset
    can be effectively evaluated under this subset."""
    if gold is not None:
      self._gold = gold
    else:
      with open(filename, 'rb') as csvfile:
        self._gold = set([tuple(row) for row in csv.reader(csvfile)][1:])
    self.collection1 = collection1
    self.collection2 = collection2
    keys1 = set([x.id for x in self.collection1])
    keys2 = set([x.id for x in self.collection2])
    self._gold = set([(k1,k2) for k1,k2 in self._gold if k1 in keys1 and k2 in keys2])

  def __getitem__(self, item):
    """Return an Eval object with a subset of the papers from collection2, and with
    gold trimmed appropriately too."""
    return Eval(None, self.collection1, self.collection2[item], self._gold)

  def calc(self, matcher):
    """Return a ScoreResults object as the result of matching papers from collection1 with those
    in collection2."""
    m = self.collection1.matchup(self.collection2, matcher)
    return ScoreResults(self, m, matcher)

  def fit(self, matcher, values, var):
    """Display parameter fitting by looping through 'values' and evaluating the performance 
    of 'matcher'.  Note that 'matcher' is expressed as a function which takes a single value
    as a parameter, and returns a Matcher object for matching.  
    
    'var' is the name of the looping parameter for display purposes only."""
    scores = []
    for v in values:
        s = self.calc(matcher(v))
        scores.append([s.recall, s.precision, s.F1])
    self._display_fit(matcher, values, scores, var)

  def _display_fit(self, matcher, keys, values, var):
    """A helper function to display the results of parameter fitting."""
    import pandas as pd
    from bokeh.charts import Line, show
    df = pd.DataFrame(dict(F1=list(zip(*values))[2]))
    df.index = keys
    line = Line(df, ylabel="", title=repr(matcher(var)), xlabel=var, plot_width=900, plot_height=300, toolbar_location=None)
    show(line)
