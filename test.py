import requests

# url = "https://smartsort.herokuapp.com/process"
# filess = {"img": open("C:/Users/siddh/Smart Sort/testimage.jpg", "rb")}
# results = requests.post(url, files=filess)
# print(results.text)

import numpy as np
import base64

with open("testimage.jpg", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read())


print(encoded_string)
message= base64.b64decode(encoded_string)
with open("savedimage.jpg", "wb") as fh:
    fh.write(message)
