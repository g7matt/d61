import csv
import collections

from matcher import *
from match_results import MatchResults
from paper import Paper


class PaperCollection:
  """A collection of Paper objects."""
  def __init__(self, filename, papers=None):
    """Construct a collection of paper objects.  If the papers are given, treat this as a
    copy constructor, otherwise, read the papers from the file.  In either case, construct
    a lookup dictionary for fast access of the papers by their id."""
    self.filename = filename
    if papers is None:
      with open(filename, 'rb') as csvfile:
        self.papers = [Paper.build(*row) for row in csv.reader(csvfile)][1:]
    else:
      self.papers = papers
    self.lookup = {p.id:p for p in self.papers}

  def __repr__(self):
    return "PaperCollection({!r}, length={})".format(self.filename, len(self.papers))

  def __len__(self):
    return len(self.papers)

  def __iter__(self):
    return self.papers.__iter__()

  def __getitem__(self, item):
    """If a slice is given, return the collection sliced as appropriate.
    If an integer is given, return the nth object in the collection.
    If a paper id is given, look up this paper in the collection and return it."""
    if isinstance(item, slice):
      return PaperCollection(self.filename, self.papers[item])
    elif isinstance(item, int):
      return self.papers[item]
    else:
      return self.lookup[item]

  def find(self, **kws):
    """Return a list of papers which match the criteria exactly."""
    result = self.papers
    if "title" in kws:
      result = (paper for paper in result if paper.match_title(kws["title"]))
    if "authors" in kws:
      result = (paper for paper in result if paper.match_authors(kws["authors"]))
    if "venue" in kws:
      result = (paper for paper in result if paper.match_venue(kws["venue"]))
    return list(result)

  def __getslice__(self, start=None, stop=None):
    return PaperCollection(self.filename, self.papers[start:stop])

  def matches(self, paper, matcher):
    """Return a list of papers which match the paper (according to the matcher function)."""
    return [p for p in self if matcher(p, paper)]

  @property
  def n(self):
    """Shorthand for normalised()."""
    return self.normalised()

  def normalised(self):
    """Return a new collection based on the current one with all the papers in the collection normalised."""
    return PaperCollection(self.filename, [p.normalise() for p in self])

  def align_venues(self, papers, matcher):
    """Find an alignment between all the venues in one collection and the other."""
    counters = collections.defaultdict(collections.Counter)
    for p in papers:
      matches = self.matches(p, matcher)
      if len(matches) == 1:
        counters[p.venue][matches[0].venue] += 1
    self.venue_counts = counters
    self.venue_map = {k2:k1 for k1,v1 in counters.items() for k2 in v1}

  def matchup(self, collection, matcher):
    """Return a MatchResults object with constructed from all the papers in this 
    and 'collection' which match according to 'matcher'."""
    return MatchResults(dict((key,value) for key,value in ((p,collection.matches(p, matcher)) for p in self) if value))
