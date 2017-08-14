import collections
import re


class Paper(collections.namedtuple('Paper', "id title words authors venue year")):
  """Paper is a class based on a named tuple, used to represent the attributes of a paper."""
  def __repr__(self):
    return self.id

  def __str__(self):
    return """\
ID:      {}
Title:   {}
Authors: {}
Venue:   {}
Year:    {}
""".format(self.id, self.title, self.authors, self.venue, self.year)

  @staticmethod
  def build(id, title, authors, venue, year):
    """Construct a Paper object, by performing minimal operations:
    - words are the set of words making up the title of the paper
    - authors are split on commas
    - years are turned into integers"""
    try:
      year = int(year)
    except ValueError:
      pass
    return Paper._make((id, title, set(title.split()), authors.split(", "), venue, year))

  def __hash__(self):
    return hash(self.id)

  def normalised_title(self):
    """Return the title normalised for punctuation and case."""
    return re.sub("[^a-z0-9]+", " ", self.title.lower()).strip()

  @staticmethod
  def normalised_name(names):
    """Return a name normalised into the form: one initial letter, space, final name"""
    if len(names) == 1:
      return names[0]
    return (names[0][0].upper() + " " + names[-1].capitalize())

  def normalised_authors(self):
    """Return the authors as a list in normalised form."""
    return [self.normalised_name(names) for names in (author.split() for author in self.authors) if names]

  def normalised_venue(self):
    v = self.venue.strip(",").strip()
    if v == "N/A":
      return ""
    v = re.sub(r"proc(\.|eedings)? ?(of ?(the )?)?(\d+(st|nd|rd|th))? ?", "proc ", v.lower())
    v = re.sub(r"(19|20)\d\d ?", "", v) # get rid of years
    return v

  def normalise(self):
    """Return a version of this with some level of normalisation to facilitate comparisons."""
    title = self.normalised_title()
    item = (
      self.id, 
      title,
      set(title.split()),
      self.normalised_authors(),
      self.normalised_venue(),
      self.year)
    return Paper._make(item)
