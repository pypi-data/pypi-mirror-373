
class LightSailPostDeploy:


    #Get container service url from container service
    #update the dns record for each domain to that container service url

    def __init__(self, domains = [], container_service_name, region, profile="default"):
        self.domains = domains
        self.container_service_name = container_service_name
        self.region = region
        self.profile = profile
        self.container_service_url = self.get_container_service_url()

    def get_container_service_url(self):
        return LightsailPostDeploy.get_lightsail_domain_from_aws(
            self.container_service_name, self.region, self.profile
        )
    

    @static_method
    def static_execute(domain, container_service_name, region='ca-central-1', profile='default'):
        lightSailDeploy = LightsailPostDeploy(domains=[domain], 
                                              container_service_name=container_service_name, region=region, profile=profile)
        lightSailDeploy.execute()

    def execute(self):
        for domain in self.domains:
            self.update_dns_record(domain, self.container_service_url)

    @staticmethod
    def attach_cert_to_container(container_service_name, region, profile="default"):
        """
        Static method to attach SSL certificate to Lightsail container service.

        :param container_service_name: Name of the container service
        :type container_service_name: str
        :param region: AWS region where the service is deployed
        :type region: str
        :param profile: AWS profile to use (default: "default")
        :type profile: str
        """
        # Implementation for attaching SSL certificate goes here
        import LightSailDomainAttachWrapper
        lightsailWrapper = LightSailDomainAttachWrapper(container_service_name, region, profile)


    def update_dns_record(domain, container_service_url):
        print (f"Updating DNS record for {domain} to point to {container_service_url}")
        pass

    @staticmethod
    def get_lightsail_domain_from_aws(container_service_name, region, profile="default"):
        """
        Static method to retrieve Lightsail container service domain from AWS.
        
        This is a utility method that can be called independently to get the actual
        domain name from AWS Lightsail for a given container service.

        :param container_service_name: Name of the container service
        :type container_service_name: str
        :param region: AWS region where the service is deployed
        :type region: str
        :param profile: AWS profile to use (default: "default")
        :type profile: str
        :returns: The public domain URL ending with amazonlightsail.com
        :rtype: str

        Example:
            >>> domain = BBAWSLightsailMiniV1a.get_lightsail_domain_from_aws(
            ...     "my-app", "us-east-1", "my-profile"
            ... )
            >>> print(domain)  # my-app.us-east-1.cs.amazonlightsail.com
        """
        import boto3
        from botocore.exceptions import ClientError
        
        try:
            # Create a session with the specified profile
            session = boto3.Session(profile_name=profile)
            lightsail_client = session.client('lightsail', region_name=region)
            
            # Get container services
            response = lightsail_client.get_container_services()
            
            # Find our container service by name
            for service in response.get('containerServices', []):
                if service.get('containerServiceName') == container_service_name:
                    # Get the public domain endpoints
                    public_domain_names = service.get('publicDomainNames', {})
                    
                    # Look for the domain that ends with amazonlightsail.com
                    for domain_list in public_domain_names.values():
                        for domain in domain_list:
                            if domain.endswith('amazonlightsail.com'):
                                return domain
                    
                    # Fallback: use the URL from container service properties
                    url = service.get('url', '')
                    if url and 'amazonlightsail.com' in url:
                        # Extract domain from URL (remove https://)
                        return url.replace('https://', '').replace('http://', '')
            
            # If not found, fall back to constructed domain
            print(f"Warning: Could not find actual domain for {container_service_name}")
            return f"{container_service_name}.{region}.cs.amazonlightsail.com"
            
        except ClientError as e:
            print(f"Error retrieving Lightsail domain: {e}")
            return f"{container_service_name}.{region}.cs.amazonlightsail.com"
        except Exception as e:
            print(f"Unexpected error: {e}")
            return f"{container_service_name}.{region}.cs.amazonlightsail.com"