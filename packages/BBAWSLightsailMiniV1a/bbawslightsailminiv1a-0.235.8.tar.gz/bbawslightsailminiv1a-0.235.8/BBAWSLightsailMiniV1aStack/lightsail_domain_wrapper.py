"""
Lightsail Domain Attachment Wrapper
===================================

This module provides a wrapper class for generating AWS CLI commands to attach
custom domains to Lightsail container services with automated SSL certificate management.

The LightSailDomainAttachWrapper class encapsulates the complex domain attachment
workflow including certificate creation, validation waiting, and fallback guidance.

:author: Generated with GitHub Copilot
:version: 1.0.0
:license: MIT
"""

from typing import List, Dict, Optional


class LightSailDomainAttachWrapper:
    """
    Wrapper class for Lightsail domain attachment automation.

    This class generates AWS CLI commands for:
        * SSL certificate creation and validation
        * Custom domain attachment to container services
        * Manual fallback commands for troubleshooting

    :param domains: List of custom domains to attach
    :param region: AWS region where the container service is deployed
    :param container_service_name: Name of the Lightsail container service
    :param max_validation_attempts: Maximum attempts to wait for certificate validation (default: 30)
    :param validation_wait_seconds: Seconds to wait between validation checks (default: 10)

    Example:
        >>> wrapper = LightSailDomainAttachWrapper(
        ...     domains=["api.example.com", "app.example.com"],
        ...     region="ca-central-1",
        ...     container_service_name="my-app-service"
        ... )
        >>> command = wrapper.get_attach_command()
        >>> print(command)
    """

    def __init__(
        self,
        domains: List[str],
        region: str,
        container_service_name: str,
        max_validation_attempts: int = 30,
        validation_wait_seconds: int = 10,
    ):
        """
        Initialize the LightSail Domain Attachment Wrapper.

        :param domains: List of custom domains to attach to the container service
        :type domains: List[str]
        :param region: AWS region where the container service is deployed
        :type region: str
        :param container_service_name: Name of the Lightsail container service
        :type container_service_name: str
        :param max_validation_attempts: Maximum validation attempts (default: 30 = 5 minutes)
        :type max_validation_attempts: int
        :param validation_wait_seconds: Seconds between validation checks (default: 10)
        :type validation_wait_seconds: int

        :raises ValueError: If domains list is empty or container_service_name is empty
        """
        if not domains:
            raise ValueError("Domains list cannot be empty")
        if not container_service_name.strip():
            raise ValueError("Container service name cannot be empty")
        if not region.strip():
            raise ValueError("Region cannot be empty")

        self.domains = domains
        self.region = region
        self.container_service_name = container_service_name
        self.max_validation_attempts = max_validation_attempts
        self.validation_wait_seconds = validation_wait_seconds

        # Derived properties
        self.primary_domain = domains[0]
        self.certificate_name = f"{container_service_name}-cert"
        self.public_domain_names = self._build_public_domain_names()

        def get_cert_name_for_domain(domain):
            """
            Get the SSL certificate name for a specific domain.

            :param domain: The domain name
            :type domain: str
            :returns: The certificate name
            :rtype: str
            """
            return f"cert-{domain.replace('.', '-')}-cert"


    def _build_public_domain_names(self) -> str:
        """
        Build the public domain names JSON string for AWS CLI.

        Creates a JSON object mapping each domain to itself for the
        --public-domain-names parameter in AWS CLI commands.

        :returns: JSON-formatted string for AWS CLI public-domain-names parameter
        :rtype: str

        Example:
            >>> wrapper._build_public_domain_names()
            '{"api.example.com": ["api.example.com"], "app.example.com": ["app.example.com"]}'
        """
        domain_mappings = []
        for domain in self.domains:
            domain_mappings.append(f'"{domain}": ["{domain}"]')
        return "{" + ", ".join(domain_mappings) + "}"

    def get_certificate_creation_command(self) -> str:
        """
        Generate AWS CLI command for SSL certificate creation.

        :returns: AWS CLI command to create SSL certificate
        :rtype: str

        Example:
            >>> wrapper.get_certificate_creation_command()
            'aws lightsail create-certificate --certificate-name my-service-cert ...'
        """

        certificate_name = self.get_cert_name_for_domain(self.primary_domain)

        return (
            f"aws lightsail create-certificate \\\n"
            f"  --certificate-name {certificate_name} \\\n"
            f"  --domain-name {self.primary_domain} \\\n"
            f"  --region {self.region}"
        )

    def get_certificate_status_command(self) -> str:
        """
        Generate AWS CLI command to check certificate status.

        :returns: AWS CLI command to query certificate validation status
        :rtype: str
        """
        return (
            f"aws lightsail get-certificates --region {self.region} "
            f"--include-certificate-details --query "
            f"'certificates[?certificateName==`{self.certificate_name}`].certificateDetail.status' "
            f"--output text"
        )

    def get_domain_attachment_command(self) -> str:
        """
        Generate AWS CLI command for domain attachment.

        :returns: AWS CLI command to attach domains to container service
        :rtype: str
        """
        return (
            f"aws lightsail update-container-service \\\n"
            f"  --service-name {self.container_service_name} \\\n"
            f"  --region {self.region} \\\n"
            f"  --public-domain-names '{self.public_domain_names}'"
        )

    def get_manual_attachment_guidance(self) -> List[str]:
        """
        Generate manual command guidance for troubleshooting.

        :returns: List of guidance messages with manual commands
        :rtype: List[str]
        """
        return [
            "🔧 MANUAL ACTION REQUIRED:",
            "If the certificate is still validating, wait a few more minutes and run:",
            "",
            self.get_domain_attachment_command(),
            "",
            "Check certificate status with:",
            f"aws lightsail get-certificates --region {self.region} --include-certificate-details",
        ]

    def get_attach_command(self) -> str:
        """
        Generate the complete domain attachment bash script.

        Creates a comprehensive bash script that:
            1. Creates SSL certificate for the primary domain
            2. Waits for certificate validation (up to configured time limit)
            3. Attempts domain attachment once certificate is validated
            4. Provides manual guidance if automation fails

        :returns: Complete bash script for domain attachment automation
        :rtype: str

        .. note::
           The script uses 'continue' for certificate creation to handle cases
           where the certificate already exists.

        .. warning::
           Certificate validation can take up to 20 minutes for DNS propagation.
           The script only waits for the configured time limit before providing
           manual guidance.
        """
        validation_minutes = (self.max_validation_attempts * self.validation_wait_seconds) / 60

        script = f"""
# Step 1: Create SSL certificate for the domain
echo "Creating SSL certificate for domain {self.primary_domain}..."
{self.get_certificate_creation_command()} || echo "Certificate may already exist"

# Step 2: Wait for certificate validation (up to {validation_minutes:.1f} minutes)
echo "Waiting for certificate validation (up to {validation_minutes:.1f} minutes)..."
for i in {{1..{self.max_validation_attempts}}}; do
    echo "Checking certificate status (attempt $i/{self.max_validation_attempts})..."
    cert_status=$({self.get_certificate_status_command()})
    if [ "$cert_status" = "ISSUED" ]; then
        echo "✅ Certificate validated successfully!"
        break
    elif [ "$cert_status" = "FAILED" ]; then
        echo "❌ Certificate validation failed!"
        break
    else
        echo "Certificate status: $cert_status - waiting {self.validation_wait_seconds} seconds..."
        sleep {self.validation_wait_seconds}
    fi
done

# Step 3: Attempt to attach the custom domains to container service
echo "Attempting to attach custom domains to container service..."
if {self.get_domain_attachment_command()}; then
    echo "✅ Domain attachment successful!"
else
    echo "❌ Domain attachment failed - certificate may still be validating"
    echo ""
    {chr(10).join(f'    echo "{line}"' for line in self.get_manual_attachment_guidance())}
fi
"""
        return script.strip()

    def get_post_deployment_messages(self) -> List[str]:
        """
        Generate informational messages for post-deployment guidance.

        :returns: List of messages to display after Terraform deployment
        :rtype: List[str]
        """
        validation_minutes = (self.max_validation_attempts * self.validation_wait_seconds) / 60

        return [
            f"🔧 SSL certificate will be created and domains attached automatically (with {validation_minutes:.1f}-minute validation wait).",
            "⚠️  If automatic attachment fails, manual commands will be displayed for you to run.",
            f"📋 Certificate check: aws lightsail get-certificates --region {self.region} --include-certificate-details",
            f"📋 Manual domain attachment: {self.get_domain_attachment_command().replace(chr(10), ' ')}",
        ]

    def get_domains_info(self) -> Dict[str, any]:
        """
        Get comprehensive domain configuration information.

        :returns: Dictionary containing all domain-related configuration
        :rtype: Dict[str, any]

        **Returned Dictionary Keys:**

        * domains: List of all domains to attach
        * primary_domain: First domain used for certificate creation
        * certificate_name: Generated certificate name
        * public_domain_names: JSON string for AWS CLI
        * region: AWS region
        * container_service_name: Container service name
        * validation_config: Validation timing configuration
        """
        return {
            "domains": self.domains,
            "primary_domain": self.primary_domain,
            "certificate_name": self.certificate_name,
            "public_domain_names": self.public_domain_names,
            "region": self.region,
            "container_service_name": self.container_service_name,
            "validation_config": {
                "max_attempts": self.max_validation_attempts,
                "wait_seconds": self.validation_wait_seconds,
                "total_wait_minutes": (self.max_validation_attempts * self.validation_wait_seconds) / 60,
            },
        }
