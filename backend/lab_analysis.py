def detect_abnormal(value,low,high):

 if value < low:
  return "LOW"

 if value > high:
  return "HIGH"

 return "NORMAL"
