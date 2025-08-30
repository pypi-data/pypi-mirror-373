"""AWS container resource collectors."""

from typing import Dict, List, Any

from ..base import BaseCollector


class ContainerCollector(BaseCollector):
    """Collector for AWS container resources."""

    @staticmethod
    def _get_repository_policy(ecr, repository_name: str) -> Dict[str, Any]:
        """
        Get repository policy for an ECR repository.

        :param ecr: ECR client
        :param str repository_name: Name of the repository
        :return: Repository policy or None if not found
        :rtype: Dict[str, Any]
        """
        try:
            return ecr.get_repository_policy(repositoryName=repository_name).get("policyText")
        except Exception as ex:
            from regscale.core.app.utils.app_utils import create_logger

            create_logger().debug(f"Error getting repository policy for {repository_name}: {ex}")
            return None

    @staticmethod
    def _get_repository_images(ecr, repository_name: str) -> List[Dict[str, Any]]:
        """
        Get image details for an ECR repository.

        :param ecr: ECR client
        :param str repository_name: Name of the repository
        :return: List of image details
        :rtype: List[Dict[str, Any]]
        """
        images = []
        image_paginator = ecr.get_paginator("describe_images")
        for image_page in image_paginator.paginate(repositoryName=repository_name):
            for image in image_page.get("imageDetails", []):
                images.append(
                    {
                        "ImageDigest": image.get("imageDigest"),
                        "ImageTags": image.get("imageTags", []),
                        "ImageSizeInBytes": image.get("imageSizeInBytes"),
                        "ImagePushedAt": str(image.get("imagePushedAt")),
                        "ImageScanStatus": image.get("imageScanStatus", {}),
                        "ImageScanFindingsSummary": image.get("imageScanFindingsSummary", {}),
                    }
                )
        return images

    def _build_repository_data(
        self, repo: Dict[str, Any], policy: Dict[str, Any], images: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build repository data dictionary.

        :param repo: Raw repository data
        :param policy: Repository policy
        :param images: List of image details
        :return: Processed repository data
        :rtype: Dict[str, Any]
        """
        return {
            "Region": self.region,
            "RepositoryName": repo.get("repositoryName"),
            "RepositoryArn": repo.get("repositoryArn"),
            "RegistryId": repo.get("registryId"),
            "RepositoryUri": repo.get("repositoryUri"),
            "CreatedAt": str(repo.get("createdAt")),
            "ImageTagMutability": repo.get("imageTagMutability"),
            "ImageScanningConfiguration": repo.get("imageScanningConfiguration", {}),
            "EncryptionConfiguration": repo.get("encryptionConfiguration", {}),
            "Policy": policy,
            "Images": images,
        }

    def get_ecr_repositories(self) -> List[Dict[str, Any]]:
        """
        Get information about ECR repositories.

        :return: List of ECR repository information
        :rtype: List[Dict[str, Any]]
        """
        repositories = []
        try:
            ecr = self._get_client("ecr")
            paginator = ecr.get_paginator("describe_repositories")

            for page in paginator.paginate():
                for repo in page.get("repositories", []):
                    try:
                        policy = self._get_repository_policy(ecr, repo["repositoryName"])
                        images = self._get_repository_images(ecr, repo["repositoryName"])
                        repo_data = self._build_repository_data(repo, policy, images)
                        repositories.append(repo_data)
                    except Exception as e:
                        self._handle_error(e, f"ECR repository {repo['repositoryName']}")
        except Exception as e:
            self._handle_error(e, "ECR repositories")
        return repositories

    def collect(self) -> Dict[str, Any]:
        """
        Collect all container resources.

        :return: Dictionary containing all container resource information
        :rtype: Dict[str, Any]
        """
        return {"ECRRepositories": self.get_ecr_repositories()}
