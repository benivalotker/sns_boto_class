#/path/path/
#title           :AWS SNS Class
#description     :AWS SNS services.
#update date     :01/01/2020 12:10
#version         :1.0
#changes         :veriosn 1.0.
#python_version  :3.6  
#==============================================================================

import boto3
import datetime
import json


class Sns():
	# constructor
	def __init__(self, sns_topic_name):
		self.__sns = boto3.client('sns')

		try:
			self.sns_topic_name = sns_topic_name
			self.topic_arn = self.__sns.create_topic(Name = sns_topic_name).get('TopicArn')
		except:
			raise Exception("topic doesn't exist")
		

	# getter and setter of new topic
	@property
	def topic(self):
		return self.__topic_arn

	@topic.setter
	def topic(self, new_topic):
		try:
			self.__sns.get_topic_attributes(TopicArn=new_topic)
			self.__topic_arn = new_topic
		except:
			raise Exception("topic doesn't exist")

		return True
			

	# Publish a message to the specified SNS topic
	def publish_to_topic(self, message):
		try:
			response = self.__sns.publish(
					TopicArn=self.__topic_arn,    
					Message=message,    
				)
		except Exception as ex:
			raise ex
		
		return response


	# create messages and publish it (can be modify)
	def send_error_notification(self, exception, context, event=None):	
		# error detalis (can be modify)
		error_time = datetime.datetime.utcnow()
		error_text = str(exception)
		lambda_name = context.function_name
		request_id = context.aws_request_id
		lambda_region = boto3.session.Session().region_name
		log_group = context.log_group_name
		log_stream = context.log_stream_name
		oid = None

		log_url = 'https://eu-west-1.console.aws.amazon.com/cloudwatch/home?region=' + str(lambda_region) + '#logEventViewer:group=' + str(log_group) + ';stream=' + str(log_stream)
		

		# message template (can be modify)
		message_body = '\n'.join([
				'Lambda "' + lambda_name + '" has failed.' ,
				'' ,
				'Error Time: ' + str(error_time) ,
				'' ,
				'Error Text: "' + str(error_text) + '"' ,
				'' ,
				'Request Id: ' + str(request_id) ,
				'' ,
				'AWS Log: ' + log_url,
				'' ,
				"Log OID : " + str(oid),
				'',
				"Event: " + str(event)
			])
		
		self.__sns.publish(
			TopicArn = self.topic_arn ,
			Subject = lambda_name + ' - Failure Alert' ,
			Message = message_body
		)
