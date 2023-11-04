import json
import boto3

def get_ec2_matches(region, os, vcpu, memory):
    '''
    Set the filters for EC2s by region, os, vcpu and memory. The following is a subset of the total available options.
    For further filters set the aws documentation @ https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_pricing_PriceList.html
    '''
    FLT = '[' 
    FLT = FLT + '{{"Field": "memory", "Value": "{m} GiB", "Type": "TERM_MATCH"}},'
    FLT = FLT + '{{"Field": "vcpu", "Value": "{c}", "Type": "TERM_MATCH"}},'
    FLT = FLT + '{{"Field": "tenancy", "Value": "shared", "Type": "TERM_MATCH"}},'
    FLT = FLT + '{{"Field": "operatingSystem", "Value": "{o}", "Type": "TERM_MATCH"}},'
    FLT = FLT + '{{"Field": "preInstalledSw", "Value": "NA", "Type": "TERM_MATCH"}},'
    FLT = FLT + '{{"Field": "regionCode", "Value": "{r}", "Type": "TERM_MATCH"}},'
    FLT = FLT + '{{"Field": "licenseModel", "Value": "No License required", "Type": "TERM_MATCH"}},'
    FLT = FLT + '{{"Field": "storage", "Value": "EBS only", "Type": "TERM_MATCH"}},'
    FLT = FLT + '{{"Field": "location", "Value": "US East (N. Virginia)", "Type": "TERM_MATCH"}},'
    FLT = FLT + '{{"Field": "capacitystatus", "Value": "Used", "Type": "TERM_MATCH"}}'
    FLT = FLT + ']'

    # Set the region. Available filters may be region dependent.
    client = boto3.client('pricing', region_name=region)

    # Set the filer variables with parameter values.
    f = FLT.format(r=region, o=os, c=vcpu, m=memory)
    
    # Retrive matching Amazon EC2 instances based on filters.
    data = client.get_products(ServiceCode='AmazonEC2', Filters=json.loads(f))
    
    # Reduce the total results by those instances avaiable for 3 Year, No Upfront, Standard pricing.
    results = []
    i = 0
    rec_length = len(data['PriceList'])
    print(rec_length)
    while i < rec_length:
        #For each record, attempts to retrieve instance types where reserved pricing is available, else catch the exception and log as on-demand pricing only.
        filter_results = json.loads(data['PriceList'][i])
        try:
            three_year_reserve = filter_results['terms']['Reserved']
            for rec in three_year_reserve:
                # Due to SKU identities changing for the same EC2 type, id1 cpatures the entire structure as an identifier. 
                # See product-example.json for an example of the full json structure of the data results.
                id1 = rec
                upfront = three_year_reserve[id1]['termAttributes']['PurchaseOption']
                contractLength = three_year_reserve[id1]['termAttributes']['LeaseContractLength']
                offeringClass = three_year_reserve[id1]['termAttributes']['OfferingClass']
                if upfront == "No Upfront" and contractLength == "3yr" and offeringClass == "standard":
                    results.append({"instance-type": filter_results['product']['attributes']['instanceType'], "rate-type": "NUF3YIR"}) 
    
        except KeyError as ke:
            results.append({"instance-type": filter_results['product']['attributes']['instanceType'], "rate-type": "ON-DEMAND ONLY"}) 
        i = i + 1
    print(results)
    return results

def get_ec2_3yr_mrr(region, os, instance_type):
    '''
    Set the filters for EC2s by region, os and instance-type. The following is a subset of the total available options.
    For further filters set the aws documentation @ https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_pricing_PriceList.html
    '''
    FLT = '[{{"Field": "instanceType", "Value": "{t}", "Type": "TERM_MATCH"}},'
    FLT = FLT + '{{"Field": "tenancy", "Value": "shared", "Type": "TERM_MATCH"}},'
    FLT = FLT + '{{"Field": "operatingSystem", "Value": "{o}", "Type": "TERM_MATCH"}},'
    FLT = FLT + '{{"Field": "preInstalledSw", "Value": "NA", "Type": "TERM_MATCH"}},'
    FLT = FLT + '{{"Field": "regionCode", "Value": "{r}", "Type": "TERM_MATCH"}},'
    FLT = FLT + '{{"Field": "licenseModel", "Value": "No License required", "Type": "TERM_MATCH"}},'
    FLT = FLT + '{{"Field": "storage", "Value": "EBS only", "Type": "TERM_MATCH"}},'
    FLT = FLT + '{{"Field": "location", "Value": "US East (N. Virginia)", "Type": "TERM_MATCH"}},'
    FLT = FLT + '{{"Field": "capacitystatus", "Value": "Used", "Type": "TERM_MATCH"}}'
    FLT = FLT + ']'
    
    # Set the region. Available filters may be region dependent.
    client = boto3.client('pricing', region_name=region)

    # Set the filer variables with parameter values.
    f = FLT.format(r=region, o=os, t=instance_type)
    
    # Retrive matching Amazon EC2 instances based on filters.
    data = client.get_products(ServiceCode='AmazonEC2', Filters=json.loads(f))
    
    results = ""
    try:
        filter_results = json.loads(data['PriceList'][0])['terms']['Reserved']
        for rec in filter_results:
            # Due to SKU identities changing for the same EC2 type, id1 and id2 cpature the entire structure as an identifier. 
            # See product-example.json for an example of the full json structure of the data results.
            id1 = rec
            id2 = list(filter_results[id1]['priceDimensions'])[0]
            upfront = filter_results[id1]['termAttributes']['PurchaseOption']
            contractLength = filter_results[id1]['termAttributes']['LeaseContractLength']
            offeringClass = filter_results[id1]['termAttributes']['OfferingClass']
            if upfront == "No Upfront" and contractLength == "3yr" and offeringClass == "standard":
                results = filter_results[id1]['priceDimensions'][id2]['pricePerUnit']['USD']
    except KeyError as ke:
        filter_results = json.loads(data['PriceList'][0])['terms']['OnDemand']
        for rec in filter_results:
            id1 = rec
            id2 = list(filter_results[id1]['priceDimensions'])[0]
            upfront = filter_results[id1]['termAttributes']['PurchaseOption']
            contractLength = filter_results[id1]['termAttributes']['LeaseContractLength']
            offeringClass = filter_results[id1]['termAttributes']['OfferingClass']
            if upfront == "No Upfront" and contractLength == "3yr" and offeringClass == "standard":
                results = filter_results[id1]['priceDimensions'][id2]['pricePerUnit']['USD']
    return results

def lambda_handler(event, context):
    # Capture the inputs from the raw post data as local variables.
    print(event)
    body = json.loads(event['body'])
    region = body['region']
    os = body['os']
    vcpu = body['vcpu']
    memory = body['memory']
    
    # Set the placeholders for EC2 matches and corresponding JSON response.
    ec2_results = []
    json_response = []
    
    try:
        ec2_results = get_ec2_matches(region, os, vcpu, memory)
        print(len(ec2_results))
        i = 0
        while i < len(ec2_results):
            json_response.append({'instance-type': ec2_results[i]['instance-type'], 'monthly-rate': 730*float(get_ec2_3yr_mrr(region, os, ec2_results[i]['instance-type']))})
            i = i + 1
    except Exception as e:
        print(e)

    
    return {
        'statusCode': 200,
        'body': json.dumps(json_response)
    }
