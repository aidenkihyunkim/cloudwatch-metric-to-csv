# cloudwatch-metric-to-csv

**cloudwatch-metric-to-csv** is a Python3 utility to extract CloudWatch metric data from AWS resources (EC2, RDS and ALB).

## Features
- Extract metric data from EC2 instances
- Extract metric data from RDS instances
- Extract metric data from AppicationELB (ALB)
- Support to output datas of multiple instance
- Save output to csv file


## Installation

1. This application requires Python 3.6 or above. 
https://www.python.org/downloads/.

1. Clone the project
```console
git clone https://github.com/aidenkihyunkim/cloudwatch-metric-to-csv.git
```

1. Install packages
```console
pip install py-dateutil boto3 awscli
```

1. Configure the [AWS CLI](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html) If you haven't used it before
```console
aws configure
```


## Usage

- For usage help run:
```console
python cloudwatch_metric2csv.py -h
```

- To extract EC2 CPU utilization metric, run:
```console
python cloudwatch_metric2csv.py --name EC2NAME_TAG,EC2NAME_TAG[,...] --metric CPUUtilization
```

- To extract RDS Database connections metric, run:
```console
python cloudwatch_metric2csv.py --name RDS_NAME[,...] --metric DatabaseConnections
```

- To extract ALB Request count metric, run:
```console
python cloudwatch_metric2csv.py --name ALB_NAME[,...] --metric RequestCount
```

- If you want to set AWS Profile/Region/ACCES KEY manually, use environment variables of boto3
[Boto3 Docs : Using environment variables](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html)


## References
- [Metrics of EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/viewing_metrics_with_cloudwatch.html)
- [Metrics of RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/MonitoringOverview.html)
- [Metrics of ALB](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-cloudwatch-metrics.html)


## License

MIT License (MIT)
