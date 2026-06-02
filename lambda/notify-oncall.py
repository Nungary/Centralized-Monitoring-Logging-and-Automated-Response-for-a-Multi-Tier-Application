import json
import boto3
from datetime import datetime

sns = boto3.client('sns')

def lambda_handler(event, context):
    try:
        # Parse the alarm from SNS message
        message = json.loads(event['Records'][0]['Sns']['Message'])
        alarm_name = message.get('AlarmName', 'Unknown')
        new_state = message.get('NewStateValue', 'Unknown')
        reason = message.get('NewStateReason', 'No reason provided')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create detailed notification
        notification = f"""
🚨 ALERT: CloudWatch Alarm Triggered

Alarm: {alarm_name}
Status: {new_state}
Time: {timestamp}
Reason: {reason}

Action Required: Please investigate immediately.
        """
        
        # Send to SNS
        response = sns.publish(
            TopicArn='arn:aws:sns:eu-west-1:430287290736:capstone-7-alarm-notifications',
            Subject=f'🚨 ALERT: {alarm_name}',
            Message=notification
        )
        
        print(f"Notification sent for alarm: {alarm_name}")
        return {'statusCode': 200, 'body': json.dumps('Notification sent')}
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps(f'Error: {str(e)}')}
