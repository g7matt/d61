def edit_distance(a, b):
  """Calculate the Levenshtein_distance between to strings.
  Here we choose the cost of insertion=1, deletion=1, substitution=1.5

  Thanks: https://en.wikipedia.org/wiki/Levenshtein_distance."""
  m = len(a)
  n = len(b)
  if n < m:
    return edit_distance(b, a)
  v0 = range(n+1)
  v1 = [0] * (n+1)
  for i in range(m):
    v1[0] = i+1
    for j in range(n):
      if a[i] == b[j]:
        cost = 0
      else:
        cost = 1.5
      v1[j+1] = min(v1[j]+1, v0[j+1]+1, v0[j]+cost)
    v0, v1 = v1, v0
  return v0[-1]
