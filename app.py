import numpy as np
import tensorflow.keras
import base64
from PIL import Image, ImageOps
from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
from azure.cosmos import exceptions, CosmosClient, PartitionKey
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
from datetime import datetime
from datetime import timedelta
from collections import Counter

def predict_class(file_path):

    np.set_printoptions(suppress=True)
    model = tensorflow.keras.models.load_model('classification_model.h5')
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    image = Image.open(file_path)
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.ANTIALIAS)
    image_array = np.asarray(image)
    image.show()
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
    data[0] = normalized_image_array
    prediction = model.predict(data)
    if(prediction[0][0]>0.5):
        return "Biodegradable"
    else:
        return "NonBiodegradable"


app = Flask(__name__, template_folder='template')
cors = CORS(app)

@app.route("/")
def main():
    return render_template('login.html')
    # return """
    #     Application is working
    # """

@app.route("/control-login",methods=['POST'])
def getData():
    username=request.form['username']
    password=request.form['password']
    request.close()
    if username == 'Siddharth' and password == 'admin':
        HOST = "https://siddharth.documents.azure.com:443/"
        MASTER_KEY="JnlB1dgHuJUiemoaUIZGMKPBiYBeHKygAkjFzMZrbZfiaaIbd9tuHvWyzHzp7GEd0TAut6JjeFN2cRWv1Bso8Q=="
        client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY} )
        db = client.get_database_client("smartsort-database")
        container = db.get_container_client("smartsort-container")
        cur_date = str(datetime.now().date())
        query = "SELECT * FROM c WHERE c.date = '"+cur_date+"'"
        items = list(container.query_items(query=query,enable_cross_partition_query=True))
        print("Today")
        print(items)
        query = "SELECT * FROM c"
        items2 = list(container.query_items(query=query,enable_cross_partition_query=True))
        print("All Time")
        print(items2)
        today = datetime.now().date()
        lastweek_date = today - timedelta(days=7)
        strtoday = str(today)
        strlastweek_date = str(lastweek_date)
        query = "SELECT * FROM c WHERE c.date BETWEEN '"+strlastweek_date+"' AND '"+strtoday+"'"
        items3 = list(container.query_items(query=query,enable_cross_partition_query=True))
        print("Last Week")
        print(items3)
        # query = "SELECT c.date FROM c WHERE c.category = 'Biodegradable' GROUP BY c.date"
        query = "SELECT c.date FROM c WHERE c.category = 'Biodegradable' ORDER BY c.date"
        bioitems = list(container.query_items(query=query,enable_cross_partition_query=True))
        print("BIODEGRADABLE DATES")
        print(bioitems)
        biodatelist = []
        biovallist = []
        templist = []
        for row in bioitems:
            templist.append(row['date'])
        print(templist)
        counter = Counter()
        counter.update(templist)
        for ele in counter:
            biodatelist.append(ele)
            biovallist.append(counter[ele])

        print(biodatelist)
        print(biovallist)

        query = "SELECT c.date FROM c WHERE c.category = 'NonBiodegradable' ORDER BY c.date"
        nonbioitems = list(container.query_items(query=query,enable_cross_partition_query=True))
        print("NON-BIODEGRADABLE DATES")
        print(nonbioitems)
        nonbiodatelist = []
        nonbiovallist = []
        templist = []
        for row in nonbioitems:
            templist.append(row['date'])
        
        counter = Counter()
        counter.update(templist)
        for ele in counter:
            nonbiodatelist.append(ele)
            nonbiovallist.append(counter[ele])


        query = "SELECT c.datetime, c.weight FROM c ORDER BY c.datetime"
        bioweightitems = list(container.query_items(query=query,enable_cross_partition_query=True))
        print("WEIGHT ITEMS - BIO")
        print(bioweightitems)
        bioweightdates = []
        bioweightvalues = []

        for row in bioweightitems:
            bioweightdates.append(row['datetime'])
            bioweightvalues.append(float(row['weight'])*1000)

        print(bioweightdates)
        print(bioweightvalues)


        return render_template("home.html", todayValues = items, allTimeValues = items2, lastWeekValues = items3, labelsbio = biodatelist, valuesbio = biovallist, labelsnon = nonbiodatelist, valuesnon = nonbiovallist, labelsbioweight = bioweightdates, valuesbioweight = bioweightvalues)
    
    return render_template('login.html')

@app.route("/process", methods=["POST"])
def processReq():
    data = request.files["img"]
    data.save("img.jpg")
    resp = predict_class("img.jpg")
    return resp



if __name__ == "__main__":
    app.run(debug=True)
