#!/usr/bin/env python3
"""
Infrastructure and Architecture Detection
"""

import ast
import re
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
import json
from .logger import log_warning


@dataclass
class InfraComponent:
    component_type: str
    name: str
    technology: str
    configuration: Dict
    usage_frequency: int
    connections: List[str]


class InfrastructureDetector:
    """Detect infrastructure components and architectural patterns"""
    
    def __init__(self):
        # Database patterns
        self.db_patterns = {
            'postgresql': {
                'imports': ['psycopg2', 'asyncpg', 'sqlalchemy'],
                'patterns': [r'postgresql://', r'postgres://', r'\.postgres\.', r'POSTGRES_'],
                'configs': [r'DATABASE_URL', r'POSTGRES_', r'PGHOST', r'PGPORT']
            },
            'mysql': {
                'imports': ['mysql.connector', 'pymysql', 'aiomysql'],
                'patterns': [r'mysql://', r'\.mysql\.', r'MYSQL_'],
                'configs': [r'MYSQL_', r'DB_HOST', r'DB_PORT']
            },
            'mongodb': {
                'imports': ['pymongo', 'motor', 'mongoengine'],
                'patterns': [r'mongodb://', r'\.mongo\.', r'MONGO_'],
                'configs': [r'MONGO_', r'MONGODB_']
            },
            'redis': {
                'imports': ['redis', 'aioredis'],
                'patterns': [r'redis://', r'\.redis\.', r'REDIS_'],
                'configs': [r'REDIS_', r'CACHE_']
            },
            'sqlite': {
                'imports': ['sqlite3'],
                'patterns': [r'\.db$', r'\.sqlite', r'sqlite://'],
                'configs': [r'DATABASE_FILE', r'DB_PATH']
            }
        }
        
        # API patterns
        self.api_patterns = {
            'rest_api': {
                'patterns': [
                    r'@app\.route\(',
                    r'@router\.',
                    r'@get\(|@post\(|@put\(|@delete\(',
                    r'\.json\(\)',
                    r'request\.get|request\.post'
                ],
                'frameworks': ['flask', 'fastapi', 'django', 'tornado']
            },
            'graphql': {
                'patterns': [
                    r'@strawberry\.',
                    r'graphql',
                    r'Query\(|Mutation\(',
                    r'schema\s*='
                ],
                'frameworks': ['strawberry', 'graphene', 'ariadne']
            },
            'grpc': {
                'patterns': [
                    r'grpc\.',
                    r'_pb2\.',
                    r'servicer',
                    r'\.proto'
                ],
                'frameworks': ['grpcio', 'grpcio-tools']
            }
        }
        
        # Message Queue patterns
        self.mq_patterns = {
            'celery': {
                'patterns': [r'@celery\.', r'@task', r'\.delay\(', r'\.apply_async'],
                'configs': [r'CELERY_', r'BROKER_URL']
            },
            'rabbitmq': {
                'patterns': [r'amqp://', r'rabbitmq', r'pika\.'],
                'configs': [r'RABBITMQ_', r'AMQP_']
            },
            'kafka': {
                'patterns': [r'kafka', r'KafkaProducer', r'KafkaConsumer'],
                'configs': [r'KAFKA_']
            },
            'sqs': {
                'patterns': [r'sqs', r'\.sqs\.', r'SQS'],
                'configs': [r'SQS_', r'AWS_SQS']
            }
        }
        
        # Cloud services
        self.cloud_patterns = {
            'aws': {
                'services': {
                    's3': [r'\.s3\.', r'S3Client', r'bucket'],
                    'lambda': [r'\.lambda\.', r'LambdaClient', r'aws_lambda'],
                    'dynamodb': [r'\.dynamodb\.', r'DynamoDBClient'],
                    'ec2': [r'\.ec2\.', r'EC2Client'],
                    'rds': [r'\.rds\.', r'RDSClient'],
                    'sqs': [r'\.sqs\.', r'SQSClient'],
                    'sns': [r'\.sns\.', r'SNSClient']
                },
                'configs': [r'AWS_', r'AMAZON_']
            },
            'gcp': {
                'services': {
                    'storage': [r'google\.cloud\.storage', r'storage_client'],
                    'bigquery': [r'google\.cloud\.bigquery', r'bigquery_client'],
                    'firestore': [r'google\.cloud\.firestore', r'firestore_client'],
                    'pubsub': [r'google\.cloud\.pubsub', r'pubsub_client']
                },
                'configs': [r'GOOGLE_', r'GCP_', r'GCLOUD_']
            },
            'azure': {
                'services': {
                    'storage': [r'azure\.storage', r'BlobServiceClient'],
                    'cosmos': [r'azure\.cosmos', r'CosmosClient'],
                    'functions': [r'azure\.functions', r'FunctionApp']
                },
                'configs': [r'AZURE_', r'MICROSOFT_']
            }
        }
        
        # Configuration patterns
        self.config_patterns = {
            'environment': [
                r'os\.environ',
                r'getenv\(',
                r'\.env',
                r'load_dotenv',
                r'environment',
                r'ENV_'
            ],
            'settings_files': [
                r'settings\.py',
                r'config\.py',
                r'configuration',
                r'\.ini',
                r'\.yaml',
                r'\.json'
            ],
            'secrets': [
                r'SECRET_',
                r'PASSWORD',
                r'TOKEN',
                r'API_KEY',
                r'PRIVATE_KEY',
                r'vault',
                r'secrets'
            ]
        }
    
    def detect_infrastructure(self, tree: ast.AST, file_path: str, file_content: str) -> Dict[str, List[InfraComponent]]:
        """Detect all infrastructure components"""
        infrastructure = {
            'databases': [],
            'apis': [],
            'message_queues': [],
            'cloud_services': [],
            'configuration': []
        }
        
        # Handle None or invalid AST
        if tree is None:
            tree = ast.Module(body=[], type_ignores=[])
        
        try:
            # Detect databases
            infrastructure['databases'] = self._detect_databases(tree, file_content)
            
            # Detect APIs
            infrastructure['apis'] = self._detect_apis(tree, file_content)
            
            # Detect Message Queues
            infrastructure['message_queues'] = self._detect_message_queues(tree, file_content)
            
            # Detect Cloud Services
            infrastructure['cloud_services'] = self._detect_cloud_services(tree, file_content)
            
            # Detect Configuration
            infrastructure['configuration'] = self._detect_configuration(tree, file_content)
        except (AttributeError, TypeError) as e:
            # Handle malformed AST gracefully
            log_warning(f"Could not detect infrastructure in {file_path}: {e}")
        
        return infrastructure
    
    def _detect_databases(self, tree: ast.AST, file_content: str) -> List[InfraComponent]:
        """Detect database usage"""
        components = []
        
        for db_type, config in self.db_patterns.items():
            usage_count = 0
            connections = []
            detected_config = {}
            
            # Check imports
            for import_pattern in config['imports']:
                if import_pattern in file_content:
                    usage_count += file_content.count(import_pattern)
                    connections.append(f"import:{import_pattern}")
            
            # Check patterns
            for pattern in config['patterns']:
                matches = re.findall(pattern, file_content, re.IGNORECASE)
                usage_count += len(matches)
                connections.extend([f"pattern:{m}" for m in matches])
            
            # Check config patterns
            for config_pattern in config.get('configs', []):
                matches = re.findall(config_pattern, file_content, re.IGNORECASE)
                if matches:
                    detected_config[config_pattern] = matches
                    connections.extend([f"config:{m}" for m in matches])
            
            if usage_count > 0:
                components.append(InfraComponent(
                    component_type="database",
                    name=db_type,
                    technology=db_type,
                    configuration=detected_config,
                    usage_frequency=usage_count,
                    connections=connections
                ))
        
        return components
    
    def _detect_apis(self, tree: ast.AST, file_content: str) -> List[InfraComponent]:
        """Detect API patterns"""
        components = []
        
        for api_type, config in self.api_patterns.items():
            usage_count = 0
            connections = []
            frameworks = []
            
            # Check patterns
            for pattern in config['patterns']:
                matches = re.findall(pattern, file_content, re.IGNORECASE | re.MULTILINE)
                usage_count += len(matches)
                connections.extend([f"endpoint:{m}" for m in matches[:5]])  # Limit to 5
            
            # Check frameworks
            for framework in config.get('frameworks', []):
                if framework in file_content:
                    frameworks.append(framework)
                    connections.append(f"framework:{framework}")
            
            if usage_count > 0:
                components.append(InfraComponent(
                    component_type="api",
                    name=api_type,
                    technology=', '.join(frameworks) if frameworks else api_type,
                    configuration={'frameworks': frameworks},
                    usage_frequency=usage_count,
                    connections=connections
                ))
        
        return components
    
    def _detect_message_queues(self, tree: ast.AST, file_content: str) -> List[InfraComponent]:
        """Detect message queue usage"""
        components = []
        
        for mq_type, config in self.mq_patterns.items():
            usage_count = 0
            connections = []
            detected_config = {}
            
            # Check patterns
            for pattern in config['patterns']:
                matches = re.findall(pattern, file_content, re.IGNORECASE)
                usage_count += len(matches)
                connections.extend([f"pattern:{m}" for m in matches])
            
            # Check config patterns
            for config_pattern in config.get('configs', []):
                matches = re.findall(config_pattern, file_content, re.IGNORECASE)
                if matches:
                    detected_config[config_pattern] = matches
                    connections.extend([f"config:{m}" for m in matches])
            
            if usage_count > 0:
                components.append(InfraComponent(
                    component_type="message_queue",
                    name=mq_type,
                    technology=mq_type,
                    configuration=detected_config,
                    usage_frequency=usage_count,
                    connections=connections
                ))
        
        return components
    
    def _detect_cloud_services(self, tree: ast.AST, file_content: str) -> List[InfraComponent]:
        """Detect cloud service usage"""
        components = []
        
        for cloud_provider, config in self.cloud_patterns.items():
            for service_name, patterns in config['services'].items():
                usage_count = 0
                connections = []
                
                for pattern in patterns:
                    matches = re.findall(pattern, file_content, re.IGNORECASE)
                    usage_count += len(matches)
                    connections.extend([f"service:{m}" for m in matches])
                
                # Check config patterns
                detected_config = {}
                for config_pattern in config.get('configs', []):
                    matches = re.findall(config_pattern, file_content, re.IGNORECASE)
                    if matches:
                        detected_config[config_pattern] = matches
                        connections.extend([f"config:{m}" for m in matches])
                
                if usage_count > 0:
                    components.append(InfraComponent(
                        component_type="cloud_service",
                        name=f"{cloud_provider}_{service_name}",
                        technology=f"{cloud_provider.upper()} {service_name.title()}",
                        configuration=detected_config,
                        usage_frequency=usage_count,
                        connections=connections
                    ))
        
        return components
    
    def _detect_configuration(self, tree: ast.AST, file_content: str) -> List[InfraComponent]:
        """Detect configuration patterns"""
        components = []
        
        for config_type, patterns in self.config_patterns.items():
            usage_count = 0
            connections = []
            
            for pattern in patterns:
                matches = re.findall(pattern, file_content, re.IGNORECASE)
                usage_count += len(matches)
                connections.extend([f"config:{m}" for m in matches[:10]])  # Limit to 10
            
            if usage_count > 0:
                components.append(InfraComponent(
                    component_type="configuration",
                    name=config_type,
                    technology=config_type,
                    configuration={},
                    usage_frequency=usage_count,
                    connections=connections
                ))
        
        return components
    
    def detect_architectural_patterns(self, tree: ast.AST, file_content: str) -> Dict[str, Dict]:
        """Detect architectural patterns"""
        patterns = {}
        
        # Microservices indicators
        microservice_indicators = [
            r'@app\.route',  # Multiple endpoints
            r'service',      # Service naming
            r'api/',         # API structure
            r'docker',       # Containerization
            r'kubernetes',   # Orchestration
        ]
        
        microservice_score = 0
        for indicator in microservice_indicators:
            if re.search(indicator, file_content, re.IGNORECASE):
                microservice_score += 1
        
        if microservice_score >= 2:
            patterns['microservices'] = {
                'confidence': microservice_score / len(microservice_indicators),
                'indicators': microservice_score
            }
        
        # Event-driven architecture
        event_indicators = [
            r'event',
            r'publish',
            r'subscribe',
            r'queue',
            r'topic',
            r'message'
        ]
        
        event_score = sum(1 for indicator in event_indicators 
                         if re.search(indicator, file_content, re.IGNORECASE))
        
        if event_score >= 2:
            patterns['event_driven'] = {
                'confidence': event_score / len(event_indicators),
                'indicators': event_score
            }
        
        # Serverless indicators
        serverless_indicators = [
            r'lambda',
            r'function',
            r'serverless',
            r'aws_lambda',
            r'cloud_function'
        ]
        
        serverless_score = sum(1 for indicator in serverless_indicators 
                              if re.search(indicator, file_content, re.IGNORECASE))
        
        if serverless_score >= 1:
            patterns['serverless'] = {
                'confidence': serverless_score / len(serverless_indicators),
                'indicators': serverless_score
            }
        
        return patterns