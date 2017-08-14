from utils import *

class Matcher:
  """A Matcher object is a function which determines whether two papers match.
  It may be negated to indicate that a False response from the matcher means
  that the papers do match.  It is commonly constructed from a function 
  using the @matcher decorator."""
  def __init__(self, label, fn, positive=True):
    self.label = label
    self.func = fn
    self.positive = positive

  def __repr__(self):
    if self.positive:
      return self.label
    else:
      return "-" + self.label

  def __call__(self, p1, p2):
    return self.positive == self.func(p1, p2)

  def __neg__(self):
    return Matcher(self.label, self.func, not self.positive)

  def __add__(self, matcher):
    """Construct a CompoundMatcher from this and another matcher so that both conditions must be met."""
    return CompoundMatcher(self, matcher)

  def __sub__(self, matcher):
    """Construct a CompoundMatcher from this and another matcher so that this must match, 
    and the other matcher must not match."""
    return CompoundMatcher(self, -matcher)

  def __or__(self, matcher):
    """Construct an AltCompoundMatcher from this and another matcher so that either this matches or 
    the other matcher  matches."""
    return AltCompoundMatcher(self, matcher)


class CompositeMatcher(Matcher):
  """An abstract class for composing matches."""
  def __init__(self, *args):
    self.matchers = []
    for arg in args:
      if isinstance(arg, self.__class__):
        self.matchers.extend(arg.matchers)
      else:
        self.matchers.append(arg)

  def __repr__(self):
    return self.sep.join(str(m) for m in self.matchers).replace("+ -", "- ")

  def __str__(self):
    return "({!r})".format(self)

  def __neg__(self):
    return self.__class__(*[-m for m in self.matchers])


class CompoundMatcher(CompositeMatcher):
  """A composite matcher linked by '+', meaning that all matchers must match."""
  sep = " + "

  def __call__(self, p1, p2):
    for matcher in self.matchers:
      if not matcher(p1, p2):
        return False
    return True


class AltCompoundMatcher(CompositeMatcher):
  """A composite matcher linked by '|', meaning that any matchers may match."""
  sep = " | "

  def __call__(self, p1, p2):
    for matcher in self.matchers:
      if matcher(p1, p2):
        return True
    return False

import functools

def matcher(f):
  """A function decorator which turns a function into a Matcher object.  This
  allows the function to be composed with other functions.  For example:

  @matcher
  def title(p, q):
    return p.title == q.title
  """
  if f.__code__.co_argcount > 2:
    keys = f.__code__.co_varnames[2:]
    def wrap(*args, **kws):
      kws.update(zip(keys, args))
      name = "{}({})".format(f.__name__, ", ".join("{}={!r}".format(k,v) for k,v in kws.items()))
      func = functools.partial(f, **kws)
      return Matcher(name, func)
    return wrap
  return Matcher(f.__name__, f)

def fauthors(a1, a2, edit):
  if len(a1) == len(a2):
    return all(edit_distance(x,y)<edit for x,y in zip(a1, a2))

bad_titles = {
  "editorial", "keynote address", "reminiscences on influential papers", 
  "editor s notes", "guest editorial", "book review column",
  "guest editor s introduction", "title"
  }

@matcher
def bad_title(p,q):
  return p.title in bad_titles or q.title in bad_titles

@matcher
def words(p,q,frac=0.5):
  return len(p.words & q.words) > frac * (len(p.words)+len(q.words))*0.5

@matcher
def title(p,q):
  return p.title==q.title

@matcher
def authors(p,q):
  return p.authors==q.authors

@matcher
def first_authors(p,q,len):
  return p.authors[:len]==q.authors[:len]

@matcher
def first_fuzzy_authors(p,q,len,edit):
  return fauthors(p.authors[:len], q.authors[:len], edit)

@matcher
def year(p,q):
  return p.year==q.year

@matcher
def valid_year(p,q):
  return p.year==q.year or q.year=="" or p.year==""

@matcher
def venue(p,q):
  return p.venue==q.venue

@matcher
def fuzzy_title(p,q,edit):
  return edit_distance(p.title, q.title) < edit

@matcher
def cut_fuzzy_title(p,q,edit):
  return cut_edit_distance(p.title, q.title) < edit

#fuzzy_title = lambda n: Matcher("fuzzy_title({})".format(n), lambda p,q: edit_distance(p.title, q.title) < n)
#cut_fuzzy_title = lambda n: Matcher("cut_fuzzy_title({})".format(n), lambda p,q: cut_edit_distance(p.title, q.title) < n)

#cauthors = lambda n: Matcher("cauthors({})".format(n), lambda p,q: p.authors[:n]==q.authors[:n])
#cfauthors = lambda n: Matcher("cfauthors({})".format(n), lambda p,q: fauthors(p.authors[:n], q.authors[:n]))

match = title+(-bad_title|authors+year)

all_but_venue = title + authors + year
all_but_authors = title + venue + year
full = title + authors + year + venue
