from flask import Flask, render_template, url_for, request, redirect
import requests
# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime
from bs4 import BeautifulSoup as bs
from flask_cors import CORS,cross_origin
from urllib.request import urlopen as uReq
import pymongo

app = Flask(__name__)     #intitalisng flask app with name = app
@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index_deploy.html")


@app.route('/scrap',methods=['POST','GET'])
@cross_origin()
def index():

    if request.method == 'POST':
        searchString = request.form['content']
        try:

            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
          #  print(flipkart_html)
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})  #Here class name can be chnaged so check it from flipkart.
            del bigboxes[0:3]
            box = bigboxes[0]
           # print(box)
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prod_html = bs(prodRes.text, "html.parser")
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})
            product_FullName=prod_html.find_all('span', {'class': "B_NuCI"})[0].text


            filename = searchString+".csv"
            fw = open(filename, "w")
            headers = "Product,Full product name, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)

            reviews = []
          #  print(commentboxes.count())
            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    name = 'No Name'

                try:
                    rating = commentbox.div.div.div.div.text

                except:
                    rating = 'No Rating'

                try:
                    commentHead = commentbox.div.div.div.find_all('p',{'class':'_2-N8zT'})[0].text
                except:
                    commentHead = 'No Comment Heading'
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    custComment = comtag[0].div.text
                except:
                    custComment = 'No Customer Comment'
           #     fw.write(searchString+","+name.replace(",", ":")+","+rating + "," + commentHead.replace(",", ":") + "," + custComment.replace(",", ":") + "\n")

       #         fw.write(searchString + "," +product_FullName + "," + name + "," + rating + "," + commentHead+ "," + custComment+ "\n")

                mydict = {"Product searched": searchString, "Full product name":product_FullName, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
            #    fw.write(searchString + "," +product_FullName + "," + name + "," + rating + "," + commentHead+ "," + custComment+ "\n")

                reviews.append(mydict)

            return render_template('results.html', reviews=reviews)
        except Exception as e:
           print("eRROR OCCURED=", e)
           return "Some error occured"
    else:
        return render_template('index_deploy.html')

if __name__ == "__main__":
    print("Running")

    app.run(debug=True)