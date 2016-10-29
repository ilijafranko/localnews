# -*- coding: utf-8 -*-

import requests
from flask import request, json
from datetime import timedelta
from sqlalchemy import *
from .models import app, sess, Location, Post, Locdict, datetime


#webhook
@app.route('/localnews', methods=['GET','POST'])
def localnews():
    data = request.get_json()
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    return get_news(message_text, sender_id)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200

#query news
def get_news(message_text, sender_id):
    place = '+'.join(message_text.split()).encode('utf-8')
    #Get coordinates from location
    url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
    params = {'query': place, 'key': '[GoogleAPIKEY]'}
    r = requests.get(url, params=params)
    if r.json()['status'] == 'OK':
        results = r.json()['results']
        location = results[0]['geometry']['location']
        location = 'Point (' + str(location['lng']) + ' ' + str(location['lat']) + ')'
        dayago = datetime.utcnow() - timedelta(hours=1000)
        loc = func.ST_GeomFromText(location, 4326)
        radius = 8000
        #Get news in radius <= 8000
        userlocs = sess.query(Location.id.label('loc_id'),
                              func.ST_Distance_Sphere(loc, Location.location).label('dist'),
                              case([(Locdict.loc_id == 61022, 5900),], else_ = 0).label("weight")) \
                    .filter(func.ST_Distance_Sphere(Location.location, loc) <= radius)\
                    .outerjoin(Locdict, Locdict.loc_id ==Location.id).subquery()
        #Sort by time and distance
        cards = sess.query(Post).join(userlocs, Post.loc_id == userlocs.c.loc_id)\
                .filter(Post.postedtime > dayago, Post.poster_id != 0) \
                    .order_by(desc(userlocs.c.dist) * 0.08 - func.pow(Post.timediff,1.5)*0.5).limit(10)
        elmlist = []
        for card in cards:
            elm = {
                    "title": card.title[0:75],
                    "subtitle": card.locname,
                    "item_url": card.link,
                    "image_url": card.thumbnail,
                    "buttons": [{
                        "type": "web_url",
                        "url": card.link,
                        "title": "Lesen"
                    }]
            }
            elmlist.append(elm)
        if len(elmlist) > 0:
            send_message(sender_id, elmlist)
        else:
            elmlist = "An diesem Ort scheint es nichts Neues zu geben. Nenne mir bitte einen" \
                  " Bezirk, eine Straße oder eine Postleitzahl in Berlin."
            err_message(sender_id, elmlist)
    else:
        elmlist = "Hallo, ich bin ein Bot, der dir die Nachrichten aus deiner Nähe liefert. Nenne mir bitte einen" \
                  " Bezirk, eine Straße oder eine Postleitzahl in Berlin."
        err_message(sender_id, elmlist)


def err_message(recipient_id, elmlist):

    #log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": ''
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": elmlist
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        print r.status_code


def send_message(recipient_id, elmlist):

    #log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": ''
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
           "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                        "elements": elmlist
        }
           }}
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        print r.status_code

