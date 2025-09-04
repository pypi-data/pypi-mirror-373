
def flatlist(li):
  flat = []
  for i in li:
    if isinstance(i,list):
      flat.extend(flatlist(i)) 
      
    else:
      flat.append(i)
  return flat
