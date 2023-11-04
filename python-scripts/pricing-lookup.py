import boto3
import sys
import json
import os

## print(os.environ['PATH'])

argumentList = sys.argv[1:]

# Translate region code to region name. 
def get_region_name(region_code):
    default_region = 'US East (N. Virginia)'
    endpoint_file = resource_filename('botocore', 'data/endpoints.json')
    try:
        with open(endpoint_file, 'r') as f:
            data = json.load(f)
        return data['partitions'][0]['regions'][region_code]['description'].replace('Europe', 'EU')
    except IOError:
        return default_region

# Filters
"""
Field types
-----------
servicecode
snapshotarchivefeetype 
instanceFamily
instance
instanceCapacityMedium
instanceCapacityLarge
instanceCapacityXlarge
instanceCapacity2xlarge
instanceCapacity4xlarge
instanceCapacity8xlarge
instanceCapacity9xlarge
instanceCapacity10xlarge
instanceCapacity12xlarge
instanceCapacity16xlarge
instanceCapacity18xlarge
instanceCapacity24xlarge
instanceCapacity32xlarge
instanceCapacityMetal
"""
## {{"Field": "storage", "Value": "", "Type": "TERM_MATCH"}},{{"Field": "volumeType", "Value": "", "Type": "TERM_MATCH"}},{{"Field": "PurchaseOption", "Value": "No Upfront", "Type": "TERM_MATCH"}},{{"Field": "OfferingClass", "Value": "standard", "Type": "TERM_MATCH"}},{{"Field": "LeaseContractLength", "Value": "3yr", "Type": "TERM_MATCH"}}
## currentGeneration - Returns empty set
## {{"Field": "memory", "Value": "{m}", "Type": "TERM_MATCH"}},{{"Field": "vcpu", "Value": "{c}", "Type": "TERM_MATCH"}}
##FLT = '[{{"Field": "instanceType", "Value": "{it}", "Type": "TERM_MATCH"}},{{"Field": "tenancy", "Value": "shared", "Type": "TERM_MATCH"}},{{"Field": "operatingSystem", "Value": "{o}", "Type": "TERM_MATCH"}},{{"Field": "preInstalledSw", "Value": "NA", "Type": "TERM_MATCH"}},{{"Field": "regionCode", "Value": "{r}", "Type": "TERM_MATCH"}},{{"Field": "capacitystatus", "Value": "Used", "Type": "TERM_MATCH"}}]'
FLT = '[{{"Field": "instanceType", "Value": "{t}", "Type": "TERM_MATCH"}},'\
    '{{"Field": "tenancy", "Value": "shared", "Type": "TERM_MATCH"}},'\
    '{{"Field": "operatingSystem", "Value": "{o}", "Type": "TERM_MATCH"}},'\
    '{{"Field": "preInstalledSw", "Value": "NA", "Type": "TERM_MATCH"}},'\
    '{{"Field": "regionCode", "Value": "{r}", "Type": "TERM_MATCH"}},'\
    '{{"Field": "licenseModel", "Value": "No License required", "Type": "TERM_MATCH"}},'\
    '{{"Field": "storage", "Value": "EBS only", "Type": "TERM_MATCH"}},'\
    '{{"Field": "location", "Value": "US East (N. Virginia)", "Type": "TERM_MATCH"}},'\
    '{{"Field": "capacitystatus", "Value": "Used", "Type": "TERM_MATCH"}}]'


# Need to check other regions
client = boto3.client('pricing', region_name='us-east-1')

region = argumentList[0]
os = argumentList[1]
instanceType = argumentList[2]
results = ""

#c=vcpu, m=memory, 
f = FLT.format(r=region, o=os, t=instanceType)
data = client.get_products(ServiceCode='AmazonEC2', Filters=json.loads(f))
print(data)
try:
    od = json.loads(data['PriceList'][0])['terms']['Reserved']
    for rec in od:
        id1 = rec
        id2 = list(od[id1]['priceDimensions'])[0]
        upfront = od[id1]['termAttributes']['PurchaseOption']
        contractLength = od[id1]['termAttributes']['LeaseContractLength']
        offeringClass = od[id1]['termAttributes']['OfferingClass']
        if upfront == "No Upfront" and contractLength == "3yr" and offeringClass == "standard":
            results = results + od[id1]['priceDimensions'][id2]['pricePerUnit']['USD']
