from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import zomatopy
import json

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class ActionSearchRestaurants(Action):
    def name(self):
        return 'action_search_restaurants'
        
    def run(self, dispatcher, tracker, domain):        
        count = 0
        config={ "user_key":"6ce88a5ec1419e335afa1c7f92f4b739"}
        zomato = zomatopy.initialize_app(config)
        loc = tracker.get_slot('location')
        cuisine = tracker.get_slot('cuisine')
        price = tracker.get_slot('price')
        location_detail=zomato.get_location(loc, 1)
        d1 = json.loads(location_detail)
        lat=d1["location_suggestions"][0]["latitude"]
        lon=d1["location_suggestions"][0]["longitude"]
        cuisines_dict={'chinese':25,'italian':55,'north indian':50,'south indian':85,'american':1,'mexican':73}
        price_dict = {'low':1,'medium':2,'high':3}
        results=zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), 50000)
        d = json.loads(results)
        response="Showing you top rated restaurants:"+"\n"
        if d['results_found'] == 0:
            response= "No restaurant found for your criteria"
            dispatcher.utter_message(response)
        else:           
            for restaurant in sorted(d['restaurants'], key=lambda x: x['restaurant']['user_rating']['aggregate_rating'], reverse=True): 
                #Getting Top 10 restaurants for chatbot response
                if((price_dict.get(price) == 1) and (restaurant['restaurant']['average_cost_for_two'] < 300) and (count < 10)):
                    response=response+ restaurant['restaurant']['name']+ " in "+ restaurant['restaurant']['location']['address']+ " has been rated "+ restaurant['restaurant']['user_rating']['aggregate_rating']+"."
                    response=response+" And the average price for two people is: "+ str(restaurant['restaurant']['average_cost_for_two'])+"\n"
                    count = count + 1
                elif((price_dict.get(price) == 2) and (restaurant['restaurant']['average_cost_for_two'] >= 300) and (restaurant['restaurant']['average_cost_for_two'] <= 700) and (count < 10)):
                    response=response+ restaurant['restaurant']['name']+ " in "+ restaurant['restaurant']['location']['address']+ " has been rated "+ restaurant['restaurant']['user_rating']['aggregate_rating']+"\n"
                    response=response+" And the average price for two people is: "+ str(restaurant['restaurant']['average_cost_for_two'])+"\n"
                    count = count + 1                        
                elif((price_dict.get(price) == 3) and (restaurant['restaurant']['average_cost_for_two'] > 700) and (count < 10)):
                    response=response+ restaurant['restaurant']['name']+ " in "+ restaurant['restaurant']['location']['address']+ " has been rated "+ restaurant['restaurant']['user_rating']['aggregate_rating']+"\n"
                    response=response+" And the average price for two people is: "+ str(restaurant['restaurant']['average_cost_for_two'])+"\n"
                    count = count + 1           
                if(count==5):
                    dispatcher.utter_message(response)
        if(count<5 and count>0):
            dispatcher.utter_message(response)
        if(count==0):
            response = "Sorry, No results found for your criteria. Would you like to search for some other restaurants?"
            dispatcher.utter_message(response)
        return [SlotSet('emailbody',response)]

        
class ActionSendEmail(Action):

    def name(self):
        return 'action_send_sendemail'

    def run(self, dispatcher, tracker, domain):
        from_user = 'harshyashodafoodiebot@gmail.com'
        to_user = tracker.get_slot('email')
        password = 'Harsh@123'
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login(from_user, password)
        subject = 'Hello from chatbox'
        msg = MIMEMultipart()
        msg['From'] = from_user
        msg['TO'] = to_user
        msg['Subject'] = subject
        body = tracker.get_slot('emailbody')
        msg.attach(MIMEText(body,'plain'))
        text = msg.as_string()
        server.sendmail(from_user,to_user,text)
        server.close()
        
class ActionCheckLocation(Action):

    def name(self):
        return 'action_chklocation'

    def run(self, dispatcher, tracker, domain):
        loc = tracker.get_slot('location')
        
        cities=['vellore', 'gandhinagar', 'aurangabad', 'jabalpur', 'gwalior', 'bhopal', 'vishakapatnam', 'patna',
        'lucknow','nagpur','vadodara','jaipur','indore','kanpur','pune','surat','ahmedabad','hyderabad','bangalore','chennai','kolkata','delhi','mumbai']
        
        
        if loc.lower() not in cities:
            dispatcher.utter_message("Sorry, we don’t operate in this city. Can you please specify some other location")
        return       
