#!/usr/bin/env python3
"""
Java Parser for Multi-Language Code Indexing
Uses javalang AST parsing for accurate Java code analysis
"""

import os
import logging
from typing import Dict, List, Optional, Set
from pathlib import Path

try:
    import javalang
except ImportError:
    javalang = None

from .base_parser import BaseParser, CodeNode, CodeRelationship, ParseResult

logger = logging.getLogger(__name__)

# Common JVM classes to ignore (not exhaustive, but covers most common ones)
JVM_COMMON_CLASSES = {
    # java.lang
    'Object', 'String', 'Integer', 'Long', 'Double', 'Float', 'Boolean', 'Byte', 'Short', 'Character',
    'Class', 'System', 'Runtime', 'Thread', 'ThreadGroup', 'ThreadLocal', 'Throwable', 'Exception',
    'RuntimeException', 'Error', 'StringBuilder', 'StringBuffer', 'Math', 'Number', 'Void',
    'Enum', 'Iterable', 'Comparable', 'Cloneable', 'CharSequence', 'Appendable', 'AutoCloseable',
    
    # java.util
    'List', 'ArrayList', 'LinkedList', 'Vector', 'Stack', 'Set', 'HashSet', 'TreeSet', 'LinkedHashSet',
    'Map', 'HashMap', 'TreeMap', 'LinkedHashMap', 'Hashtable', 'Properties', 'Collection', 'Collections',
    'Arrays', 'Iterator', 'ListIterator', 'Queue', 'Deque', 'ArrayDeque', 'PriorityQueue',
    'Optional', 'OptionalInt', 'OptionalLong', 'OptionalDouble', 'Scanner', 'Random', 'UUID',
    'Date', 'Calendar', 'TimeZone', 'Locale', 'Currency', 'Timer', 'TimerTask',
    
    # java.io
    'File', 'InputStream', 'OutputStream', 'Reader', 'Writer', 'FileInputStream', 'FileOutputStream',
    'FileReader', 'FileWriter', 'BufferedReader', 'BufferedWriter', 'PrintWriter', 'PrintStream',
    'ByteArrayInputStream', 'ByteArrayOutputStream', 'ObjectInputStream', 'ObjectOutputStream',
    'Serializable', 'IOException', 'FileNotFoundException',
    
    # java.nio
    'Path', 'Paths', 'Files', 'ByteBuffer', 'CharBuffer', 'IntBuffer', 'LongBuffer', 'FloatBuffer',
    'DoubleBuffer', 'ShortBuffer', 'MappedByteBuffer',
    
    # java.util.stream
    'Stream', 'IntStream', 'LongStream', 'DoubleStream', 'Collectors', 'Collector',
    
    # java.util.function
    'Function', 'Predicate', 'Consumer', 'Supplier', 'BiFunction', 'BiPredicate', 'BiConsumer',
    'UnaryOperator', 'BinaryOperator', 'IntFunction', 'IntPredicate', 'IntConsumer', 'IntSupplier',
    
    # java.time
    'LocalDate', 'LocalTime', 'LocalDateTime', 'ZonedDateTime', 'Instant', 'Duration', 'Period',
    'ZoneId', 'ZoneOffset', 'Clock', 'Year', 'Month', 'DayOfWeek', 'OffsetDateTime', 'OffsetTime',
    
    # java.util.concurrent
    'Future', 'CompletableFuture', 'Executor', 'ExecutorService', 'Executors', 'ThreadPoolExecutor',
    'ScheduledExecutorService', 'Callable', 'Runnable', 'TimeUnit', 'Semaphore', 'CountDownLatch',
    'CyclicBarrier', 'Phaser', 'Exchanger', 'Lock', 'ReentrantLock', 'ReadWriteLock',
    'ConcurrentHashMap', 'ConcurrentLinkedQueue', 'BlockingQueue', 'LinkedBlockingQueue',
    
    # java.lang.reflect
    'Method', 'Field', 'Constructor', 'Modifier', 'Proxy', 'InvocationHandler',
    
    # java.net
    'URL', 'URI', 'URLConnection', 'HttpURLConnection', 'Socket', 'ServerSocket',
    'InetAddress', 'InetSocketAddress',
    
    # java.sql
    'Connection', 'Statement', 'PreparedStatement', 'CallableStatement', 'ResultSet',
    'SQLException', 'DriverManager', 'DataSource',
    
    # javax/jakarta
    'HttpServlet', 'HttpServletRequest', 'HttpServletResponse', 'ServletException',
    'Filter', 'FilterChain', 'ServletContext', 'HttpSession',
}

