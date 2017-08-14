import collections
import re

def venue_map(gold, collection1, collection2, min_count=5):
  """Return a dictionary of venue2 -> venue1 maps from the dataset where the map is given by
  the most common mapping, and there are at least min_count entries."""
  # Extract the venues
  v1 = [collection1[x].venue for x,_ in gold]
  v2 = [collection2[x].venue for _,x in gold]
  # Count how many venue2 -> venue1 we find
  d = collections.defaultdict(list)
  for x1,x2 in zip(v1,v2):
    if x1 != "" and x2 != "":
      d[x2].append(x1)
  # Get the most common elements
  d2 = {k:collections.Counter(v).most_common(1) for k,v in d.items()}
  # Ensure that there are at least min_count elements
  return {k:v[0] for k,v in d2.items() if v[0][1] >= min_count}

def show_venue_map(map):
  import pandas as pd
  import numpy as np
  keys   = np.array(map.keys())
  counts = np.array([v[1] for v in map.values()])
  values = np.array([v[0] for v in map.values()])
  idx = np.argsort(-counts)
  #df = pd.DataFrame([("venue_2",keys[idx]), ("venue_1",values[idx]), ("count",counts[idx])])
  df = pd.DataFrame(zip(keys[idx], values[idx], counts[idx]))
  df.columns = ("venue_2", "venue_1", "count")
  return df
