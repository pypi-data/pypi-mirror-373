import boto3
from tabulate import tabulate


class ECSManager:

    @classmethod
    def get_node_arn(cls, cluster, pattern=None, anti_pattern=None):
        taks_per_service = {}
        client = boto3.client('ecs')
        to_return = []
        for x in client.list_services(cluster=cluster, maxResults=100).get('serviceArns', []):
            if pattern:
                for c in pattern:
                    if c in x.lower():
                        to_return.append(x)
            elif anti_pattern:
                found_node = True
                for c in anti_pattern:
                    if c in x.lower():
                        found_node = False
                        continue
                if found_node:
                    to_return.append(x)
        return to_return

    @classmethod
    def start_service(cls, cluster, pattern=None, anti_pattern=None, nb_tasks=1):
        client = boto3.client('ecs')
        service_arns = cls.get_node_arn(cluster, pattern=pattern, anti_pattern=anti_pattern)
        for service_arn in service_arns:
            client.update_service(
                cluster=cluster,
                service=service_arn,
                desiredCount=nb_tasks
            )

    @classmethod
    def stop_service(cls, cluster, pattern=None, anti_pattern=None):
        client = boto3.client('ecs')
        service_arns = cls.get_node_arn(cluster, pattern=pattern, anti_pattern=anti_pattern)
        for service_arn in service_arns:
            client.update_service(
                cluster=cluster,
                service=service_arn,
                desiredCount=0
            )

    @classmethod
    def info_cluster(cls, cluster):
        client = boto3.client('ecs')
        services = sorted(client.list_services(cluster=cluster).get('serviceArns', []))
        describe_service = client.describe_services(cluster=cluster, services=services).get('services', [])
        display = [['Service Name', 'Nb desired', 'Nb running', 'Nb pending']]
        for service in describe_service:
            service_name = service['serviceName'].split('/')[-1]
            running_count = service['runningCount']
            pending_count = service['pendingCount']
            desired_count = service['desiredCount']
            display.append([service_name, desired_count, running_count, pending_count])
        print(tabulate(display[1:], headers=display[0]))

