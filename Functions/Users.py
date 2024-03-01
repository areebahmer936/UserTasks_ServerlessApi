import json
import boto3
from uuid import uuid4

def respond(statusCode, type, content):
    return {
        "statusCode":statusCode,
        "body":json.dumps({type:content})
    }
        
    
def createUser(event, context):
    # TODO implement
    body = json.loads(event["body"])
    userName = body.get("UserName")
    userId = str(uuid4())
    
    
    if not userName:
        return respond(400, "error", "Invalid Parameters")        
    
    dynamoDb = boto3.resource("dynamodb")
    table= dynamoDb.Table("Users")

    response = table.get_item(Key={"UserId":userId})
    if "Item" in response:
        return respond(409, "error", "User already exists.")

    else:
        try:
            table.put_item(Item={"UserId":userId, "UserName":userName, "IsDeleted":False})
            return respond(201, "message", f'User created with id:{userId}, name:{userName}')
 
        except Exception as e:
            return respond(501, "error", str(e))


def deleteUser(event, context):
    # TODO implement
    userId = event['pathParameters']['UserId']

    dynamoDb = boto3.resource("dynamodb")
    table= dynamoDb.Table("Users")

    response = table.get_item(Key={"UserId":userId})
    if "Item" in response:
        table.update_item(Key={"UserId":userId},
        UpdateExpression="SET IsDeleted = :status",
        ExpressionAttributeValues={":status": True},
        ReturnValues="UPDATED_NEW"  )
        
        return respond(200, "message",f'User {userId} - {response["Item"]["UserName"]} deleted')

    else:
        return respond(404, "error",f"User doesn't exist" )


def getUser(event, context):
    # TODO implement
    userId = event['pathParameters']['UserId']
    
    dynamoDb = boto3.resource("dynamodb")
    table= dynamoDb.Table("Users")

    try:
        if not userId:
            response = table.scan()
            allUsers = response.get("Items", [])
            if allUsers:
                return respond(200, "data", allUsers)
            else:
                return respond(404, "error", "No Users found")
            
        else:
            response = table.get_item(Key={"UserId":userId})
            if "Item" in response:                
                return respond(200, "data", response["Item"])

            else:
                return respond(404, "error", "User not found")
                
    except Exception as e:
        return respond(501, "error", str(e))
        

def updateUser(event, context):
    # TODO implement
    body = json.loads(event['body'])
    userName = body.get("UserName")
    userId = event['pathParameters']['UserId']
    if not userName:
        return respond(400, "error", "Invalid parameters")
    
    dynamoDb = boto3.resource("dynamodb")
    table= dynamoDb.Table("Users")
    try: 
        response = table.get_item(Key={"UserId":userId})
        if "Item" in response:
            table.update_item(Key={"UserId": userId},
            UpdateExpression="SET UserName = :userName",
            ExpressionAttributeValues={":userName": userName},
            ReturnValues="UPDATED_NEW")
            
            return respond(200, "message", "Successfully Updated")
            
        else:
            return respond(404, "error", "User not found.")
    except Exception as e:
        return respond(501, "error", str(e))