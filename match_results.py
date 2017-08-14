import collections
from paper import Paper
import pandas as pd

class MatchResult:
  """A MatchResult is a pair: the key is the reference paper, and the values are those papers it matches."""
  def __init__(self, item):
    self.key, self.values = item

  def __repr__(self):
    return "{!r}: {}".format(self.key, self.values)

  def __str__(self):
    return "{}\n{}".format(self.key, "\n".join(str(v) for v in self.values))

  @property
  def id(self):
    """Display the ids of a paper and of its matching papers."""
    return "{}\n{}".format(self.key.id, "\n".join(str(v.id) for v in self.values))

  @property
  def authors(self):
    """Display the authors of a paper and of its matching papers."""
    return "{}\n{}".format(", ".join(self.key.authors), "\n".join(", ".join(v.authors) for v in self.values))

  @property
  def title(self):
    """Display the title of a paper and of its matching papers."""
    return "{}\n{}".format(self.key.title, "\n".join(str(v.title) for v in self.values))

  @property
  def venue(self):
    """Display the venue of a paper and of its matching papers."""
    return "{}\n{}".format(self.key.venue, "\n".join(str(v.venue) for v in self.values))

  @property
  def year(self):
    """Display the year of a paper and of its matching papers."""
    return "{}\n{}".format(self.key.year, "\n".join(str(v.year) for v in self.values))


class MatchResults:
  """MatchResults is a dictionary of MatchResult values, mapping papers to their matches."""
  def __init__(self, results):
    self.results = results
    self.dict = {k.id:(k,v) for k,v in results.items()}

  @staticmethod
  def fromKeys(pairs, collection1, collection2):
    """Build a MatchResults object from a list of pairs (the key from collection1, 
    and the key from collection2).  This is used for example to create a MatchResults object
    from the gold file."""
    merged = collections.defaultdict(list)
    for key1,key2 in pairs:
      merged[key1].append(key2)
    result = {collection1[key]:[collection2[v] for v in values] for key,values in merged.items()}
    return MatchResults(result)

  def _get(self, index):
    """Get a single MatchResult item given an integer, string or Paper index."""
    if isinstance(index, int):
      return self.results.items()[index]
    if isinstance(index, str):
      return self.dict[index]
    if isinstance(index, Paper):
      return index, self.results[index]

  def __getitem__(self, index):
    """If the index is an integer, string or Paper, get the corresponding MatchResult.
    If the index is a list, tuple, set or slice, get the corresponding MatchResult objects and
    bundle them back into a MatchResults object for further processing."""
    if isinstance(index, Paper):
      return MatchResult(self._get(index))
    elif isinstance(index, (list, tuple, set)):
      return MatchResults(dict(self._get(x) for x in index))
    elif isinstance(index, slice):
      return MatchResults(dict(self.results.items()[index]))
    else:
      return MatchResult(self._get(index))

  def __len__(self):
    return len(self.results)

  def __repr__(self):
    return repr(self.results.keys())

  @property
  def pairs(self):
    """Return pairs of ids corresponding to matches between collection1 and collection2.
    This is effectively the reverse operation to MatchResults.fromKeys()"""
    return {(k.id,m.id) for k,matches in self.results.items() for m in matches}

  @property
  def dataframe(self):
    """Construct a dataframe from the match results where each value is a paper."""
    keys, values = list(zip(*self.results.items()))
    n = max(len(v) for v in values)
    result = dict(DBLP1=keys)
    for i in range(n):
      result["Scholar ({})".format(i)] = [v[i] if i<len(v) else None for v in values]
    return pd.DataFrame(result)

  @property
  def id(self):
    """Construct a dataframe from the match results where each value is the id of the paper."""
    df = self.dataframe
    for col in df.columns:
      df[col] = [v.id if v is not None else "---" for v in df[col]]
    return df

  @property
  def authors(self):
    """Construct a dataframe from the match results where each value is the authors of the paper."""
    df = self.dataframe
    for col in df.columns:
      df[col] = [", ".join(v.authors) if v is not None else "---" for v in df[col]]
    return df

  @property
  def title(self):
    """Construct a dataframe from the match results where each value is the title of the paper."""
    df = self.dataframe
    for col in df.columns:
      df[col] = [v.title if v is not None else "---" for v in df[col]]
    return df

  @property
  def venue(self):
    """Construct a dataframe from the match results where each value is the venue of the paper."""
    df = self.dataframe
    for col in df.columns:
      df[col] = [v.venue if v is not None else "---" for v in df[col]]
    return df

  @property
  def year(self):
    """Construct a dataframe from the match results where each value is the year of the paper."""
    df = self.dataframe
    for col in df.columns:
      df[col] = [v.year if v is not None else "---" for v in df[col]]
    return df

  def __add__(self, matcher):
    """Add this with a matcher.  That is, construct a new MatchResults based on this one, but further constrained."""
    result = dict()
    for key, values in self.results.items():
      r = [v for v in values if matcher(key,v)]
      if r:
        result[key] = r
    return MatchResults(result)

  def __or__(self, match_results):
    """Or this with other matcher results!  That is, construct a new MatchResults based on this, 
    but extended to include the new match results."""
    result = {k:v[:] for k,v in self.results.items()}
    for k,v in match_results.results.items():
      if k in result:
        base = result[k]
        result[k].extend([x for x in v if x not in base])
      else:
        result[k] = v[:]
    return MatchResults(result)
