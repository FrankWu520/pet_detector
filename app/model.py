import requests

API_URL = "https://api-inference.huggingface.co/models/wuzhenfrank/pet-detector"
headers = {"Authorization": "Bearer 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"}


def query(filename):
  try:
    with open(filename, "rb") as f:
      data = f.read()
    response = requests.post(API_URL, headers=headers, data=data)
    response = response.json()
    if response[0]["score"] > response[1]["score"]:
      return response[0]
    else:
      return response[1]
  except:
    return response