class JavaParser(BaseParser):
    """
    Java language parser using javalang AST
    Part of Composite Pattern - Leaf class
    """
    
    def __init__(self):
        super().__init__('java')
        self.supported_extensions = {'.java'}
        if javalang is None:
            logger.warning("javalang library not installed. Java parsing will be limited.")
    
    def can_parse(self, file_path: str) -> bool:
        """Check if this parser can handle the given file"""
        path = Path(file_path)
        return path.suffix.lower() in self.supported_extensions
    
    def get_supported_extensions(self) -> Set[str]:
        """Get file extensions supported by this parser"""
        return self.supported_extensions
    
    def parse_file(self, file_path: str) -> ParseResult:
        """Parse a Java file and return nodes and relationships"""
        if javalang is None:
            return ParseResult(
                file_path=file_path,
                language=self.language,
                nodes={},
                relationships=[],
                success=False,
                error_message="javalang library not installed. Run: pip install javalang"
            )
        
        if self._is_binary_file(file_path):
            return ParseResult(
                file_path=file_path,
                language=self.language,
                nodes={},
                relationships=[],
                success=False,
                error_message="Binary file detected"
            )
        
        content = self._read_file_safely(file_path)
        if content is None:
            return ParseResult(
                file_path=file_path,
                language=self.language,
                nodes={},
                relationships=[],
                success=False,
                error_message="Could not read file"
            )
        
        try:
            tree = javalang.parse.parse(content)
        except javalang.parser.JavaSyntaxError as e:
            return ParseResult(
                file_path=file_path,
                language=self.language,
                nodes={},
                relationships=[],
                success=False,
                error_message=f"Java syntax error: {str(e)}"
            )
        except Exception as e:
            return ParseResult(
                file_path=file_path,
                language=self.language,
                nodes={},
                relationships=[],
                success=False,
                error_message=f"Parse error: {str(e)}"
            )
        
        nodes = {}
        relationships = []
        
        # Create file node
        file_node = self._create_node(
            node_type='file',
            name=os.path.basename(file_path),
            path=file_path,
            summary=f"Java file: {os.path.basename(file_path)}"
        )
        nodes[file_node.id] = file_node
        
        # Get package name
        package_name = self._get_package_name(tree)
        
        # Parse AST nodes
        self._parse_ast_nodes(tree, file_node, file_path, nodes, relationships, package_name)
        
        return ParseResult(
            file_path=file_path,
            language=self.language,
            nodes=nodes,
            relationships=relationships,
            success=True
        )
    
    def _get_package_name(self, tree) -> Optional[str]:
        """Extract package name from the compilation unit"""
        if hasattr(tree, 'package') and tree.package:
            return tree.package.name
        return None
    
    def _parse_ast_nodes(self, tree, parent_node: CodeNode, file_path: str, 
                        nodes: Dict[int, CodeNode], relationships: List[CodeRelationship],
                        package_name: Optional[str]):
        """Parse AST nodes recursively"""
        
        # Parse imports
        if hasattr(tree, 'imports'):
            for import_decl in tree.imports:
                self._handle_import(import_decl, parent_node, file_path, nodes, relationships)
        
        # Parse type declarations (classes, interfaces, enums, records)
        if hasattr(tree, 'types'):
            for type_decl in tree.types:
                if isinstance(type_decl, javalang.tree.ClassDeclaration):
                    self._handle_class_declaration(type_decl, parent_node, file_path, nodes, relationships, package_name)
                elif isinstance(type_decl, javalang.tree.InterfaceDeclaration):
                    self._handle_interface_declaration(type_decl, parent_node, file_path, nodes, relationships, package_name)
                elif isinstance(type_decl, javalang.tree.EnumDeclaration):
                    self._handle_enum_declaration(type_decl, parent_node, file_path, nodes, relationships, package_name)
                elif hasattr(javalang.tree, 'RecordDeclaration') and isinstance(type_decl, javalang.tree.RecordDeclaration):
                    # Java 14+ records
                    self._handle_record_declaration(type_decl, parent_node, file_path, nodes, relationships, package_name)
    
    def _handle_import(self, import_decl, parent_node: CodeNode, file_path: str,
                      nodes: Dict[int, CodeNode], relationships: List[CodeRelationship]):
        """Handle import statements"""
        import_path = import_decl.path
        is_static = import_decl.static
        is_wildcard = import_decl.wildcard
        
        # Skip common JVM imports
        if import_path and '.' in import_path:
            last_part = import_path.split('.')[-1]
            if last_part in JVM_COMMON_CLASSES:
                return
        
        import_node = self._create_node(
            node_type='import',
            name=import_path,
            path=file_path,
            summary=f"{'Static ' if is_static else ''}Import: {import_path}{'.*' if is_wildcard else ''}",
            parent_id=parent_node.id,
            is_static=is_static,
            is_wildcard=is_wildcard
        )
        nodes[import_node.id] = import_node
        
        rel = self._create_relationship(
            source_id=parent_node.id,
            target_id=import_node.id,
            relationship_type='imports'
        )
        relationships.append(rel)
    
    def _handle_class_declaration(self, class_decl, parent_node: CodeNode, file_path: str,
                                 nodes: Dict[int, CodeNode], relationships: List[CodeRelationship],
                                 package_name: Optional[str]):
        """Handle class declarations"""
        class_name = class_decl.name
        
        # Skip common JVM classes
        if class_name in JVM_COMMON_CLASSES:
            return
        
        # Get modifiers
        modifiers = class_decl.modifiers if hasattr(class_decl, 'modifiers') else []
        is_abstract = 'abstract' in modifiers
        is_final = 'final' in modifiers
        is_public = 'public' in modifiers
        
        # Get extends and implements
        extends_class = None
        if hasattr(class_decl, 'extends') and class_decl.extends:
            extends_class = class_decl.extends.name
        
        implements_interfaces = []
        if hasattr(class_decl, 'implements') and class_decl.implements:
            implements_interfaces = [impl.name for impl in class_decl.implements]
        
        # Full qualified name
        fqn = f"{package_name}.{class_name}" if package_name else class_name
        
        class_node = self._create_node(
            node_type='class',
            name=class_name,
            path=file_path,
            summary=f"{'Abstract ' if is_abstract else ''}{'Final ' if is_final else ''}Class: {class_name}",
            parent_id=parent_node.id,
            modifiers=modifiers,
            extends=extends_class,
            implements=implements_interfaces,
            package=package_name,
            fqn=fqn
        )
        nodes[class_node.id] = class_node
        
        rel = self._create_relationship(
            source_id=parent_node.id,
            target_id=class_node.id,
            relationship_type='contains'
        )
        relationships.append(rel)
        
        # Parse class body
        self._parse_class_body(class_decl.body, class_node, file_path, nodes, relationships, class_name)
    
    def _handle_interface_declaration(self, interface_decl, parent_node: CodeNode, file_path: str,
                                    nodes: Dict[int, CodeNode], relationships: List[CodeRelationship],
                                    package_name: Optional[str]):
        """Handle interface declarations"""
        interface_name = interface_decl.name
        
        # Get extends
        extends_interfaces = []
        if hasattr(interface_decl, 'extends') and interface_decl.extends:
            extends_interfaces = [ext.name for ext in interface_decl.extends]
        
        # Full qualified name
        fqn = f"{package_name}.{interface_name}" if package_name else interface_name
        
        interface_node = self._create_node(
            node_type='interface',
            name=interface_name,
            path=file_path,
            summary=f"Interface: {interface_name}",
            parent_id=parent_node.id,
            extends=extends_interfaces,
            package=package_name,
            fqn=fqn
        )
        nodes[interface_node.id] = interface_node
        
        rel = self._create_relationship(
            source_id=parent_node.id,
            target_id=interface_node.id,
            relationship_type='contains'
        )
        relationships.append(rel)
        
        # Parse interface body
        self._parse_interface_body(interface_decl.body, interface_node, file_path, nodes, relationships, interface_name)
    
    def _handle_enum_declaration(self, enum_decl, parent_node: CodeNode, file_path: str,
                               nodes: Dict[int, CodeNode], relationships: List[CodeRelationship],
                               package_name: Optional[str]):
        """Handle enum declarations"""
        enum_name = enum_decl.name
        
        # Full qualified name
        fqn = f"{package_name}.{enum_name}" if package_name else enum_name
        
        enum_node = self._create_node(
            node_type='enum',
            name=enum_name,
            path=file_path,
            summary=f"Enum: {enum_name}",
            parent_id=parent_node.id,
            package=package_name,
            fqn=fqn
        )
        nodes[enum_node.id] = enum_node
        
        rel = self._create_relationship(
            source_id=parent_node.id,
            target_id=enum_node.id,
            relationship_type='contains'
        )
        relationships.append(rel)
        
        # Parse enum constants
        if hasattr(enum_decl, 'body') and hasattr(enum_decl.body, 'constants'):
            for constant in enum_decl.body.constants:
                constant_node = self._create_node(
                    node_type='enum_constant',
                    name=f"{enum_name}.{constant.name}",
                    path=file_path,
                    summary=f"Enum constant: {constant.name}",
                    parent_id=enum_node.id
                )
                nodes[constant_node.id] = constant_node
                
                rel = self._create_relationship(
                    source_id=enum_node.id,
                    target_id=constant_node.id,
                    relationship_type='contains'
                )
                relationships.append(rel)
    
    def _handle_record_declaration(self, record_decl, parent_node: CodeNode, file_path: str,
                                 nodes: Dict[int, CodeNode], relationships: List[CodeRelationship],
                                 package_name: Optional[str]):
        """Handle record declarations (Java 14+)"""
        record_name = record_decl.name
        
        # Full qualified name
        fqn = f"{package_name}.{record_name}" if package_name else record_name
        
        record_node = self._create_node(
            node_type='record',
            name=record_name,
            path=file_path,
            summary=f"Record: {record_name}",
            parent_id=parent_node.id,
            package=package_name,
            fqn=fqn
        )
        nodes[record_node.id] = record_node
        
        rel = self._create_relationship(
            source_id=parent_node.id,
            target_id=record_node.id,
            relationship_type='contains'
        )
        relationships.append(rel)
    
    def _parse_class_body(self, body, class_node: CodeNode, file_path: str,
                         nodes: Dict[int, CodeNode], relationships: List[CodeRelationship],
                         class_name: str):
        """Parse class body for fields, methods, and inner classes"""
        if not body:
            return
        
        for member in body:
            if isinstance(member, javalang.tree.FieldDeclaration):
                self._handle_field_declaration(member, class_node, file_path, nodes, relationships, class_name)
            elif isinstance(member, javalang.tree.MethodDeclaration):
                self._handle_method_declaration(member, class_node, file_path, nodes, relationships, class_name)
            elif isinstance(member, javalang.tree.ConstructorDeclaration):
                self._handle_constructor_declaration(member, class_node, file_path, nodes, relationships, class_name)
            elif isinstance(member, javalang.tree.ClassDeclaration):
                # Inner class
                self._handle_class_declaration(member, class_node, file_path, nodes, relationships, None)
            elif isinstance(member, javalang.tree.InterfaceDeclaration):
                # Inner interface
                self._handle_interface_declaration(member, class_node, file_path, nodes, relationships, None)
            elif isinstance(member, javalang.tree.EnumDeclaration):
                # Inner enum
                self._handle_enum_declaration(member, class_node, file_path, nodes, relationships, None)
    
    def _parse_interface_body(self, body, interface_node: CodeNode, file_path: str,
                            nodes: Dict[int, CodeNode], relationships: List[CodeRelationship],
                            interface_name: str):
        """Parse interface body for methods and constants"""
        if not body:
            return
        
        for member in body:
            if isinstance(member, javalang.tree.FieldDeclaration):
                # Interface constants
                self._handle_field_declaration(member, interface_node, file_path, nodes, relationships, interface_name)
            elif isinstance(member, javalang.tree.MethodDeclaration):
                # Interface methods (including default and static methods)
                self._handle_method_declaration(member, interface_node, file_path, nodes, relationships, interface_name)
    
    def _handle_field_declaration(self, field_decl, parent_node: CodeNode, file_path: str,
                                nodes: Dict[int, CodeNode], relationships: List[CodeRelationship],
                                class_name: str):
        """Handle field declarations"""
        field_type = field_decl.type.name if hasattr(field_decl.type, 'name') else str(field_decl.type)
        modifiers = field_decl.modifiers if hasattr(field_decl, 'modifiers') else []
        
        for declarator in field_decl.declarators:
            field_name = declarator.name
            
            field_node = self._create_node(
                node_type='field',
                name=f"{class_name}.{field_name}",
                path=file_path,
                summary=f"Field: {field_type} {field_name}",
                parent_id=parent_node.id,
                field_type=field_type,
                modifiers=modifiers
            )
            nodes[field_node.id] = field_node
            
            rel = self._create_relationship(
                source_id=parent_node.id,
                target_id=field_node.id,
                relationship_type='contains'
            )
            relationships.append(rel)
    
    def _handle_method_declaration(self, method_decl, parent_node: CodeNode, file_path: str,
                                 nodes: Dict[int, CodeNode], relationships: List[CodeRelationship],
                                 class_name: str):
        """Handle method declarations"""
        method_name = method_decl.name
        modifiers = method_decl.modifiers if hasattr(method_decl, 'modifiers') else []
        return_type = method_decl.return_type.name if hasattr(method_decl.return_type, 'name') else str(method_decl.return_type)
        
        # Get parameters
        parameters = []
        if hasattr(method_decl, 'parameters') and method_decl.parameters:
            for param in method_decl.parameters:
                param_type = param.type.name if hasattr(param.type, 'name') else str(param.type)
                parameters.append(f"{param_type} {param.name}")
        
        method_node = self._create_node(
            node_type='method',
            name=f"{class_name}.{method_name}",
            path=file_path,
            summary=f"Method: {return_type} {method_name}({', '.join(parameters)})",
            parent_id=parent_node.id,
            method_name=method_name,
            return_type=return_type,
            parameters=parameters,
            modifiers=modifiers
        )
        nodes[method_node.id] = method_node
        
        rel = self._create_relationship(
            source_id=parent_node.id,
            target_id=method_node.id,
            relationship_type='contains'
        )
        relationships.append(rel)
    
    def _handle_constructor_declaration(self, constructor_decl, parent_node: CodeNode, file_path: str,
                                      nodes: Dict[int, CodeNode], relationships: List[CodeRelationship],
                                      class_name: str):
        """Handle constructor declarations"""
        modifiers = constructor_decl.modifiers if hasattr(constructor_decl, 'modifiers') else []
        
        # Get parameters
        parameters = []
        if hasattr(constructor_decl, 'parameters') and constructor_decl.parameters:
            for param in constructor_decl.parameters:
                param_type = param.type.name if hasattr(param.type, 'name') else str(param.type)
                parameters.append(f"{param_type} {param.name}")
        
        constructor_node = self._create_node(
            node_type='method',
            name=f"{class_name}.<init>",
            path=file_path,
            summary=f"Constructor: {class_name}({', '.join(parameters)})",
            parent_id=parent_node.id,
            method_name='<init>',
            parameters=parameters,
            modifiers=modifiers,
            is_constructor=True
        )
        nodes[constructor_node.id] = constructor_node
        
        rel = self._create_relationship(
            source_id=parent_node.id,
            target_id=constructor_node.id,
            relationship_type='contains'
        )
        relationships.append(rel)