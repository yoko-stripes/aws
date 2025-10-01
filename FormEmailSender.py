import json
import boto3
import os
import re
import html
import sys
from urllib.parse import parse_qs 

def lambda_handler(event, context):
    # env varibles implemented
    getareceiveradvertisingratebook = os.getenv ('RECIPIENT_EMAIL_ADVERTISING_RATE_BOOK')
    getareceivercontactus = os.getenv ('RECIPIENT_EMAIL_CONTACT_US')
    getareceiverktown = os.getenv ('RECIPIENT_EMAIL_KTOWN')
    getareceiverreprintrequest = os.getenv ('RECIPIENT_EMAIL_REQUEST_REPRINT')
    getasendercontactus = os.getenv ('SENDER_EMAIL_CON_US')
    getasenderratebook = os.getenv ('SENDER_EMAIL_RATE_BOOK')
    getasenderktown = os.getenv ('SENDER_EMAIL_KTOWN')
    getasenderrequestreprint = os.getenv ('SENDER_EMAIL_REQUEST_REPRINT')
    awsareamap = os.getenv ('SES_REGION')
    
    sesClient = boto3.client("ses", region_name = awsareamap )

    #print("Received event:", json.dumps(event))

    body = event.get('body', None)
    if body is None:
    # Handle the case where the body is missing
      return {
        'statusCode': 400,
        'body': 'Try Again Later.'
    }

    body = event['body']
    form_data = parse_qs(body)

    # Honey Pot 
    first_name = form_data.get('first_name', [''])[0]

    # iamform this will hold the form name contact us k-town now etc
    iamform = form_data.get('iamform', [''])[0]

    incommingform = iamform 
    if incommingform == "ConUs":
        name = form_data.get('name', [''])[0] 
        email = form_data.get('email', [''])[0] 
        location = form_data.get('location', [''])[0] 
        topic = form_data.get('topic', [''])[0] 
        message = form_data.get('message', [''])[0]
        checkthevar = [name, email, location, topic, message]
        # Create a data var
        data = {
       'names': name,
       'locations': location,
       'topics': topic,
       'messages': message
        }
    elif incommingform == "KTno":
        name = form_data.get('name', [''])[0] 
        town = form_data.get('town', [''])[0] 
        email = form_data.get('email', [''])[0] 
        topic = form_data.get('topic', [''])[0] 
        message = form_data.get('message', [''])[0]
        checkthevar = [name, town, email, topic, message]
        # Create a data var
        data = {
       'names': name,
       'towns': town,
       'topics': topic,
       'messages': message
        }
    elif incommingform == "RePrin":
        name = form_data.get('name', [''])[0] 
        email = form_data.get('email', [''])[0] 
        location = form_data.get('location', [''])[0] 
        message = form_data.get('message', [''])[0]
        checkthevar = [name, email, location, message]
        # Create a data var
        data = {
       'names': name,
       'locations': location,
       'messages': message
        }  
    elif incommingform == "AdvRaBoK":
        name = form_data.get('name', [''])[0] 
        lname = form_data.get('lname', [''])[0] 
        email = form_data.get('email', [''])[0] 
        location = form_data.get('location', [''])[0] 
        company = form_data.get('company', [''])[0]
        checkthevar = [name, lname, email, location, company]
        # Create a data var
        data = {
       'names': name,
       'lnames': lname,
       'locations': location,
       'companys': company
        }
    else:
        return {
            'statusCode': 204,
            'body': 'Thanks for your submission...'  # Message
        }    
    # Stop processing Form cannot be Verified

    # Check HoneyPot Field
    if first_name:
        return  {
            'statusCode': 204,
            'headers': {},
            'body': ''
        }
    # Continue normal processing if first_name is empty 

    # Valid Email Check
    epattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    # If email does not match the pattern, exit the program
    if not re.match(epattern, email):
    # Exit the program if the email is invalid   
        return {
            'statusCode': 204,
            'body': 'Thank You...'  # blank message
        } 

    # Blocking Disposable Email Services
    # List of known disposable email services
    disposable_domains = ["mailinator.com", "10minutemail.com", "guerrillamail.com", "maildrop.cc", "throwawaymail.com",
                        "temp-mail.org", "getnada.com", "fakemailgenerator.com", "mohmal.com", "dispostable.com", 
                        "yopmail.com", "spamgourmet.com", "tempail.com", "emailondeck.com", "mailcatch.com", 
                        "trashmail.com", "binkmail.com", "fakeinbox.com", "throwawayemail.com", "tempinbox.com"]
    # If Found Stop Program
    if email.split('@')[1] in disposable_domains:
    # Exit the program if a disposable email is detected   
        return {
            'statusCode': 204,
            'body': 'Thank You...'  # blank message
        } 
      
    # Domain Blocker
    blockeddomain = email.split('@')[1].lower()
    # Check if the domain is Russia or China
    if blockeddomain.endswith('.ru') or blockeddomain.endswith('.cn'): 
    # Return your custom message or just an empty body Program has been Stopped Bad Domain
        return {
            'statusCode': 204,
            'body': 'Thank You...'  # Custom message for blocked domains
        }

    #Check For Spammy Words
    spammyspam = ['free', 'buy now', 'http', 'https', 'www', 'script', '$', 'kill', 'opportunity', 'attention', 'salary', 'proposal',
                  'deal', 'invitation', 'investment', 'exclusive', 'spende', 'risk-free', 'audit', 'spende' ]
    
    # checkthevar will depend on iamform           
    if any(phrase.lower() in var.lower() for phrase in spammyspam for var in checkthevar):
       # If spam is detected stop the code
        return {
            'statusCode': 204,
            'body': 'Thank You...'  # blank message
        }    
    
    def sanitize_email(email):
    # Strip any extra spaces and convert to lowercase
        return email.strip().lower()

    # Sanitize function
    sanitize = lambda stripitall: html.escape(stripitall.strip())

    # Use a loop to apply the sanitize function to each field
    sanitized_data = {field: sanitize(data[field]) for field in data}

    if incommingform == "ConUs":
       sanitized_name = sanitized_data['names']
       sanitized_email = sanitize_email(email)
       sanitized_location = sanitized_data['locations']
       sanitized_topic = sanitized_data['topics']
       sanitized_message = sanitized_data['messages']
    
       emailResponse = sesClient.send_email(
         Destination = {
            "ToAddresses":[
                getareceivercontactus
            ]
         },
         Message={
            "Body":{
                "Text":{
                    "Data":  f"Name: {sanitized_name} \n"
                             f"Email: {sanitized_email} \n"
                             f"Location: {sanitized_location} \n"
                             f"Topic: {sanitized_topic} \n"
                              "Message:\n"
                             f"{sanitized_message}"
                }
            },
            "Subject":{
                "Data": "Contact Us Submission"
            },
         },
        Source = getasendercontactus
      )
       html_content = """
        <html>
        <head>
            <title>Form Submitted</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                }
                #Pformtext2 {
                    margin: 0 auto;
                    text-align: center;
                    max-width: 680px;
                    width: auto;
                    background-color: #fff;
                    padding: 30px;
                }
                h1 {
                    color: #268dfb;
                }
                h2 {
                    color: #555;
                }
                p {
                    font-size: 16px;
                    color: #555;
                }
            </style>
        </head>
            <body>
                <div id="Pformtext2">
                <label class="labb2"><h1>Your Message Has Been Sent.</h1><span style="font-size:90px;">&#128231;</span></label>
                <hr>
                <h2>Contact Form Submission.</h2>
                <h3>
                <p>Thank you for reaching out to us.<br> We will get back to you as soon as possible.</p>
                </h3>
                </div>
            </body> 
        </html>  
      """
       return {
            'statusCode': 200,
            'headers': {
            'Content-Type': 'text/html'
               },
            'body': html_content
            }  
    elif incommingform == "KTno":
       sanitized_name = sanitized_data['names']
       sanitized_town = sanitized_data['towns']
       sanitized_email = sanitize_email(email)
       sanitized_topic = sanitized_data['topics']
       sanitized_message = sanitized_data['messages']
    
       emailResponse = sesClient.send_email(
         Destination = {
            "ToAddresses":[
                getareceiverktown
            ]
         },
         Message={
            "Body":{
                "Text":{
                    "Data":  f"Name: {sanitized_name} \n"
                             f"Location: {sanitized_town} \n"
                             f"Email: {sanitized_email} \n"
                             f"Topic: {sanitized_topic} \n"
                              "Message:\n"
                             f"{sanitized_message}"
                }
            },
            "Subject":{
                "Data": "K Town Now Submission"
            },
         },
        Source = getasenderktown
      )
       html_content = """
        <html>
        <head>
            <title>Form Submitted</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                }
                #Pformtext2 {
                    margin: 0 auto;
                    text-align: center;
                    max-width: 680px;
                    width: auto;
                    background-color: #fff;
                    padding: 30px;
                }
                h1 {
                    color: #268dfb;
                }
                h2 {
                    color: #555;
                }
                p {
                    font-size: 16px;
                    color: #555;
                }
            </style>
        </head>
            <body>
                <div id="Pformtext2">
                <label class="labb2"><h1>Your Message Has Been Sent.</h1></label>
                <hr>
                <h2>K Town Now Form Submission.</h2>
                <h3>
                <p>Thank you for reaching out to us.<br> We will get back to you as soon as possible.</p>
                </h3>
                </div>
            </body> 
        </html>  
      """
       return {
            'statusCode': 200,
            'headers': {
            'Content-Type': 'text/html'
               },
            'body': html_content
            }  
    elif incommingform == "RePrin":
       sanitized_name = sanitized_data['names']
       sanitized_email = sanitize_email(email)
       sanitized_location = sanitized_data['locations']
       sanitized_message = sanitized_data['messages']
    
       emailResponse = sesClient.send_email(
         Destination = {
            "ToAddresses":[
                getareceiverreprintrequest
            ]
         },
         Message={
            "Body":{
                "Text":{
                    "Data":  f"Name: {sanitized_name} \n"
                             f"Email: {sanitized_email} \n"
                             f"Location: {sanitized_location} \n"
                              "Message:\n"
                             f"{sanitized_message}"
                }
            },
            "Subject":{
                "Data": "Reprint Request Submission"
            },
         },
        Source = getasenderrequestreprint
      )
       html_content = """
        <html>
        <head>
            <title>Form Submitted</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                }
                #Pformtext2 {
                    margin: 0 auto;
                    text-align: center;
                    max-width: 680px;
                    width: auto;
                    background-color: #fff;
                    padding: 30px;
                }
                h1 {
                    color: #268dfb;
                }
                h2 {
                    color: #555;
                }
                p {
                    font-size: 16px;
                    color: #555;
                }
            </style>
        </head>        
            <body>
                <div id="Pformtext2">
                <label class="labb2"><h1>Your Message Has Been Sent.</h1></label>
                <hr>
                <h2>Reprint Request Form Submission.</h2>
                <h3>
                <p>Thank you for reaching out to us.<br> We will get back to you as soon as possible.</p>
                </h3>
                </div> 
            </body> 
        </html>  
      """
       return {
            'statusCode': 200,
            'headers': {
            'Content-Type': 'text/html'
               },
            'body': html_content
            }  
    elif incommingform == "AdvRaBoK":
       sanitized_name = sanitized_data['names']
       sanitized_lname = sanitized_data['lnames']
       sanitized_email = sanitize_email(email)
       sanitized_location = sanitized_data['locations']
       sanitized_company = sanitized_data['companys']
    
       emailResponse = sesClient.send_email(
         Destination = {
            "ToAddresses":[
                getareceiveradvertisingratebook
            ]
         },
         Message={
            "Body":{
                "Text":{
                    "Data":  f"Name: {sanitized_name} \n"
                             f"Last Name: {sanitized_lname} \n"
                             f"Email: {sanitized_email} \n"
                             f"Location: {sanitized_location} \n"
                             f"Company Name: {sanitized_company}"
                }
            },
            "Subject":{
                "Data": f"Advertising {sanitized_location} Rate Book Submission"
            },
         },
       Source = getasenderratebook
      )
       html_content = f"""
        <html>
            <body>
                <div id="Pformtext2" style="margin:380px auto 0 auto;text-align-last:center;max-width:680px;width: 100%;">
                <label class="labb2"><h1 style="color:#268dfb;">Your Message Has Been Sent.</h1></label>
                <hr>
                <h2>Advertising Rate Book Form Submission.</h2>
                <h3>
                <p>Thank you for reaching out to us.<br> We will get back to you as soon as possible.</p>
                </h3>
                <hr>
                <h2>Download {sanitized_location} Advertising Rate Book.</h2>
                <a style="display: block;background-color: #0472E3;border: none;border-radius: 4px;color: #fff;margin:10px auto;text-decoration: none;text-align: center;min-width: 50px;max-width: 350px;width: 100%;padding: 15px;" href="https://help.stripes.com/submission_forms/advertising_rate_book/{sanitized_location}-advertising-rate-book.pdf"  download >Advertising Rate Book List Download</a><br>
                </div>
            </body> 
        </html>  
      """
       return {
            'statusCode': 200,
            'headers': {
            'Content-Type': 'text/html'
               },
            'body': html_content
            }