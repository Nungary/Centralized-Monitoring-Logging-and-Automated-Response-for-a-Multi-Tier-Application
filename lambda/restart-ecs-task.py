import json
import boto3

ecs = boto3.client('ecs')
sns = boto3.client('sns')

def lambda_handler(event, context):
    cluster = 'capstone-7-app-cluster'
    service = 'capstone-7-app-service'
    
    try:
        # Get current tasks
        tasks = ecs.list_tasks(cluster=cluster, serviceName=service)
        
        if tasks['taskArns']:
            # Stop one task to force restart
            task_arn = tasks['taskArns'][0]
            ecs.stop_task(cluster=cluster, task=task_arn, reason='Auto-remediation: High CPU detected')
            
            message = f"Restarted ECS task {task_arn} due to high CPU"
            print(message)
            
            # Send notification
            sns.publish(
                TopicArn='arn:aws:sns:eu-west-1:430287290736:capstone-7-alarm-notifications',
                Subject='ECS Task Restarted',
                Message=message
            )
            
            return {'statusCode': 200, 'body': json.dumps(message)}
        else:
            return {'statusCode': 200, 'body': 'No tasks to restart'}
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps(f'Error: {str(e)}')}
