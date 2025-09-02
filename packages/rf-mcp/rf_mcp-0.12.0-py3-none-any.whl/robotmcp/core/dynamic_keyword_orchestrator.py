"""Main orchestrator for dynamic keyword discovery."""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from robotmcp.models.library_models import KeywordInfo, ParsedArguments
from robotmcp.core.library_manager import LibraryManager
from robotmcp.core.keyword_discovery import KeywordDiscovery
from robotmcp.utils.argument_processor import ArgumentProcessor

if TYPE_CHECKING:
    from robotmcp.models.session_models import ExecutionSession

logger = logging.getLogger(__name__)


class DynamicKeywordDiscovery:
    """Main orchestrator for dynamic Robot Framework keyword discovery and management."""
    
    def __init__(self):
        self.library_manager = LibraryManager()
        self.keyword_discovery = KeywordDiscovery()
        self.argument_processor = ArgumentProcessor()
        
        # Initialize session manager (use the execution session manager instead)
        self.session_manager = None  # Will be set by ExecutionCoordinator when needed
        
        # Initialize with minimal libraries
        self._initialize_minimal()
    
    def set_session_manager(self, session_manager):
        """Set the session manager from the execution coordinator."""
        self.session_manager = session_manager
    
    def _initialize_minimal(self) -> None:
        """Initialize with minimal core libraries only."""
        # Load minimal core libraries
        core_libraries = ["BuiltIn", "Collections", "String"]
        self.library_manager.load_session_libraries(core_libraries, self.keyword_discovery)
        
        # Add keywords to cache
        for lib_info in self.library_manager.libraries.values():
            self.keyword_discovery.add_keywords_to_cache(lib_info)
        
        logger.info(f"Initialized with minimal libraries: {len(self.library_manager.libraries)} libraries with {len(self.keyword_discovery.keyword_cache)} keywords")
    
    def _initialize_legacy(self) -> None:
        """Legacy initialization method - loads all libraries."""
        # Load all libraries through the library manager
        self.library_manager.load_all_libraries(self.keyword_discovery)
        
        # Add all keywords to cache
        for lib_info in self.library_manager.libraries.values():
            self.keyword_discovery.add_keywords_to_cache(lib_info)
        
        logger.info(f"Initialized {len(self.library_manager.libraries)} libraries with {len(self.keyword_discovery.keyword_cache)} keywords")
    
    # Public API methods
    def find_keyword(self, keyword_name: str, active_library: str = None) -> Optional[KeywordInfo]:
        """Find a keyword by name with fuzzy matching, optionally filtering by active library."""
        # Try LibDoc-based storage first if available (more accurate)
        try:
            from robotmcp.utils.rf_libdoc_integration import get_rf_doc_storage
            rf_doc_storage = get_rf_doc_storage()
            
            if rf_doc_storage.is_available():
                libdoc_result = self._find_keyword_libdoc(keyword_name, active_library, rf_doc_storage)
                if libdoc_result:
                    return libdoc_result
        except Exception as e:
            logger.debug(f"LibDoc keyword search failed, falling back to inspection: {e}")
        
        # Fall back to inspection-based discovery
        return self.keyword_discovery.find_keyword(keyword_name, active_library)
    
    def _find_keyword_libdoc(self, keyword_name: str, active_library: str, rf_doc_storage) -> Optional[KeywordInfo]:
        """Find keyword using LibDoc storage with library filtering."""
        if not keyword_name:
            return None
            
        # Get keywords to search based on active library filter
        keywords = []
        
        if active_library:
            # Get keywords ONLY from active library + built-ins
            if active_library in ["Browser", "SeleniumLibrary"]:
                try:
                    keywords.extend(rf_doc_storage.get_keywords_by_library(active_library))
                    logger.debug(f"LibDoc: Found {len([k for k in keywords if k.library == active_library])} keywords from {active_library}")
                except Exception as e:
                    logger.debug(f"LibDoc: Failed to get {active_library} keywords: {e}")
            
            # Add built-in libraries using centralized registry
            from robotmcp.config.library_registry import get_builtin_libraries
            builtin_libraries = get_builtin_libraries()
            
            for builtin_lib in builtin_libraries.keys():
                try:
                    builtin_kws = rf_doc_storage.get_keywords_by_library(builtin_lib)
                    keywords.extend(builtin_kws)
                    logger.debug(f"LibDoc: Found {len(builtin_kws)} keywords from {builtin_lib}")
                except:
                    pass  # Library might not be loaded
        else:
            # Get all keywords when no filter is specified
            keywords = rf_doc_storage.get_all_keywords()
        
        # Search for exact match first
        for kw in keywords:
            if kw.name.lower() == keyword_name.lower():
                # Convert LibDoc keyword to our KeywordInfo format
                return KeywordInfo(
                    name=kw.name,
                    library=kw.library,
                    method_name=kw.name.replace(' ', '_').lower(),
                    doc=kw.doc,
                    short_doc=kw.short_doc,
                    args=kw.args,
                    defaults={},  # LibDoc doesn't provide defaults in same format
                    tags=kw.tags,
                    is_builtin=(kw.library in builtin_libraries)
                )
        
        # Try fuzzy matching with name variations
        normalized = keyword_name.lower().strip()
        variations = [
            normalized.replace(' ', ''),   # Remove spaces
            normalized.replace('_', ' '),  # Replace underscores
            normalized.replace('-', ' '),  # Replace hyphens
        ]
        
        for variation in variations:
            for kw in keywords:
                if kw.name.lower().replace(' ', '') == variation:
                    return KeywordInfo(
                        name=kw.name,
                        library=kw.library,
                        method_name=kw.name.replace(' ', '_').lower(),
                        doc=kw.doc,
                        short_doc=kw.short_doc,
                        args=kw.args,
                        defaults={},
                        tags=kw.tags,
                        is_builtin=(kw.library in builtin_libraries)
                    )
        
        return None
    
    def _execute_with_rf_type_conversion(self, method, keyword_info, original_args):
        """Execute method using Robot Framework's native type conversion system."""
        try:
            from robot.running.arguments.typeconverters import TypeConverter
            from robot.running.arguments.typeinfo import TypeInfo
            from robot.running.arguments.argumentresolver import ArgumentResolver
            from robot.running.arguments import ArgumentSpec
            import inspect
            
            # Get method signature
            sig = inspect.signature(method)
            
            # Smart detection: only process named arguments if we actually find valid ones
            potential_named_args = any('=' in arg for arg in original_args)
            
            if potential_named_args:
                # Try to use the actual method signature for parameter validation (more reliable than KeywordInfo.args)
                try:
                    param_names = list(sig.parameters.keys())
                    logger.debug(f"Method signature parameters for {keyword_info.name}: {param_names}")
                    
                    # Parse arguments to see if we actually have valid named arguments
                    positional_args, named_args = self._split_args_using_method_signature(original_args, sig)
                except (AttributeError, TypeError):
                    # Fallback to the original KeywordInfo-based approach (for tests and edge cases)
                    logger.debug(f"Unable to inspect method signature, falling back to KeywordInfo.args approach")
                    if hasattr(keyword_info, 'args') and keyword_info.args:
                        positional_args, named_args = self._split_args_into_positional_and_named(original_args, keyword_info.args)
                    else:
                        # No signature info available, fall back to positional-only
                        raise Exception("fallback_to_positional")
                
                # Only use named argument processing if we found actual named arguments
                if named_args:
                    logger.debug(f"Found valid named arguments for {keyword_info.name}: {named_args}")
                    
                    # Create ArgumentSpec from LibDoc signature
                    spec = self._create_argument_spec_from_libdoc(keyword_info.args)
                    
                    # Use Robot Framework's ArgumentResolver to properly handle arguments
                    resolver = ArgumentResolver(spec)
                    resolved_positional, resolved_named = resolver.resolve(positional_args, named_args)
                    
                    # ArgumentResolver might return different types, handle them properly
                    if not isinstance(resolved_named, dict):
                        logger.debug(f"ArgumentResolver returned non-dict for named args: {type(resolved_named)} = {resolved_named}")
                        if hasattr(resolved_named, '__iter__') and not isinstance(resolved_named, str):
                            # Convert list/tuple to dict if possible
                            resolved_named = dict(resolved_named) if resolved_named else {}
                        else:
                            resolved_named = {}
                    
                    # Apply type conversion to resolved arguments
                    converted_positional = self._convert_positional_with_rf(resolved_positional, sig)
                    converted_named = self._convert_named_with_rf(resolved_named, sig)
                    
                    # Execute with both positional and named arguments
                    if converted_named:
                        result = method(*converted_positional, **converted_named)
                    else:
                        result = method(*converted_positional)
                        
                    logger.debug(f"RF native type conversion succeeded for {keyword_info.name} with named args: {list(converted_named.keys()) if converted_named else 'none'}")
                    return ('executed', result)  # Return tuple to indicate execution happened
                else:
                    # Arguments contain '=' but none are valid named arguments (e.g., locator strings)
                    logger.debug(f"Arguments contain '=' but no valid named arguments found for {keyword_info.name}, using positional processing")
                    raise Exception("fallback_to_positional")  # Trigger fallback
                    
            else:
                # No '=' signs detected, use original positional-only logic
                logger.debug(f"No potential named arguments detected for {keyword_info.name}, using positional processing")
                raise Exception("fallback_to_positional")  # Trigger fallback
                
        except Exception as e:
            if str(e) == "fallback_to_positional":
                # Use the original positional-only logic
                logger.debug(f"Falling back to positional-only processing for {keyword_info.name}")
                
                converted_args = []
                param_list = list(sig.parameters.values())
                
                for i, (arg_value, param) in enumerate(zip(original_args, param_list)):
                    if param.annotation != inspect.Parameter.empty:
                        # Create TypeInfo from annotation
                        type_info = TypeInfo.from_type_hint(param.annotation)
                        
                        # Get converter for this type
                        converter = TypeConverter.converter_for(type_info)
                        
                        # BUGFIX: Convert non-string arguments to strings before passing to RF TypeConverter
                        # Robot Framework's TypeConverter expects string input that it converts to other types
                        if not isinstance(arg_value, str):
                            string_arg_value = str(arg_value)
                            logger.debug(f"Converting non-string argument {arg_value} (type: {type(arg_value).__name__}) to string '{string_arg_value}' for RF TypeConverter")
                        else:
                            string_arg_value = arg_value
                        
                        # Convert the argument
                        converted_value = converter.convert(string_arg_value, param.name)
                        converted_args.append(converted_value)
                        
                        logger.debug(f"RF converted arg {i} '{param.name}': {arg_value} -> {converted_value} (type: {type(converted_value).__name__})")
                    else:
                        # No type annotation, use as-is
                        converted_args.append(arg_value)
                
                # Execute with converted arguments
                result = method(*converted_args)
                
                logger.debug(f"RF native type conversion succeeded for {keyword_info.name}")
                return ('executed', result)  # Return tuple to indicate execution happened
            else:
                # Re-raise other exceptions
                raise e
            
        except ImportError as ie:
            logger.debug(f"Robot Framework type conversion not available: {ie}")
            return ('not_available', None)  # Indicate type conversion wasn't available
        except Exception as e:
            logger.debug(f"RF native type conversion failed for {keyword_info.name}: {e}")
            # Log more details for debugging
            logger.debug(f"Method signature: {inspect.signature(method) if 'inspect' in locals() else 'N/A'}")
            logger.debug(f"Original args: {original_args}")
            import traceback
            logger.debug(f"Full traceback: {traceback.format_exc()}")
            # CRITICAL: Even though execution failed, it DID execute - don't try again
            raise e  # Re-raise the exception instead of returning None
    
    def _split_args_into_positional_and_named(self, args: List[str], signature_args: List[str] = None) -> tuple[List[str], Dict[str, str]]:
        """
        Split user arguments into positional and named arguments using LibDoc signature information.
        
        This method reuses the logic from rf_native_type_converter to ensure consistency.
        """
        positional = []
        named = {}
        
        # Build list of valid parameter names from signature
        valid_param_names = set()
        if signature_args:
            for arg_str in signature_args:
                if ':' in arg_str:
                    param_name = arg_str.split(':', 1)[0].strip()
                    if param_name.startswith('*'):
                        param_name = param_name[1:]  # Remove * for varargs
                    if param_name.startswith('*'):
                        param_name = param_name[1:]  # Remove ** for kwargs
                    if param_name and not param_name.startswith('*'):
                        valid_param_names.add(param_name)
        
        for arg in args:
            if '=' in arg and self._looks_like_named_arg(arg, valid_param_names):
                key, value = arg.split('=', 1)
                named[key.strip()] = value
            else:
                positional.append(arg)
        
        return positional, named
    
    def _split_args_using_method_signature(self, original_args: List[str], method_signature) -> Tuple[List[str], Dict[str, str]]:
        """
        Split arguments into positional and named using the actual method signature.
        This is more reliable than using KeywordInfo.args which may be outdated or incorrect.
        """
        positional_args = []
        named_args = {}
        
        # Get parameter names from the actual method signature
        param_names = list(method_signature.parameters.keys())
        
        for arg in original_args:
            if '=' in arg:
                # Potential named argument
                param_name, param_value = arg.split('=', 1)
                
                # Check if this is a valid parameter name for the method
                if param_name in param_names:
                    named_args[param_name] = param_value
                    logger.debug(f"Valid named argument: {param_name}={param_value}")
                else:
                    # Not a valid parameter name - treat as positional (e.g., locator string)
                    positional_args.append(arg)
                    logger.debug(f"Invalid parameter name '{param_name}' - treating '{arg}' as positional")
            else:
                # Regular positional argument
                positional_args.append(arg)
        
        return positional_args, named_args
    
    def _looks_like_named_arg(self, arg: str, valid_param_names: set = None) -> bool:
        """
        Check if an argument looks like a named argument.
        
        Uses valid parameter names from LibDoc signature to distinguish between
        actual named parameters and locator strings containing '=' characters.
        """
        if '=' not in arg:
            return False
        
        key_part = arg.split('=', 1)[0].strip()
        
        # Must be valid Python identifier
        if not key_part.isidentifier():
            return False
        
        # If we have valid parameter names from signature, only treat as named arg
        # if the key matches an actual parameter name
        if valid_param_names:
            return key_part in valid_param_names
        
        # Fallback: assume it's a named argument if it's a valid identifier
        return True
    
    def _create_argument_spec_from_libdoc(self, libdoc_args: List[str]):
        """Create Robot Framework ArgumentSpec from LibDoc signature."""
        from robot.running.arguments import ArgumentSpec
        
        positional_or_named = []
        kw_only = []
        defaults = {}
        var_positional = None
        var_named = None
        keyword_only_separator_found = False
        
        for arg_str in libdoc_args:
            # Handle the special "*" separator for keyword-only arguments
            if arg_str.strip() == '*':
                keyword_only_separator_found = True
                continue
                
            if ':' in arg_str:
                # Extract parameter name and default value
                name, default_part = arg_str.split(':', 1)
                name = name.strip()
                
                # Handle varargs and kwargs
                if name.startswith('**'):
                    var_named = name[2:] if len(name) > 2 else 'kwargs'
                elif name.startswith('*'):
                    var_positional = name[1:] if len(name) > 1 else 'args'
                elif name not in ['*', '**']:  # Only add regular parameters
                    if keyword_only_separator_found:
                        kw_only.append(name)
                    else:
                        positional_or_named.append(name)
                    
                    # Extract default value if present
                    if '=' in default_part:
                        defaults[name] = default_part.split('=', 1)[1].strip()
        
        return ArgumentSpec(
            positional_or_named=positional_or_named,
            named_only=kw_only,
            defaults=defaults,
            var_positional=var_positional,
            var_named=var_named
        )
    
    def _convert_positional_with_rf(self, args: List[str], signature) -> List[Any]:
        """Convert positional arguments using RF type conversion."""
        from robot.running.arguments.typeconverters import TypeConverter
        from robot.running.arguments.typeinfo import TypeInfo
        
        converted_args = []
        param_list = list(signature.parameters.values())
        
        for i, arg_value in enumerate(args):
            if i < len(param_list):
                param = param_list[i]
                if param.annotation != param.empty:
                    # Create TypeInfo from annotation
                    type_info = TypeInfo.from_type_hint(param.annotation)
                    
                    # Get converter for this type
                    converter = TypeConverter.converter_for(type_info)
                    
                    # Convert the argument
                    converted_value = converter.convert(arg_value, param.name)
                    converted_args.append(converted_value)
                    
                    logger.debug(f"RF converted positional arg {i} '{param.name}': {arg_value} -> {converted_value} (type: {type(converted_value).__name__})")
                else:
                    # No type annotation, use as-is
                    converted_args.append(arg_value)
            else:
                # More arguments than parameters, use as-is
                converted_args.append(arg_value)
        
        return converted_args
    
    def _convert_named_with_rf(self, named_args: Dict[str, str], signature) -> Dict[str, Any]:
        """Convert named arguments using RF type conversion."""
        from robot.running.arguments.typeconverters import TypeConverter
        from robot.running.arguments.typeinfo import TypeInfo
        
        converted_named = {}
        param_dict = {param.name: param for param in signature.parameters.values()}
        
        for name, value in named_args.items():
            if name in param_dict:
                param = param_dict[name]
                if param.annotation != param.empty:
                    # Create TypeInfo from annotation
                    type_info = TypeInfo.from_type_hint(param.annotation)
                    
                    # Get converter for this type
                    converter = TypeConverter.converter_for(type_info)
                    
                    # Convert the argument
                    converted_value = converter.convert(value, name)
                    converted_named[name] = converted_value
                    
                    logger.debug(f"RF converted named arg '{name}': {value} -> {converted_value} (type: {type(converted_value).__name__})")
                else:
                    # No type annotation, use as-is
                    converted_named[name] = value
            else:
                # Unknown parameter, use as-is
                converted_named[name] = value
        
        return converted_named
    
    def get_keyword_suggestions(self, keyword_name: str, limit: int = 5) -> List[str]:
        """Get keyword suggestions based on partial match."""
        return self.keyword_discovery.get_keyword_suggestions(keyword_name, limit)
    
    def suggest_similar_keywords(self, keyword_name: str, max_suggestions: int = 5) -> List[KeywordInfo]:
        """Suggest similar keywords based on name similarity."""
        # This is a more sophisticated version that returns KeywordInfo objects
        suggestions = []
        keyword_lower = keyword_name.lower()
        
        for cached_name, keyword_info in self.keyword_discovery.keyword_cache.items():
            score = self._similarity_score(keyword_lower, cached_name)
            if score > 0.3:  # Minimum similarity threshold
                suggestions.append((score, keyword_info))
        
        # Sort by similarity score and return top suggestions
        suggestions.sort(key=lambda x: x[0], reverse=True)
        return [info for _, info in suggestions[:max_suggestions]]
    
    def search_keywords(self, pattern: str) -> List[KeywordInfo]:
        """Search for keywords matching a pattern."""
        import re
        try:
            regex = re.compile(pattern, re.IGNORECASE)
            matches = []
            for keyword_info in self.keyword_discovery.keyword_cache.values():
                if (regex.search(keyword_info.name) or 
                    regex.search(keyword_info.doc) or 
                    regex.search(keyword_info.library)):
                    matches.append(keyword_info)
            return matches
        except re.error:
            # If pattern is not valid regex, do simple string matching
            pattern_lower = pattern.lower()
            return [info for info in self.keyword_discovery.keyword_cache.values() 
                   if pattern_lower in info.name.lower() or 
                      pattern_lower in info.doc.lower() or 
                      pattern_lower in info.library.lower()]
    
    def get_keywords_by_library(self, library_name: str) -> List[KeywordInfo]:
        """Get all keywords from a specific library."""
        return self.keyword_discovery.get_keywords_by_library(library_name)
    
    def get_all_keywords(self) -> List[KeywordInfo]:
        """Get all cached keywords."""
        return self.keyword_discovery.get_all_keywords()
    
    def get_keyword_count(self) -> int:
        """Get total number of cached keywords."""
        return self.keyword_discovery.get_keyword_count()
    
    def is_dom_changing_keyword(self, keyword_name: str) -> bool:
        """Check if a keyword likely changes the DOM."""
        return self.keyword_discovery.is_dom_changing_keyword(keyword_name)
    
    # Argument processing methods
    def parse_arguments(self, args: List[str]) -> ParsedArguments:
        """Parse a list of arguments into positional and named arguments."""
        return self.argument_processor.parse_arguments(args)
    
    def _parse_arguments(self, args: List[str]) -> ParsedArguments:
        """Parse Robot Framework-style arguments (internal method for compatibility)."""
        return self.argument_processor.parse_arguments(args)
    
    def _parse_arguments_for_keyword(self, keyword_name: str, args: List[str], library_name: str = None) -> ParsedArguments:
        """Parse arguments using LibDoc information for a specific keyword."""
        return self.argument_processor.parse_arguments_for_keyword(keyword_name, args, library_name)
    
    def _parse_arguments_with_rf_spec(self, keyword_info: KeywordInfo, args: List[str]) -> ParsedArguments:
        """Parse arguments using Robot Framework's native ArgumentSpec if available."""
        try:
            from robot.running.arguments import ArgumentSpec
            from robot.running.arguments.argumentresolver import ArgumentResolver
            
            # Try to create ArgumentSpec from keyword info
            if hasattr(keyword_info, 'args') and keyword_info.args:
                spec = ArgumentSpec(
                    positional_or_named=keyword_info.args,
                    defaults=keyword_info.defaults if hasattr(keyword_info, 'defaults') else {}
                )
                
                # Use Robot Framework's ArgumentResolver to split arguments
                resolver = ArgumentResolver(spec, resolve_named=True)
                positional, named = resolver.resolve(args, named_args=None)
                
                # Convert to our ParsedArguments format
                parsed = ParsedArguments()
                parsed.positional = positional
                parsed.named = {k: v for k, v in named.items()} if named else {}
                
                return parsed
                
        except (ImportError, Exception) as e:
            logger.debug(f"RF ArgumentSpec parsing failed: {e}, using fallback parsing")
            
        # Fall back to our custom parsing logic
        return self._parse_arguments(args)
    
    
    
    # Library management methods
    def get_library_exclusion_info(self) -> Dict[str, Any]:
        """Get information about library exclusions."""
        return self.library_manager.get_library_exclusion_info()
    
    def get_library_status(self) -> Dict[str, Any]:
        """Get status of all libraries."""
        return {
            "loaded_libraries": {
                name: {
                    "keywords": len(lib.keywords),
                    "doc": lib.doc,
                    "version": lib.version,
                    "scope": lib.scope
                }
                for name, lib in self.library_manager.libraries.items()
            },
            "failed_imports": self.library_manager.failed_imports,
            "total_keywords": len(self.keyword_discovery.keyword_cache)
        }
    
    async def _ensure_session_libraries(self, session_id: str, keyword_name: str) -> None:
        """Ensure required libraries are loaded for the session."""
        if not self.session_manager:
            logger.debug("No session manager available, skipping session library loading")
            return
            
        session = self.session_manager.get_session(session_id)
        if not session:
            session = self.session_manager.create_session(session_id)
        
        # Get libraries that should be loaded for this session
        required_libraries = session.get_libraries_to_load()
        optional_libraries = session.get_optional_libraries()
        
        # Load any missing required libraries
        libraries_to_load = []
        for lib_name in required_libraries:
            if lib_name not in self.library_manager.libraries:
                libraries_to_load.append(lib_name)
        
        if libraries_to_load:
            self.library_manager.load_session_libraries(libraries_to_load, self.keyword_discovery)
            
            # Add new keywords to cache
            for lib_name in libraries_to_load:
                if lib_name in self.library_manager.libraries:
                    lib_info = self.library_manager.libraries[lib_name]
                    self.keyword_discovery.add_keywords_to_cache(lib_info)
                    session.mark_library_loaded(lib_name)
        
        # Try to load library on-demand if keyword is not found
        if not self.find_keyword(keyword_name):
            # Try to determine which library might have this keyword, respecting session context
            potential_library = self._guess_library_for_keyword(keyword_name, session)
            if potential_library and potential_library not in self.library_manager.libraries:
                if self.library_manager.load_library_on_demand(potential_library, self.keyword_discovery):
                    lib_info = self.library_manager.libraries[potential_library]
                    self.keyword_discovery.add_keywords_to_cache(lib_info)
                    session.mark_library_loaded(potential_library)
    
    def _guess_library_for_keyword(self, keyword_name: str, session: 'ExecutionSession' = None) -> Optional[str]:
        """Guess which library might contain a keyword based on name patterns, respecting session context."""
        keyword_lower = keyword_name.lower()
        
        # If session has a specific web automation library, respect it for browser keywords
        if session:
            web_lib = session.get_web_automation_library()
            if web_lib and any(term in keyword_lower for term in ['browser', 'click', 'fill', 'navigate', 'page', 'screenshot']):
                # Session has explicit web automation library - use it instead of guessing
                logger.debug(f"Session has {web_lib}, using it for '{keyword_name}' instead of auto-detection")
                return web_lib
        
        # Common keyword patterns to library mappings
        patterns = {
            r'\b(click|fill|navigate|browser|page|screenshot)\b': 'Browser',
            r'\b(get request|post|put|delete|create session)\b': 'RequestsLibrary',
            r'\b(parse xml|get element|xpath)\b': 'XML',
            r'\b(run process|start process|terminate)\b': 'Process',
            r'\b(create file|remove file|directory)\b': 'OperatingSystem',
            r'\b(get current date|convert date)\b': 'DateTime'
        }
        
        for pattern, library in patterns.items():
            if re.search(pattern, keyword_lower):
                return library
        
        return None
    
    def _find_keyword_with_session(self, keyword_name: str, active_library: str = None, session_id: str = None) -> Optional[KeywordInfo]:
        """Find keyword respecting session search order with strict boundary enforcement."""
        # If no session or session manager, use normal search
        if not session_id or not self.session_manager:
            return self.find_keyword(keyword_name, active_library)
        
        session = self.session_manager.get_session(session_id)
        if not session:
            return self.find_keyword(keyword_name, active_library)
        
        # Get session configuration
        search_order = session.get_search_order()
        session_type = session.get_session_type()
        
        logger.debug(f"Session '{session_id}' search order: {search_order}, type: {session_type.value}")
        
        # CRITICAL FIX: Validate active_library against session boundaries
        if active_library and active_library not in search_order:
            logger.warning(f"Active library '{active_library}' not in session '{session_id}' search order {search_order}")
            # For typed sessions, strictly enforce boundaries
            if session_type.value != "unknown":
                logger.info(f"Strict mode: ignoring out-of-bounds active_library '{active_library}' for session type '{session_type.value}'")
                active_library = None
        
        # Search in session search order with exact matches first
        for lib_name in search_order:
            if lib_name in self.library_manager.libraries:
                lib_keywords = self.get_keywords_by_library(lib_name)
                for kw in lib_keywords:
                    if kw.name.lower() == keyword_name.lower():
                        logger.info(f"Found '{keyword_name}' in '{lib_name}' via session search order (type: {session_type.value})")
                        return kw
        
        # Try fuzzy matching within session boundaries
        normalized = keyword_name.lower().strip()
        variations = [
            normalized.replace(' ', ''),   # Remove spaces
            normalized.replace('_', ' '),  # Replace underscores
            normalized.replace('-', ' '),  # Replace hyphens
        ]
        
        for lib_name in search_order:
            if lib_name in self.library_manager.libraries:
                lib_keywords = self.get_keywords_by_library(lib_name)
                for variation in variations:
                    for kw in lib_keywords:
                        if kw.name.lower().replace(' ', '') == variation:
                            logger.info(f"Found '{keyword_name}' in '{lib_name}' via fuzzy search order match (type: {session_type.value})")
                            return kw
        
        # REMOVED: No fallback to normal search - respect session boundaries strictly
        logger.info(f"Keyword '{keyword_name}' not found within session '{session_id}' boundaries (type: {session_type.value}, search_order: {search_order})")
        return None
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a session."""
        if not self.session_manager:
            return None
        session = self.session_manager.get_session(session_id)
        if not session:
            return None
        return session.get_session_info()
    
    async def _update_rf_search_order(self, session) -> None:
        """Update Robot Framework's native library search order."""
        try:
            # Get BuiltIn library instance to call Set Library Search Order
            if 'BuiltIn' in self.library_manager.libraries:
                builtin_lib = self.library_manager.libraries['BuiltIn']
                builtin_instance = builtin_lib.instance
                
                # Get current search order from session
                search_order = session.get_search_order()
                
                # Filter to only include loaded libraries
                loaded_search_order = [lib for lib in search_order if lib in self.library_manager.libraries]
                
                if loaded_search_order and hasattr(builtin_instance, 'set_library_search_order'):
                    # Use Robot Framework's native Set Library Search Order
                    builtin_instance.set_library_search_order(*loaded_search_order)
                    logger.debug(f"Updated RF search order: {loaded_search_order}")
        except Exception as e:
            logger.debug(f"Could not update RF search order: {e}")
    
    def create_session(self, session_id: str) -> Dict[str, Any]:
        """Create a new session."""
        if not self.session_manager:
            return {"error": "Session manager not available"}
        session = self.session_manager.create_session(session_id)
        return session.get_session_info()
    
    def _parse_library_prefix(self, keyword_name: str) -> tuple[Optional[str], Optional[str]]:
        """Parse library prefix from keyword name (e.g., 'XML.Get Element Count' -> ('XML', 'Get Element Count'))."""
        if '.' not in keyword_name:
            return None, None
        
        parts = keyword_name.split('.', 1)
        if len(parts) == 2:
            library_name, keyword_part = parts
            # Validate that library_name looks like a valid library name
            if library_name and keyword_part and library_name.replace('_', '').replace(' ', '').isalnum():
                return library_name, keyword_part
        
        return None, None
    
    async def _ensure_library_loaded(self, library_name: str) -> bool:
        """Ensure a specific library is loaded."""
        if library_name in self.library_manager.libraries:
            return True
        
        # Try to load the library on demand
        success = self.library_manager.load_library_on_demand(library_name, self.keyword_discovery)
        if success:
            # Add keywords to cache
            lib_info = self.library_manager.libraries[library_name]
            self.keyword_discovery.add_keywords_to_cache(lib_info)
            logger.info(f"Loaded library '{library_name}' for explicit prefix")
            return True
        
        logger.warning(f"Could not load library '{library_name}' for prefix")
        return False
    
    def _find_keyword_with_library_prefix(self, keyword_name: str, library_name: str) -> Optional[KeywordInfo]:
        """Find keyword in a specific library only."""
        if library_name not in self.library_manager.libraries:
            logger.debug(f"Library '{library_name}' not loaded for prefix search")
            return None
        
        # Search only in the specified library
        lib_keywords = self.get_keywords_by_library(library_name)
        for kw in lib_keywords:
            if kw.name.lower() == keyword_name.lower():
                logger.debug(f"Found '{keyword_name}' in '{library_name}' via explicit prefix")
                return kw
        
        # Try fuzzy matching within the library
        normalized = keyword_name.lower().strip()
        variations = [
            normalized.replace(' ', ''),   # Remove spaces
            normalized.replace('_', ' '),  # Replace underscores
            normalized.replace('-', ' '),  # Replace hyphens
        ]
        
        for variation in variations:
            for kw in lib_keywords:
                if kw.name.lower().replace(' ', '') == variation:
                    logger.debug(f"Found '{keyword_name}' in '{library_name}' via fuzzy prefix match")
                    return kw
        
        logger.debug(f"Keyword '{keyword_name}' not found in library '{library_name}'")
        return None
    
    def set_session_search_order(self, session_id: str, search_order: List[str]) -> bool:
        """Manually set search order for a session."""
        if not self.session_manager:
            return False
        session = self.session_manager.get_session(session_id)
        if not session:
            return False
        
        session.search_order = search_order.copy()
        
        # Update Robot Framework's native search order
        try:
            import asyncio
            asyncio.create_task(self._update_rf_search_order(session))
        except Exception as e:
            logger.debug(f"Could not update search order: {e}")
        
        return True
    
    # Properties for backward compatibility and access to internal components
    @property
    def libraries(self) -> Dict[str, Any]:
        """Access to loaded libraries."""
        return self.library_manager.libraries
    
    @property
    def keyword_cache(self) -> Dict[str, KeywordInfo]:
        """Access to keyword cache."""
        return self.keyword_discovery.keyword_cache
    
    @property
    def failed_imports(self) -> Dict[str, str]:
        """Access to failed imports."""
        return self.library_manager.failed_imports
    
    @property
    def excluded_libraries(self) -> set:
        """Access to excluded libraries."""
        return self.library_manager.excluded_libraries
    
    # Utility methods
    def _similarity_score(self, a: str, b: str) -> float:
        """Calculate similarity score between two strings."""
        if not a or not b:
            return 0.0
        
        # Simple similarity based on common substring length
        a, b = a.lower(), b.lower()
        if a == b:
            return 1.0
        
        # Check for substring matches
        shorter, longer = (a, b) if len(a) <= len(b) else (b, a)
        if shorter in longer:
            return len(shorter) / len(longer)
        
        # Calculate based on common characters
        common = sum(1 for char in shorter if char in longer)
        return common / max(len(a), len(b))
    
    # Execution methods (delegated from the original implementation)
    def _execute_direct_method_call(self, keyword_info: KeywordInfo, parsed_args: ParsedArguments, original_args: List[str], session_variables: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a keyword by calling its method directly."""
        try:
            # Get library instance
            if keyword_info.library not in self.libraries:
                return {
                    "success": False,
                    "error": f"Library '{keyword_info.library}' is not loaded. Available libraries: {list(self.libraries.keys())}",
                    "keyword_info": {
                        "name": keyword_info.name,
                        "library": keyword_info.library,
                        "args": keyword_info.args,
                        "doc": keyword_info.doc
                    }
                }
            
            library = self.libraries[keyword_info.library]
            
            if library.instance is None:
                return {
                    "success": False,
                    "error": f"Library '{keyword_info.library}' instance is not initialized",
                    "keyword_info": {
                        "name": keyword_info.name,
                        "library": keyword_info.library,
                        "args": keyword_info.args,
                        "doc": keyword_info.doc
                    }
                }
            
            method = getattr(library.instance, keyword_info.method_name)
            
            # Handle different types of method calls
            if keyword_info.is_builtin and hasattr(library.instance, '_context'):
                # BuiltIn library methods might need context
                # BUGFIX: Convert non-string arguments to strings for Robot Framework execution
                # Robot Framework expects string arguments that it converts to appropriate types
                string_args = []
                for arg in original_args:
                    if not isinstance(arg, str):
                        string_arg = str(arg)
                        logger.debug(f"Converting non-string argument {arg} (type: {type(arg).__name__}) to string '{string_arg}' for BuiltIn method with context")
                        string_args.append(string_arg)
                    else:
                        string_args.append(arg)
                
                result = method(*string_args)
            else:
                # Regular library methods - use centralized type conversion configuration
                from robotmcp.config.library_registry import get_libraries_requiring_type_conversion
                type_conversion_libraries = get_libraries_requiring_type_conversion()
                
                if keyword_info.library in type_conversion_libraries:
                    # Enhanced logging for named arguments debugging
                    has_potential_named_args = any('=' in arg for arg in original_args)
                    logger.debug(f"NAMED_ARGS_DEBUG: {keyword_info.name} from {keyword_info.library} - args={original_args}, has_potential_named={has_potential_named_args}")
                    
                    try:
                        # Use Robot Framework's native type conversion system for libraries that need it
                        conversion_result = self._execute_with_rf_type_conversion(method, keyword_info, original_args)
                        logger.debug(f"NAMED_ARGS_DEBUG: Type conversion result for {keyword_info.name}: {conversion_result[0] if conversion_result else 'None'}")
                        if conversion_result[0] == 'executed':  # Successfully converted and executed
                            result = conversion_result[1]  # Use the result as-is
                        elif conversion_result[0] == 'not_available':
                            # Type conversion not available, fallback to our argument processing
                            parsed = self.argument_processor.parse_arguments_for_keyword(keyword_info.name, original_args, keyword_info.library)
                            pos_args = parsed.positional
                            kwargs = parsed.named
                            
                            if kwargs:
                                result = method(*pos_args, **kwargs)
                            else:
                                result = method(*pos_args)
                    except Exception as lib_error:
                        logger.debug(f"{keyword_info.library} execution failed: {lib_error}")
                        # NAMED ARGUMENTS FIX: Instead of re-raising, try the parsed arguments approach
                        # This ensures named arguments are preserved when type conversion fails
                        logger.info(f"Type conversion failed for {keyword_info.name}, falling back to parsed argument processing")
                        parsed = self.argument_processor.parse_arguments_for_keyword(keyword_info.name, original_args, keyword_info.library)
                        pos_args = parsed.positional
                        kwargs = parsed.named
                        
                        logger.debug(f"Fallback execution: positional={pos_args}, named={list(kwargs.keys()) if kwargs else 'none'}")
                        
                        if kwargs:
                            result = method(*pos_args, **kwargs)
                            logger.debug(f"Successfully executed {keyword_info.name} with fallback named arguments")
                        else:
                            result = method(*pos_args)
                            logger.debug(f"Successfully executed {keyword_info.name} with fallback positional arguments")
                elif keyword_info.name == "Create List":
                    # Collections.Create List takes variable arguments
                    result = method(*parsed_args.positional)
                elif keyword_info.name == "Set Variable":
                    # Set Variable takes one argument
                    value = parsed_args.positional[0] if parsed_args.positional else None
                    result = method(value)
                else:
                    # OBJECT ARGUMENTS FIX: Libraries like XML, RequestsLibrary, Collections need original object arguments, not string conversions
                    libraries_needing_objects = ["XML", "RequestsLibrary", "Collections"]
                    
                    if keyword_info.library in libraries_needing_objects:
                        # Use original arguments to preserve object types (e.g., XML Elements)
                        logger.debug(f"Object-preserving execution for {keyword_info.name} in {keyword_info.library}: using original args")
                        if parsed_args.named:
                            result = method(*original_args, **parsed_args.named)
                            logger.debug(f"Successfully executed {keyword_info.name} with original args + named arguments")
                        else:
                            result = method(*original_args)
                            logger.debug(f"Successfully executed {keyword_info.name} with original args only")
                    else:
                        # NAMED ARGUMENTS FIX: For other libraries, check for named arguments
                        # This was the critical bug - line was ignoring named arguments completely
                        logger.debug(f"Standard execution path for {keyword_info.name}: positional={parsed_args.positional}, named={list(parsed_args.named.keys()) if parsed_args.named else 'none'}")
                        
                        if parsed_args.named:
                            result = method(*parsed_args.positional, **parsed_args.named)
                            logger.debug(f"Successfully executed {keyword_info.name} with named arguments: {list(parsed_args.named.keys())}")
                        else:
                            result = method(*parsed_args.positional)
                            logger.debug(f"Successfully executed {keyword_info.name} with positional arguments only")
            
            return {
                "success": True,
                "output": str(result) if result is not None else f"Executed {keyword_info.name}",
                "result": result,
                "keyword_info": {
                    "name": keyword_info.name,
                    "library": keyword_info.library,
                    "doc": keyword_info.doc
                }
            }
            
        except Exception as e:
            import traceback
            logger.debug(f"Full traceback for {keyword_info.library}.{keyword_info.name}: {traceback.format_exc()}")
            return {
                "success": False,
                "error": f"Error executing {keyword_info.library}.{keyword_info.name}: {str(e)}",
                "keyword_info": {
                    "name": keyword_info.name,
                    "library": keyword_info.library,
                    "args": keyword_info.args,
                    "doc": keyword_info.doc
                }
            }
    
    async def execute_keyword(self, keyword_name: str, args: List[str], session_variables: Dict[str, Any] = None, active_library: str = None, session_id: str = None, library_prefix: str = None) -> Dict[str, Any]:
        """Execute a keyword dynamically with session-based library management and optional library prefix support."""
        # Parse library prefix from keyword name if present (e.g., "XML.Get Element Count")
        parsed_library, parsed_keyword = self._parse_library_prefix(keyword_name)
        
        # Determine effective library prefix (parameter overrides parsed)
        effective_library_prefix = library_prefix or parsed_library
        effective_keyword_name = parsed_keyword or keyword_name
        # Handle session-based library loading
        if session_id:
            await self._ensure_session_libraries(session_id, effective_keyword_name)
        
        # Handle library prefix loading if specified
        if effective_library_prefix:
            await self._ensure_library_loaded(effective_library_prefix)
        
        # Find keyword with library prefix, session search order, or active library filtering
        if effective_library_prefix:
            keyword_info = self._find_keyword_with_library_prefix(effective_keyword_name, effective_library_prefix)
        else:
            keyword_info = self._find_keyword_with_session(effective_keyword_name, active_library, session_id)
        
        if not keyword_info:
            if effective_library_prefix:
                error_msg = f"Keyword '{effective_keyword_name}' not found in library '{effective_library_prefix}'"
            else:
                error_msg = f"Keyword '{effective_keyword_name}' not found"
                if active_library:
                    error_msg += f" in active library '{active_library}' or built-in libraries"
                else:
                    error_msg += " in any loaded library"
                
            return {
                "success": False,
                "error": error_msg,
                "suggestions": self.get_keyword_suggestions(effective_keyword_name, 3),
                "library_prefix": effective_library_prefix,
                "active_library_filter": active_library,
                "session_id": session_id
            }
        
        # Record keyword usage for session management and update search order
        if session_id:
            session = self.session_manager.get_session(session_id)
            if session:
                # Record the base keyword name (without library prefix) for session detection
                session.record_keyword_usage(effective_keyword_name)
                # Update Robot Framework's native search order
                await self._update_rf_search_order(session)
        
        try:
            # Log which library the keyword was found in for debugging
            if active_library and keyword_info.library != active_library:
                logger.debug(f"Using built-in keyword '{keyword_info.name}' from {keyword_info.library} (active library: {active_library})")
            else:
                logger.debug(f"Executing keyword '{keyword_info.name}' from {keyword_info.library}")
            
            # Parse arguments using LibDoc information for accuracy
            # BUGFIX: Convert all arguments to strings before parsing since Robot Framework expects string inputs
            string_args = []
            for arg in args:
                if not isinstance(arg, str):
                    string_arg = str(arg)
                    logger.debug(f"Converting non-string argument {arg} (type: {type(arg).__name__}) to string '{string_arg}' for RF argument parsing")
                    string_args.append(string_arg)
                else:
                    string_args.append(arg)
            
            parsed_args = self._parse_arguments_for_keyword(effective_keyword_name, string_args, keyword_info.library)
            
            # Enhanced debug logging for named arguments
            logger.debug(f"NAMED_ARGS_DEBUG: Parsed arguments for {effective_keyword_name}: positional={parsed_args.positional}, named={list(parsed_args.named.keys()) if parsed_args.named else 'none'}")
            
            # Execute the keyword
            result = self._execute_direct_method_call(keyword_info, parsed_args, args, session_variables or {})
            result["session_id"] = session_id
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing {effective_keyword_name}: {str(e)}",
                "library_prefix": effective_library_prefix,
                "keyword_info": {
                    "name": keyword_info.name,
                    "library": keyword_info.library,
                    "doc": keyword_info.doc
                },
                "active_library_filter": active_library,
                "session_id": session_id
            }


# Global instance management
_keyword_discovery = None


def get_keyword_discovery() -> DynamicKeywordDiscovery:
    """Get the global keyword discovery instance."""
    global _keyword_discovery
    if _keyword_discovery is None:
        _keyword_discovery = DynamicKeywordDiscovery()
    return _keyword_discovery