gcp_control_tests = {
    "ac-2": {
        "PUBLIC_BUCKET_ACL": {
            "severity": "HIGH",
            "description": "Cloud Storage buckets should not be anonymously or publicly accessible",
        },
        "PUBLIC_DATASET": {
            "severity": "HIGH",
            "description": "Datasets should not be publicly accessible by anyone on the internet",
        },
        "AUDIT_LOGGING_DISABLED": {
            "severity": "LOW",
            "description": "Cloud Audit Logging should be configured properly across all services and all users from a "
            "project",
        },
    },
    "au-2": {
        "AUDIT_LOGGING_DISABLED": {
            "severity": "LOW",
            "description": "Cloud Audit Logging should be configured properly across all services and all users from a "
            "project",
        }
    },
    "ac-3": {
        "NON_ORG_IAM_MEMBER": {
            "severity": "HIGH",
            "description": "Corporate login credentials should be used instead of Gmail accounts",
        },
        "SQL_NO_ROOT_PASSWORD": {
            "severity": "HIGH",
            "description": "MySQL database instance should not allow anyone to connect with administrative privileges.",
        },
    },
    "ac-5": {
        "KMS_ROLE_SEPARATION": {
            "severity": "MEDIUM",
            "description": "Separation of duties should be enforced while assigning KMS related roles to users",
        },
        "SERVICE_ACCOUNT_ROLE_SEPARATION": {
            "severity": "MEDIUM",
            "description": "Separation of duties should be enforced while assigning service account related roles to "
            "users",
        },
    },
    "ac-6": {
        "FULL_API_ACCESS": {
            "severity": "MEDIUM",
            "description": "Instances should not be configured to use the default service account with full access to "
            "all Cloud APIs",
        },
        "OVER_PRIVILEGED_SERVICE_ACCOUNT_USER": {
            "severity": "MEDIUM",
            "description": "The iam.serviceAccountUser and iam.serviceAccountTokenCreator roles should not be assigned "
            "to a user at the project level",
        },
        "PRIMITIVE_ROLES_USED": {
            "severity": "MEDIUM",
            "description": "Basic roles (Owner, Writer, Reader) are too permissive and should not be used",
        },
        "OVER_PRIVILEGED_ACCOUNT": {
            "severity": "MEDIUM",
            "description": "Default Service account should not used for Project access in Kubernetes Clusters",
        },
        "KMS_PROJECT_HAS_OWNER": {
            "severity": "MEDIUM",
            "description": 'Users should not have "Owner" permissions on a project that has cryptographic keys',
        },
    },
    "au-9": {
        "PUBLIC_LOG_BUCKET": {
            "severity": "HIGH",
            "description": "Storage buckets used as log sinks should not be publicly accessible",
        }
    },
    "au-11": {
        "LOCKED_RETENTION_POLICY_NOT_SET": {
            "severity": "LOW",
            "description": "A locked retention policy should be configured for Cloud Storage buckets",
        },
        "OBJECT_VERSIONING_DISABLED": {
            "severity": "LOW",
            "description": "Log-buckets should have Object Versioning enabled",
        },
    },
    "ca-3": {
        "PUBLIC_IP_ADDRESS": {
            "severity": "HIGH",
            "description": "VMs should not be assigned public IP addresses",
        },
        "PUBLIC_SQL_INSTANCE": {
            "severity": "HIGH",
            "description": "Cloud SQL database instances should not be publicly accessible by anyone on the internet",
        },
    },
    "cp-9": {
        "AUTO_BACKUP_DISABLED": {
            "severity": "MEDIUM",
            "description": "Automated backups should be Enabled",
        }
    },
    "ia-2": {
        "MFA_NOT_ENFORCED": {
            "severity": "HIGH",
            "description": "Multi-factor authentication should be enabled for all users in your org unit",
        }
    },
    "sc-7": {
        "OVER_PRIVILEGED_ACCOUNT": {
            "severity": "MEDIUM",
            "description": "Default Service account should not used for Project access in Kubernetes Clusters",
        },
        "PUBLIC_IP_ADDRESS": {
            "severity": "HIGH",
            "description": "VMs should not be assigned public IP addresses",
        },
        "PUBLIC_SQL_INSTANCE": {
            "severity": "HIGH",
            "description": "Cloud SQL database instances should not be publicly accessible by anyone on the internet",
        },
        "NETWORK_POLICY_DISABLED": {
            "severity": "MEDIUM",
            "description": "Network policy should be Enabled on Kubernetes Engine Clusters",
        },
        "OPEN_CASSANDRA_PORT": {
            "severity": "HIGH",
            "description": "Firewall rules should not allow connections from all IP addresses on TCP ports 7000-7001, "
            "7199, 8888, 9042, 9160, 61620-61621",
        },
        "OPEN_CISCOSECURE_WEBSM_PORT": {
            "severity": "HIGH",
            "description": "Firewall rules should not allow connections from all IP addresses on TCP port 9090",
        },
        "OPEN_DIRECTORY_SERVICES_PORT": {
            "severity": "HIGH",
            "description": "Firewall rules should not allow connections from all IP addresses on TCP or UDP port 445",
        },
        "OPEN_DNS_PORT": {
            "severity": "HIGH",
            "description": "Firewall rules should not allow connections from all IP addresses on TCP or UDP port 53",
        },
        "OPEN_ELASTICSEARCH_PORT": {
            "severity": "HIGH",
            "description": "Firewall rules should not allow connections from all IP addresses on TCP ports 9200, 9300",
        },
        "OPEN_FTP_PORT": {
            "severity": "HIGH",
            "description": "Firewall rules should not allow connections from all IP addresses on TCP port 21",
        },
        "OPEN_HTTP_PORT": {
            "severity": "HIGH",
            "description": "Firewall rules should not allow connections from all IP addresses on TCP port 80",
        },
        "OPEN_LDAP_PORT": {
            "severity": "HIGH",
            "description": "Firewall rules should not allow connections from all IP addresses on TCP ports 389, 636"
            " or UDP port 389",
        },
        "OPEN_MEMCACHED_PORT": {
            "severity": "HIGH",
            "description": "Firewall rules should not allow connections from all IP addresses on TCP ports 11211, "
            "11214-11215 or UDP ports 11211, 11214-11215",
        },
        "OPEN_MONGODB_PORT": {
            "severity": "HIGH",
            "description": "Firewall rules should not allow connections from all IP addresses on TCP ports 27017-27019",
        },
        "OPEN_MYSQL_PORT": {
            "severity": "HIGH",
            "description": "Firewall rules should not allow connections from all IP addresses on TCP port 3306",
        },
        "OPEN_NETBIOS_PORT": {
            "severity": "HIGH",
            "description": "Firewall rules should not allow connections from all IP addresses on TCP or UDP ports "
            "137-139",
        },
        "OPEN_ORACLEDB_PORT": {
            "severity": "HIGH",
            "description": "Firewall rules should not allow connections from all IP addresses on TCP ports 1521, "
            "2483-2484 or UDP ports 2483-2484",
        },
        "OPEN_POP3_PORT": {
            "severity": "HIGH",
            "description": "Firewall rules should not allow connections from all IP addresses on TCP port 110",
        },
        "OPEN_POSTGRESQL_PORT": {
            "severity": "HIGH",
            "description": "Firewall rules should not allow connections from all IP addresses on TCP or UDP port 5432",
        },
        "OPEN_RDP_PORT": {
            "severity": "HIGH",
            "description": "Firewall rules should not allow connections from all IP addresses on TCP or UDP port 3389",
        },
        "OPEN_REDIS_PORT": {
            "severity": "HIGH",
            "description": "Firewall rules should not allow connections from all IP addresses on TCP port 6379",
        },
        "OPEN_SMTP_PORT": {
            "severity": "HIGH",
            "description": "Firewall rules should not allow connections from all IP addresses on TCP port 25",
        },
        "OPEN_SSH_PORT": {
            "severity": "HIGH",
            "description": "Firewall rules should not allow connections from all IP addresses on TCP or SCTP port 22",
        },
        "OPEN_TELNET_PORT": {
            "severity": "HIGH",
            "description": "Firewall rules should not allow connections from all IP addresses on TCP port 23",
        },
        "SSL_NOT_ENFORCED": {
            "severity": "HIGH",
            "description": "Cloud SQL database instance should require all incoming connections to use SSL",
        },
        "WEAK_SSL_POLICY": {
            "severity": "MEDIUM",
            "description": "Weak or insecure SSL Policys should not be used",
        },
    },
    "sc-12": {
        "KMS_PROJECT_HAS_OWNER": {
            "severity": "MEDIUM",
            "description": 'Users should not have "Owner" permissions on a project that has cryptographic keys',
        },
        "KMS_KEY_NOT_ROTATED": {
            "severity": "MEDIUM",
            "description": "Encryption keys should be rotated within a period of 90 days",
        },
    },
    "si-4": {
        "FIREWALL_RULE_LOGGING_DISABLED": {
            "severity": "MEDIUM",
            "description": "Firewall rule logging should be enabled so you can audit network access",
        },
        "FLOW_LOGS_DISABLED": {
            "severity": "LOW",
            "description": "VPC Flow logs should be Enabled for every subnet in VPC Network",
        },
    },
}
