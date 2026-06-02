import json
import boto3
from datetime import datetime

ec2 = boto3.client('ec2')
sns = boto3.client('sns')

def lambda_handler(event, context):
    try:
        # Get all running EC2 instances with capstone-7-web tag
        response = ec2.describe_instances(
            Filters=[
                {'Name': 'tag:Name', 'Values': ['capstone-7-web-*']},
                {'Name': 'instance-state-name', 'Values': ['running']}
            ]
        )
        
        tagged_instances = []
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                
                # Add investigation tag
                ec2.create_tags(
                    Resources=[instance_id],
                    Tags=[
                        {'Key': 'Status', 'Value': 'INVESTIGATE'},
                        {'Key': 'AlertTime', 'Value': timestamp},
                        {'Key': 'Reason', 'Value': 'High error count detected'}
                    ]
                )
                tagged_instances.append(instance_id)
                print(f"Tagged instance {instance_id} for investigation")
        
        # Send notification
        message = f"Tagged {len(tagged_instances)} EC2 instances for investigation: {', '.join(tagged_instances)}"
        sns.publish(
            TopicArn='arn:aws:sns:eu-west-1:430287290736:capstone-7-alarm-notifications',
            Subject='EC2 Instances Tagged for Investigation',
            Message=message
        )
        
        return {'statusCode': 200, 'body': json.dumps(message)}
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps(f'Error: {str(e)}')}
