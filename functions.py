import os
import json
import hashlib
import requests
import boto3
import botocore


def handler(event):
    """
    Lambda handler for the RequestGeneratorLambda function.

    Validates the request event object and retrieves Oauth tokens from Secrets Manager.
    Attempts to generates a PD incident, refreshes the PD token if expired and retries.
    Logs event object to Dynamo.
    """ 

    # Debug print request event
    print("Request Event:", event)

    # Validate request event fields
    event_obj = validate_request_event(event)

    # Get oauth token secret
    secret_name = os.environ['SECRET_NAME']
    sm_client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    secret_str = response['SecretString']

    # Convert to dict
    secret_json = json.loads(secret_str)
    oauth_access_token = secret_json["PDOAuthAccessToken"]
    oauth_client_id = secret_json["PDOAuthAccessToken"]
    oauth_secret = secret_json["PDOAuthAccessToken"]

    # attempt to create pd incident & log to dynamodb

    # create pd incident

    response = create_pd_incident(event_obj, oauth_access_token)
    if response.status_code == 401:
        # invalid token
        print("Woops, unauthorized. Refreshing token...")
        # refresh token
        token = refresh_oauth_token(oauth_client_id, oauth_secret)
        # try again
        response = create_pd_incident(event_obj, token)
    # valid token
    # TODO
    # save to dynamodb
    
    # log to dynamodb, attempt to create pd incident
    # refresh oauth token then try again if token is invalid
    # create PD incident, log to dynamodb

def refresh_oauth_token(client_id, client_secret):
    """
    Params:
    client_id: string
    client_secret: string

    get oauth refresh tokens from passed secret object
    refresh oauth token
    update the value
    return the token
    """

    url = "https://identity.pagerduty.com/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "as_account-us.railing-ai incidents.read incidents.write"
    }

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    
    # parse out the oauth access token
    data = response.json()
    access_token = data.get('access_token')

    # update the secrets manager payload with the new access token
    updated_secret = {
          "PDOAuthClientID": client_id,
          "PDOAuthClientSecret": client_secret,
          "PDOAuthAccessToken": access_token
        }

    # TODO: uncomment
    #client = boto3.client('secretsmanager', region_name=region_name)
    try:
        # save the uploaded payload to Secrets Manager
    #    response = client.update_secret(SecretId=secret_name, SecretString=updated_secret)
        # return the refreshed token
        return access_token
    except botocore.exceptions.ClientError as e:
        print(e)
    
    
def create_pd_incident(event_obj, oauth_secret):
    """
    Attempt to create a PD Incident
    """

    # Retrieve service ID & from email
    service_id = os.environ['PD_SERVICE_ID']
    pd_from_email = os.environ['PD_FROM_EMAIL']
    
    url = "https://api.pagerduty.com/incidents"

    payload = { "incident": {
            "type": "incident",
            "title": event_obj["title"],
            "service": {
                "id": service_id,
                "type": "service_reference"
            },
            "urgency": "high",
            "body": {
                "type": "incident_body",
                "details": event_obj["summary"]
            },
            "escalation_policy": {
                "id": "P042MBS",
                "type": "escalation_policy_reference"
            }
        } }
        
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "From": pd_from_email,
        "Authorization": f"Bearer {oauth_secret}"
    }

    response = requests.post(url, json=payload, headers=headers)

    # Immediately raise 400 client errors
    if response.status_code == 400:
        print("400 Client Error Occurred:", response.text)
        response.raise_for_status()    
    return response

def validate_request_event(request_event):
    # Parse request event
    message_body = event["Records"][0]["body"]
    message_body_parsed = json.loads(message_body)
    message_parsed = json.loads(message_body_parsed["Message"])

    try:
        title = message_parsed["title"]
        summary = message_parsed["summary"]
        context = message_parsed["long_context"]
    except KeyError:
        raise KeyError("Cannot process message - improper format")

    return {
        "title": title,
        "summary": summary,
        "context": context
    }

def log_request(title, summary, context):
    """
    Log request to DynamoDB
    """
    # Step 1: Generate current timestamp
    request_time = datetime.datetime.now().isoformat()

    # Step 2: Concatenate the data to create a unique string
    concatenated_data = request_time + title + summary + context

    # Step 3: Create a hash of the concatenated data
    hash_id = hashlib.sha256(concatenated_data.encode()).hexdigest()

    # DynamoDB client
    ddb_client = boto3.client('dynamodb')

    # Step 4: Put the item into DynamoDB
    response = ddb_client.put_item(
        TableName='YourTableName',  # Replace with your table name
        Item={
            'id': {'S': hash_id},
            'title': {'S': title},
            'summary': {'S': summary},
            'context': {'S': context},
            'request_time': {'S': request_time}
        }
    )

    return response

def action_handler(event):
    # TODO
    # this is the lambda triggered by the incoming webhook - make it do something
    # needs the context fields to operate - a dict of some sort with the action item?
    # e.g. action_item, action_context?
    pass

if __name__ == "__main__":

    oauth_access_token = os.environ['ACCESS_TOKEN']
    client_id = os.environ['CLIENT_ID']
    client_secret = os.environ['CLIENT_SECRET']

    event_obj = {
        "title": "Approve IAM role dev-org-master?",
        "summary": "Chuck is requesting dev-org-master",
        "context": "dev-org-master is used for admin stuff. This user has used this role never before."
    }

    # Test the behavior of creating an incident and refreshing the token if needed
    response = create_pd_incident(event_obj, oauth_access_token)

    if response.status_code == 401:
        print("Woops, unauthorized. Trying again...")
        token = refresh_oauth_token(client_id, client_secret)
        print("Refresh token:", token)
        # Try again
        create_incident_response = create_pd_incident(event_obj, token)
        create_incident_response.raise_for_status()
        print(response)