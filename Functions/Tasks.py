import json
import boto3
from uuid import uuid4

def respond(statusCode, type, content):
    return {
        "statusCode":statusCode,
        "body":json.dumps({type:content})
        
    }

def createTask(event, context):
    # TODO implement
    body = json.loads(event["body"])
    userId = body.get("AssignedUserId")
    taskDesc = body.get("TaskDescription")
    taskId = str(uuid4())

    
    if not taskDesc or not userId:
        return respond(400, "error", "Invalid Parameters")
        
    
    dynamoDb = boto3.resource("dynamodb")
    userTable= dynamoDb.Table("Users")
    taskTable= dynamoDb.Table("Tasks")
    
    response = userTable.get_item(Key={"UserId":userId})
    taskResponse = taskTable.get_item(Key={"TaskId":taskId})
    
    if "Item" in taskResponse:
        return respond(409, "message", f"Task with id {taskId} already exist")

    else:    
        if "Item" in response:
            try :
                userTable.update_item(Key={"UserId": userId},
                UpdateExpression="SET TaskId = :taskId",
                ExpressionAttributeValues={":taskId": taskId},
                ReturnValues="UPDATED_NEW")
                
                taskTable.put_item(Item={"TaskId":taskId, "TaskDescription":taskDesc, "AssignedUserId":userId})
                
                return respond(200, "message",f'Task {taskId} assigned to {userId} - {response["Item"]["UserName"]}' )

            except Exception as e:
                return respond(501, "error", str(e))
        else:
            return respond(404, "error", "User doesn't exist" )


def getTask(event, context):
    # TODO implement
    taskId = event['pathParameters']['TaskId']
    dynamoDb = boto3.resource("dynamodb")
    table= dynamoDb.Table("Tasks")
    
    if not taskId:
        try: 
            response = table.scan()
            tasks = response.get("Items", [])
            if tasks:
                # Return the list of tasks
                return respond(200, "data", tasks)
            else:
                return respond(404, "error", "No tasks found")
        except Exception as e:
            return respond(501, "error", str(e))
        
    else:
        try:
            response = table.get_item(Key={"TaskId":taskId})
            if "Item" in response:
                return respond(200, "data", response["Item"])
            else:
                return respond(404, "error", "Task does not exist")
        except Exception as e:
            return respond(501, "error", str(e))


def updateTask(event, context):
    # TODO implement
    body = json.loads(event["body"])
    taskId =  event['pathParameters']['TaskId']
    userId = body.get("AssignedUserId")
    taskDescription = body.get("TaskDescription")


    
    if not taskDescription:
        return respond(400, "error", "Invalid Parameters")
    
    dynamoDb = boto3.resource("dynamodb")
    taskTable= dynamoDb.Table("Tasks")
    userTable= dynamoDb.Table("Users")

    response = taskTable.get_item(Key={"TaskId":taskId})
    if "Item" in response:
        if userId:
            previousUserId = response["Item"]["AssignedUserId"]
            try:
                if previousUserId != userId:
                    userTable.update_item(Key={"UserId":previousUserId},
                                                      UpdateExpression="REMOVE TaskId")

                    getNewUserResponse = userTable.get_item(Key={"UserId":userId})
                    if "Item" in getNewUserResponse:
                        userTable.update_item(Key={"UserId":userId},
                        UpdateExpression="SET TaskId = :taskId",
                        ExpressionAttributeValues={":taskId": taskId},)
                    else:
                        return respond(404, "error", "User not found")
                        
                    taskTable.update_item(Key={"TaskId": taskId},
                    UpdateExpression="SET TaskDescription = :taskDesc, AssignedUserId= :userId",
                    ExpressionAttributeValues={":taskDesc": taskDescription, ":userId":userId},
                    ReturnValues="UPDATED_NEW")
                    return respond(200, "message", "Task Updated")

                else:
                    taskTable.update_item(Key={"TaskId": taskId},
                        UpdateExpression="SET TaskDescription = :taskDesc",
                        ExpressionAttributeValues={":taskDesc": taskDescription},
                        ReturnValues="UPDATED_NEW")
                    
                return respond(200, "message", "Task Updated")
                            
            except Exception as e:
                return respond(501, "error", str(e))
             
        else:
            try: 
                taskTable.update_item(Key={"TaskId": taskId},
                        UpdateExpression="SET TaskDescription = :taskDesc",
                        ExpressionAttributeValues={":taskDesc": taskDescription},
                        ReturnValues="UPDATED_NEW")
                return respond(200, "message", "Task Updated")
            except Exception as e:
                return respond(501, "error", str(e))       
    else:
        return respond(404, "error", "Task not found")
        
def deleteTask(event, context):
    # TODO implement
    taskId = event['pathParameters']['TaskId']

    dynamoDb = boto3.resource("dynamodb")
    userTable = dynamoDb.Table("Users")
    taskTable = dynamoDb.Table("Tasks")
    
    try:
        response = taskTable.get_item(Key={"TaskId":taskId})
        if "Item" in response:
            userId = response["Item"]["AssignedUserId"]
            userTable.update_item(Key={"UserId":userId},
            UpdateExpression="REMOVE TaskId",
            ReturnValues="UPDATED_NEW")
            taskTable.delete_item(Key={"TaskId":taskId})
            
            return respond(200, "message", "Successfully deleted")
        else:
            return respond(404, "error", "Task not found")
            
    except Exception as e:
        return respond(501, "error", str(e))





