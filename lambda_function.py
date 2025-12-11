import json
import os
import boto3

TABLE_NAME = os.getenv("EMP_TABLE", "Emp_Master")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def _response(status_code, body_dict):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body_dict)
    }


def lambda_handler(event, context):
    print("Event:", json.dumps(event))

    method = event.get("httpMethod") or \
             event.get("requestContext", {}).get("http", {}).get("method")

    raw_path = event.get("path") or event.get("rawPath", "/")

    if raw_path.endswith("/employee"):
        if method == "POST":
            return handle_post_employee(event)
        elif method == "GET":
            return handle_get_employee(event)

    return _response(404, {"message": "Not Found"})


def handle_post_employee(event):
    try:
        body = event.get("body") or "{}"
        if event.get("isBase64Encoded"):
            import base64
            body = base64.b64decode(body).decode("utf-8")

        data = json.loads(body)
        emp_id = data["Emp_Id"]
        first_name = data["First_Name"]
        last_name = data["Last_Name"]
        doj = data["Date_Of_Joining"]
    except Exception as e:
        print("Error parsing body:", e)
        return _response(400, {"error": "Invalid request body"})

    item = {
        "Emp_Id": emp_id,
        "First_Name": first_name,
        "Last_Name": last_name,
        "Date_Of_Joining": doj
    }

    table.put_item(Item=item)
    print("Inserted item:", item)

    return _response(201, {"message": "Employee created", "item": item})


def handle_get_employee(event):
    params = event.get("queryStringParameters") or {}
    emp_id = params.get("emp_id")

    if not emp_id:
        return _response(400, {"error": "emp_id query parameter is required"})

    resp = table.get_item(Key={"Emp_Id": emp_id})
    item = resp.get("Item")
    print("Fetched item:", item)

    if not item:
        return _response(404, {"error": "Employee not found"})

    return _response(200, {"item": item})
#dummy2
