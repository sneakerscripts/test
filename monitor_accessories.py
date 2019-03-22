import requests
import json
from bs4 import BeautifulSoup
import urllib3
import time
from deepdiff import DeepDiff
import datetime

initial = []

session = requests.Session()
url = "http://www.supremenewyork.com/shop/all/accessories"
data = session.get(url)
soup = BeautifulSoup(data.text, 'html.parser')
for link in soup.find_all('article'):
    prod_link = link.div.h1.a.get('href')
    product = link.div.h1.get_text()
    color = link.div.p.get_text()
    instock = link.div.a.div
    if instock != None:
    	instock = link.div.a.div.get_text()
    else:
    	instock = "In Stock!"
    initial.append("Product: " + product + " - " + "Color: " + color + " - " + "Status: " + str(instock) + " - " + "Link: " + "http://www.supremenewyork.com"+prod_link)
#print(initial)
#print("\n")


infinte = "true"
while infinte == "true":
	try:
		restock_check = []
		session = requests.Session()
		url = "http://www.supremenewyork.com/shop/all/accessories"
		try:
			data = session.get(url)
		except:
			print("Connection Error!")
		soup = BeautifulSoup(data.text, 'html.parser')
		for link in soup.find_all('article'):
		    prod_link = link.div.h1.a.get('href')
		    product = link.div.h1.get_text()
		    color = link.div.p.get_text()
		    instock = link.div.a.div
		    if instock != None:
		    	instock = link.div.a.div.get_text()
		    else:
		    	instock = "In Stock!"
		    restock_check.append("Product: " + product + " - " + "Color: " + color + " - " + "Status: " + str(instock) + " - " + "Link: " + "http://www.supremenewyork.com"+prod_link)
		#print(restock_check)
		test = DeepDiff(initial, restock_check, verbose_level=1, view='tree')
		restocks = len(test)
		if restocks != 0:
			set_of_values_changed = test['values_changed']
			changed = list(set_of_values_changed)[0]
			changes = changed.t2
			changes = changes.replace(" - ", "\n")
			print(changes)
			if "sold out" not in changes:
				print("RESTOCKED!")
				time = datetime.datetime.now()
				time = str(time)
				webhook_url = 'https://hooks.slack.com/services/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'
				slack_data = {'text': ":rotating_light:RESTOCK ALERT:rotating_light:\n" + "\n" + changes + "\n" + "\n" + time}

				response = requests.post(
				    webhook_url, data=json.dumps(slack_data),
				    headers={'Content-Type': 'application/json'}
				)
				if response.status_code != 200:
				    raise ValueError(
				        'Request to slack returned an error %s, the response is:\n%s'
				        % (response.status_code, response.text)
				    )
			else:
				print("OUT OF STOCK :(")
			initial = restock_check
		else:
			print("NO RESTOCK!")
	except:
		print("Error connection... retrying!")