except KeyError as ke:
    od = json.loads(data['PriceList'][0])['terms']['OnDemand']
    for rec in od:
        id1 = rec
        id2 = list(od[id1]['priceDimensions'])[0]
        upfront = od[id1]['termAttributes']['PurchaseOption']
        contractLength = od[id1]['termAttributes']['LeaseContractLength']
        offeringClass = od[id1]['termAttributes']['OfferingClass']
        if upfront == "No Upfront" and contractLength == "3yr" and offeringClass == "standard":
            results = results + od[id1]['priceDimensions'][id2]['pricePerUnit']['USD']

aws_region_map = {
    'ca-central-1': 'Canada (Central)',
    'ap-northeast-3': 'Asia Pacific (Osaka-Local)',
    'us-east-1': 'US East (N. Virginia)',
    'ap-northeast-2': 'Asia Pacific (Seoul)',
    'us-gov-west-1': 'AWS GovCloud (US)',
    'us-east-2': 'US East (Ohio)',
    'ap-northeast-1': 'Asia Pacific (Tokyo)',
    'ap-south-1': 'Asia Pacific (Mumbai)',
    'ap-southeast-2': 'Asia Pacific (Sydney)',
    'ap-southeast-1': 'Asia Pacific (Singapore)',
    'sa-east-1': 'South America (Sao Paulo)',
    'us-west-2': 'US West (Oregon)',
    'eu-west-1': 'EU (Ireland)',
    'eu-west-3': 'EU (Paris)',
    'eu-west-2': 'EU (London)',
    'us-west-1': 'US West (N. California)',
    'eu-central-1': 'EU (Frankfurt)'
    }

ebs_name_map = {
    'standard': 'Magnetic',
    'gp2': 'General Purpose',
    'gp3': 'General Purpose',
    'io1': 'Provisioned IOPS',
    'st1': 'Throughput Optimized HDD',
    'sc1': 'Cold HDD'
}
region = 'us-east-1'
resolved_region = aws_region_map[region]
aws_pricing_region = "us-east-1"
pricing_auth = boto3.client('pricing', region_name=aws_pricing_region)
for ebs_code in ebs_name_map:
    response = pricing_auth.get_products(ServiceCode='AmazonEC2', Filters=[
        {'Type': 'TERM_MATCH', 'Field': 'volumeType', 'Value': ebs_name_map[ebs_code]}, 
        {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': resolved_region}])
    for result in response['PriceList']:
        json_result = json.loads(result)
        for json_result_level_1 in json_result['terms']['OnDemand'].values():
            for json_result_level_2 in json_result_level_1['priceDimensions'].values():
                for price_value in json_result_level_2['pricePerUnit'].values():
                    ebs_name_map[ebs_code] = float(price_value)



ebs_pricing = client.get_products(ServiceCode="AmazonEC2", Filters=[{"Type": "TERM_MATCH","Field": "usagetype","Value": "USE2-EBS:SnapshotUsage"}])
#pricing_info = json.loads(ebs_pricing['PriceList'][0])
ss_GiB_mon_rate = 0
try:
    od = json.loads(ebs_pricing['PriceList'][0])['terms']['OnDemand']
    for rec in od:
        id1 = rec
        id2 = list(od[id1]['priceDimensions'])[0]
        ss_GiB_mon_rate = od[id1]['priceDimensions'][id2]['pricePerUnit']['USD'].replace('"', '')
except Exception as e:
    print(e)

#ss_key_value1 = (pricing_info['terms']['OnDemand']).values() 
#d1 = dict(ss_key_value1)
#print(d1)
#ss_GiB_mon_rate = ss_dict2['pricePerUnit']['USD']

#ss_GiB_mon_rate = (json.dumps(pricing_info['terms']['OnDemand']['EZ8T7N34G3H5Y4ER.JRTCKXETXF']['priceDimensions']['EZ8T7N34G3H5Y4ER.JRTCKXETXF.6YS6EN2CT7']['pricePerUnit']['USD'])).replace('"', '')
print("SnapShot GiB/Mo: " + ss_GiB_mon_rate)
print("EBS gp3 GiB/Mo: " + str(ebs_name_map['gp3']))
print("EC2 hourly rate for " + instanceType + ": " + results)

print('Monthly:')
ss_total = float(ss_GiB_mon_rate)*75
ebs_total = ebs_name_map['gp3']*50
ec2_total = float(results)*730
print("SnapShot 500Gib/Mon: " + str(ss_total))
print("EBS gp3 200GiB/Mo: " + str(ebs_total))
print("EC2 Monthly rate for " + instanceType + ": " + str(ec2_total))
print("Total monthly rate: " + str(ss_total+ebs_total+ec2_total))