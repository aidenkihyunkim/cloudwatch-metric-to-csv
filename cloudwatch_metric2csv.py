# -*- coding: utf-8 -*-
##############################################
# Export CloudWatch metric data to csv file
# Author: Aiden Kim
# 2020-11-19
##############################################

from datetime import timedelta, timezone, datetime
import argparse
import dateutil
import boto3
import re
import csv
import config


# parse argument
parser = argparse.ArgumentParser()
parser.add_argument("--name", help="""
	The Name tag of EC2 or name of RDS or name of ALB.
	This name allow multiple inputs separated by a comma.""")
parser.add_argument("--metric", help="""
	The name of the CloudWatch metric.""")
parser.add_argument("--period", help="""
	The granularity, in seconds, of the returned data points.
	A period can be as short as one minute (60 seconds) and must be a multiple of 60. 
	The default value is 3600.""")
parser.add_argument("--start", help="""
	The timestamp that determines the first data point to return.
	This timestamp must be in ISO 8601 UTC format.
	Default is 24 hours ago.""")
parser.add_argument("--end", help="""
	The timestamp that determines the last data point to return.
	This timestamp must be in ISO 8601 UTC format.
	Default is now.""")
parser.add_argument("--statistics", help="""
	The metric statistics.
	Default is Average.""")
parser.add_argument("--file", help="""
	The name of the output csv file. 
	Default is '[METRIC].csv'.""")
args = parser.parse_args()

# check if parameter is valid
metrics = dict((k.lower(), {'metric': k, 'namespace': v}) for k,v in config.METRICS.items())
allowed_statistics = ['SampleCount', 'Average', 'Sum', 'Minimum', 'Maximum']
if (not args.metric) or (args.metric.lower() not in metrics.keys()):
	print('Invalid --metric {} provided. Valid metrics: {}'.format(args.metric, list(metrics.keys())))
	exit(-1)
if (not args.name):
	print('Invalid --name {} provided.'.format(args.name))
	exit(-2)
if (args.statistics) and (args.statistics not in allowed_statistics):
	print('Invalid --statistics {} provided. Valid statistics: {}'.format(args.statistics, allowed_statistics))
	exit(-3)

# extract parameters
names = args.name.split(',')
metric = args.metric.lower()
period = int(args.period) if args.period else 3600
start = dateutil.parser.parse(args.start).astimezone(timezone.utc) if args.start else datetime.utcnow() - timedelta(days=1)
end = dateutil.parser.parse(args.end).astimezone(timezone.utc) if args.end else datetime.utcnow()
statistics = args.statistics if args.statistics else 'Average'
file = args.file if args.file else '{}.csv'.format(metrics[metric]['metric'])

# get metric datas
datas = []
cw = boto3.client('cloudwatch')
if ('AWS/EC2' in metrics[metric]['namespace']):
	ec2 = boto3.client('ec2')
	for name in names:
		ec2_res = ec2.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [name]}])
		if ec2_res and ('Reservations' in ec2_res) and (len(ec2_res['Reservations'])>0) and ('Instances' in ec2_res['Reservations'][0]) and (len(ec2_res['Reservations'][0]['Instances'])>0):
			for instance in ec2_res['Reservations'][0]['Instances']:
				cw_stats = cw.get_metric_statistics(
					StartTime=start, EndTime=end, Period=period, Statistics=[statistics],
					Namespace='AWS/EC2', MetricName=metrics[metric]['metric'],
					Dimensions=[{'Name': 'InstanceId', 'Value': instance['InstanceId']}],
				)
				if ('Label' in cw_stats) and ('Datapoints' in cw_stats) and (len(cw_stats['Datapoints'])>0):
					cw_stats['Label'] = '{}@{}'.format(cw_stats['Label'], name)
					datas.append(cw_stats)
if ('AWS/RDS' in metrics[metric]['namespace']):
	for name in names:
		cw_stats = cw.get_metric_statistics(
			StartTime=start, EndTime=end, Period=period, Statistics=[statistics],
			Namespace='AWS/RDS', MetricName=metrics[metric]['metric'],
			Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': name}],
		)
		if ('Label' in cw_stats) and ('Datapoints' in cw_stats) and (len(cw_stats['Datapoints'])>0):
			cw_stats['Label'] = '{}@{}'.format(cw_stats['Label'], name)
			datas.append(cw_stats)
if ('AWS/ApplicationELB' in metrics[metric]['namespace']):
	elb2 = boto3.client('elbv2')
	for name in names:
		elb2_res = elb2.describe_load_balancers(Names=[name])
		if elb2_res and ('LoadBalancers' in elb2_res) and (len(elb2_res['LoadBalancers'])>0):
			for elb in elb2_res['LoadBalancers']:
				cw_stats = cw.get_metric_statistics(
					StartTime=start, EndTime=end, Period=period, Statistics=[statistics],
					Namespace='AWS/ApplicationELB', MetricName=metrics[metric]['metric'],
					Dimensions=[{'Name': 'LoadBalancer', 'Value': re.sub('arn:.+:loadbalancer/', '', elb['LoadBalancerArn'])}],
				)
				if ('Label' in cw_stats) and ('Datapoints' in cw_stats) and (len(cw_stats['Datapoints'])>0):
					cw_stats['Label'] = '{}@{}'.format(cw_stats['Label'], name)
					datas.append(cw_stats)

# merge datas to one sheet
sheet = {}
for data in datas:
	for item in data['Datapoints']:
		timestr = item['Timestamp'].strftime('%Y-%m-%d %H:%M:%SZ')
		label = '{} ({})'.format(data['Label'], item['Unit'])
		if (timestr in sheet):
			sheet[timestr][label] = item[statistics]
		else:
			sheet[timestr] = { label: item[statistics] }
#print(sorted(sheet.items()))
if (len(sheet.keys()) == 0):
	print('No metric data found.')
	exit(-9)

# write csv file
with open(file, 'w', newline='') as csvfile:
	csvwriter = csv.writer(
		csvfile,
		delimiter=',',
		quotechar='"',
		quoting=csv.QUOTE_MINIMAL)
	for i, (k, v) in enumerate(sorted(sheet.items())):
		if (i == 0) :
			csvwriter.writerow( ['Time'] + sorted(v.keys()) )
		csvwriter.writerow([k] + [v[key] for key in sorted(v.keys())])

print('{} rows were written on the file {}'.format(len(sheet.keys()), file))

exit(0);
