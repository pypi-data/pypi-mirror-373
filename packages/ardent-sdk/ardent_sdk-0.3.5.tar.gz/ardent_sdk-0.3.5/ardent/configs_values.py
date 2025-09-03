config_definition = {
    "mongodb": {
        "required_params": ["connection_string", "databases"],
        "structure": {
            "connection_string": str,
            "databases": {
                "type": list,
                "structure": {
                    "required": ["name", "collections"],
                    "properties": {
                        "name": str,
                        "collections": {
                            "type": list,
                            "structure": {
                                "required": ["name"],
                                "properties": {
                                    "name": str
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "postgreSQL": {
        "required_params": ["databases", "Hostname", "Port", "username", "password"],
        "structure": {
            "Hostname": str,
            "Port": str,
            "username": str,
            "password": str,
            "databases": {
                "type": list,
                "structure": {
                    "required": ["name"],
                    "properties": {
                        "name": str
                    }
                }
            }
        }
    },
    "supabase": {
        "required_params": ["project_url", "api_key", "databases"],
        "structure": {
            "project_url": str,
            "api_key": str,
            "databases": list  # Simple list, no nested structure
        }
    },
    "airflow": {
        "required_params": ["github_token", "repo", "dag_path", "host", "username", "password"],
        "structure": {
            "github_token": str,
            "repo": str,
            "dag_path": str,
            "requirements_path": str,
            "host": str,
            "username": str,
            "password": str,
        }
    },
    "azureSQLServer": {
        "endpoint": "/v1/configs/setAzureSQLServerConfig",
        "required_params": ["server", "username", "password", "version", "databases"],
        "structure": {
            "server": str,
            "username": str,
            "password": str,
            "version": str,
            "databases": {
                "type": list,
                "structure": {
                    "required": ["name"],
                    "properties": {
                        "name": str
                    }
                }
            }
        }
    },
    "snowflake": {
        "required_params": ["account", "user", "password", "warehouse", "databases"],
        "structure": {
            "account": str,
            "user": str,
            "password": str,
            "warehouse": str,
            "databases": {
                "type": list,
                "structure": {
                    "required": ["name"],
                    "properties": {
                        "name": str
                    }
                }
            }
        }
    },
    "databricks": {
        "required_params": ["server_hostname", "http_path", "access_token", "catalogs"],
        "structure": {
            "server_hostname": str,
            "http_path": str,
            "access_token": str,
            "catalogs": {
                "type": list,
                "structure": {
                    "required": ["name", "databases"],
                    "properties": {
                        "name": str,
                        "databases": {
                            "type": list,
                            "structure": {
                                "required": ["name", "tables"],
                                "properties": {
                                    "name": str,
                                    "tables": {
                                        "type": list,
                                        "structure": {
                                            "required": ["name"],
                                            "properties": {
                                                "name": str
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "mysql": {
        "required_params": ["host", "port", "username", "password", "databases"],
        "structure": {
            "host": str,
            "port": str,
            "username": str,
            "password": str,
            "databases": {
                "type": list,
                "structure": {
                    "required": ["name"],
                    "properties": {
                        "name": str
                    }
                }
            }
        }
    },
    "databricksJobs": {
        "required_params": ["workspace_url", "access_token", "github_token", "repo", "repo_path"],
        "structure": {
            "workspace_url": str,
            "access_token": str,
            "github_token": str,
            "repo": str,
            "repo_path": str,
        }
    },
    "tigerbeetle": {
        "required_params": ["cluster_id", "replica_addresses"],
        "structure": {
            "cluster_id": str,
            "replica_addresses": list,  # List of strings
        }
    }
}