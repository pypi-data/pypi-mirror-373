"""AWS security resource collectors."""

from typing import Dict, List, Any

from ..base import BaseCollector


class SecurityCollector(BaseCollector):
    """Collector for AWS security resources."""

    def get_iam_info(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get information about IAM users and roles.

        :return: Dictionary containing IAM user and role information
        :rtype: Dict[str, List[Dict[str, Any]]]
        """
        iam_info = {"Users": [], "Roles": []}
        try:
            iam = self._get_client("iam")

            # Get users
            user_paginator = iam.get_paginator("list_users")
            for page in user_paginator.paginate():
                for user in page.get("Users", []):
                    iam_info["Users"].append(
                        {
                            "UserName": user.get("UserName"),
                            "UserId": user.get("UserId"),
                            "Arn": user.get("Arn"),
                            "CreateDate": str(user.get("CreateDate")),
                            "PasswordLastUsed": (
                                str(user.get("PasswordLastUsed")) if user.get("PasswordLastUsed") else None
                            ),
                        }
                    )

            # Get roles
            role_paginator = iam.get_paginator("list_roles")
            for page in role_paginator.paginate():
                for role in page.get("Roles", []):
                    iam_info["Roles"].append(
                        {
                            "RoleName": role.get("RoleName"),
                            "RoleId": role.get("RoleId"),
                            "Arn": role.get("Arn"),
                            "CreateDate": str(role.get("CreateDate")),
                            "AssumeRolePolicyDocument": role.get("AssumeRolePolicyDocument"),
                            "Description": role.get("Description"),
                            "MaxSessionDuration": role.get("MaxSessionDuration"),
                        }
                    )
        except Exception as e:
            self._handle_error(e, "IAM users and roles")
        return iam_info

    def get_kms_keys(self) -> List[Dict[str, Any]]:
        """
        Get information about KMS keys.

        :return: List of KMS key information
        :rtype: List[Dict[str, Any]]
        """
        keys = []
        try:
            kms = self._get_client("kms")
            paginator = kms.get_paginator("list_keys")

            for page in paginator.paginate():
                for key in page.get("Keys", []):
                    try:
                        key_info = kms.describe_key(KeyId=key["KeyId"])["KeyMetadata"]
                        keys.append(
                            {
                                "Region": self.region,
                                "KeyId": key_info.get("KeyId"),
                                "Arn": key_info.get("Arn"),
                                "Description": key_info.get("Description"),
                                "Enabled": key_info.get("Enabled"),
                                "KeyState": key_info.get("KeyState"),
                                "CreationDate": str(key_info.get("CreationDate")),
                                "Origin": key_info.get("Origin"),
                                "KeyManager": key_info.get("KeyManager"),
                            }
                        )
                    except Exception as e:
                        self._handle_error(e, f"KMS key {key['KeyId']}")
        except Exception as e:
            self._handle_error(e, "KMS keys")
        return keys

    def get_secrets(self) -> List[Dict[str, Any]]:
        """
        Get information about Secrets Manager secrets.

        :return: List of secret information
        :rtype: List[Dict[str, Any]]
        """
        secrets = []
        try:
            sm = self._get_client("secretsmanager")
            paginator = sm.get_paginator("list_secrets")

            for page in paginator.paginate():
                for secret in page.get("SecretList", []):
                    secrets.append(
                        {
                            "Region": self.region,
                            "Name": secret.get("Name"),
                            "ARN": secret.get("ARN"),
                            "Description": secret.get("Description"),
                            "KmsKeyId": secret.get("KmsKeyId"),
                            "LastChangedDate": str(secret.get("LastChangedDate")),
                            "LastAccessedDate": str(secret.get("LastAccessedDate")),
                            "Tags": secret.get("Tags", []),
                            "SecretVersionsToStages": secret.get("SecretVersionsToStages", {}),
                        }
                    )
        except Exception as e:
            self._handle_error(e, "Secrets Manager secrets")
        return secrets

    def get_waf_info(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get information about WAF configurations.

        :return: Dictionary containing WAF configuration information
        :rtype: Dict[str, List[Dict[str, Any]]]
        """
        waf_info = {"WebACLs": [], "IPSets": [], "RuleGroups": []}
        try:
            wafv2 = self._get_client("wafv2")

            # Get Web ACLs
            web_acls = wafv2.list_web_acls(Scope="REGIONAL")
            for acl in web_acls.get("WebACLs", []):
                try:
                    acl_detail = wafv2.get_web_acl(Name=acl["Name"], Id=acl["Id"], Scope="REGIONAL")
                    waf_info["WebACLs"].append(
                        {
                            "Region": self.region,
                            "Name": acl.get("Name"),
                            "Id": acl.get("Id"),
                            "ARN": acl.get("ARN"),
                            "Description": acl.get("Description"),
                            "Rules": acl_detail.get("WebACL", {}).get("Rules", []),
                        }
                    )
                except Exception as e:
                    self._handle_error(e, f"WAF Web ACL {acl['Name']}")

            # Get IP Sets
            ip_sets = wafv2.list_ip_sets(Scope="REGIONAL")
            for ip_set in ip_sets.get("IPSets", []):
                try:
                    ip_set_detail = wafv2.get_ip_set(Name=ip_set["Name"], Id=ip_set["Id"], Scope="REGIONAL")
                    waf_info["IPSets"].append(
                        {
                            "Region": self.region,
                            "Name": ip_set.get("Name"),
                            "Id": ip_set.get("Id"),
                            "ARN": ip_set.get("ARN"),
                            "Description": ip_set.get("Description"),
                            "Addresses": ip_set_detail.get("IPSet", {}).get("Addresses", []),
                        }
                    )
                except Exception as e:
                    self._handle_error(e, f"WAF IP Set {ip_set['Name']}")

            # Get Rule Groups
            rule_groups = wafv2.list_rule_groups(Scope="REGIONAL")
            for group in rule_groups.get("RuleGroups", []):
                try:
                    group_detail = wafv2.get_rule_group(Name=group["Name"], Id=group["Id"], Scope="REGIONAL")
                    waf_info["RuleGroups"].append(
                        {
                            "Region": self.region,
                            "Name": group.get("Name"),
                            "Id": group.get("Id"),
                            "ARN": group.get("ARN"),
                            "Description": group.get("Description"),
                            "Rules": group_detail.get("RuleGroup", {}).get("Rules", []),
                        }
                    )
                except Exception as e:
                    self._handle_error(e, f"WAF Rule Group {group['Name']}")
        except Exception as e:
            self._handle_error(e, "WAF configurations")
        return waf_info

    def get_acm_certificates(self) -> List[Dict[str, Any]]:
        """
        Get information about ACM certificates.

        :return: List of certificate information
        :rtype: List[Dict[str, Any]]
        """
        certificates = []
        try:
            acm = self._get_client("acm")
            paginator = acm.get_paginator("list_certificates")

            for page in paginator.paginate():
                for cert in page.get("CertificateSummaryList", []):
                    try:
                        cert_detail = acm.describe_certificate(CertificateArn=cert["CertificateArn"])["Certificate"]
                        certificates.append(
                            {
                                "Region": self.region,
                                "DomainName": cert_detail.get("DomainName"),
                                "CertificateArn": cert_detail.get("CertificateArn"),
                                "Status": cert_detail.get("Status"),
                                "Type": cert_detail.get("Type"),
                                "IssueDate": str(cert_detail.get("IssuedAt")) if cert_detail.get("IssuedAt") else None,
                                "ExpiryDate": str(cert_detail.get("NotAfter")) if cert_detail.get("NotAfter") else None,
                                "SubjectAlternativeNames": cert_detail.get("SubjectAlternativeNames", []),
                                "DomainValidationOptions": cert_detail.get("DomainValidationOptions", []),
                                "Tags": cert_detail.get("Tags", []),
                            }
                        )
                    except Exception as e:
                        self._handle_error(e, f"ACM certificate {cert['CertificateArn']}")
        except Exception as e:
            self._handle_error(e, "ACM certificates")
        return certificates

    def collect(self) -> Dict[str, Any]:
        """
        Collect all security resources.

        :return: Dictionary containing all security resource information
        :rtype: Dict[str, Any]
        """
        return {
            "IAM": self.get_iam_info(),
            "KMSKeys": self.get_kms_keys(),
            "Secrets": self.get_secrets(),
            "WAF": self.get_waf_info(),
            "ACMCertificates": self.get_acm_certificates(),
        }
