#!/usr/bin/env python3
"""
Comprehensive test suite for AutoIt parser
"""
import pytest
import tempfile
import os
from pathlib import Path

from claude_code_indexer.parsers.autoit_parser import AutoItParser
from claude_code_indexer.parsers.base_parser import ParseResult


class TestAutoItParser:
    """Test suite for AutoIt parser functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.parser = AutoItParser()
    
    def test_file_extension_support(self):
        """Test that parser recognizes AutoIt file extensions"""
        assert self.parser.can_parse("test.au3")
        assert self.parser.can_parse("script.aut")
        assert self.parser.can_parse("compiled.a3x")
        assert not self.parser.can_parse("test.py")
        assert not self.parser.can_parse("script.js")
    
    def test_supported_extensions(self):
        """Test supported extensions list"""
        extensions = self.parser.get_supported_extensions()
        assert ".au3" in extensions
        assert ".aut" in extensions
        assert ".a3x" in extensions
        assert len(extensions) == 3
    
    def test_simple_function_parsing(self):
        """Test parsing of simple AutoIt functions"""
        autoit_code = '''
        #include <MsgBoxConstants.au3>
        
        Global $g_sMessage = "Hello World"
        
        Func Main()
            MsgBox($MB_OK, "Test", $g_sMessage)
        EndFunc
        
        Main()
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.au3', delete=False) as f:
            f.write(autoit_code)
            temp_file = f.name
        
        try:
            result = self.parser.parse_file(temp_file)
            
            assert result.success
            assert result.language == "autoit"
            
            # Check for expected nodes
            functions = [n for n in result.nodes.values() if n.node_type == 'function']
            imports = [n for n in result.nodes.values() if n.node_type == 'import']
            variables = [n for n in result.nodes.values() if n.node_type == 'variable']
            
            assert len(functions) >= 1
            assert any(f.name == 'Main' for f in functions)
            assert len(imports) >= 1
            assert any(i.name == 'MsgBoxConstants.au3' for i in imports)
            assert len(variables) >= 1
            assert any(v.name == '$g_sMessage' for v in variables)
            
        finally:
            os.unlink(temp_file)
    
    def test_complex_autoit_script(self):
        """Test parsing of complex AutoIt script with GUI elements"""
        autoit_code = '''
        #include <GUIConstantsEx.au3>
        #include <WindowsConstants.au3>
        #include <ButtonConstants.au3>
        
        ; Global variables
        Global $g_hMainGUI
        Global $g_idButton
        Global $g_sTitle = "AutoIt Test Application"
        
        ; Main function
        Func Main()
            Local $aData[10]
            $g_hMainGUI = CreateMainWindow()
            ShowMainWindow()
            RunMessageLoop()
        EndFunc
        
        Func CreateMainWindow()
            Local $hGUI = GUICreate($g_sTitle, 400, 300)
            Local $idLabel = GUICtrlCreateLabel("Welcome!", 10, 10)
            $g_idButton = GUICtrlCreateButton("Click Me", 10, 50, 100, 30)
            Return $hGUI
        EndFunc
        
        Func ShowMainWindow()
            GUISetState(@SW_SHOW, $g_hMainGUI)
        EndFunc
        
        Func RunMessageLoop()
            While 1
                Local $nMsg = GUIGetMsg()
                If $nMsg = $GUI_EVENT_CLOSE Then
                    ExitLoop
                ElseIf $nMsg = $g_idButton Then
                    OnButtonClick()
                EndIf
            WEnd
        EndFunc
        
        Func OnButtonClick()
            ; Create COM object
            Local $oExcel = ObjCreate("Excel.Application")
            MsgBox($MB_OK, "Info", "Button clicked!")
        EndFunc
        
        ; Hotkey setup
        HotKeySet("{ESC}", "ExitApp")
        
        Func ExitApp()
            Exit
        EndFunc
        
        ; Start the application
        Main()
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.au3', delete=False) as f:
            f.write(autoit_code)
            temp_file = f.name
        
        try:
            result = self.parser.parse_file(temp_file)
            
            assert result.success
            assert result.language == "autoit"
            
            # Count node types
            node_counts = {}
            for node in result.nodes.values():
                node_counts[node.node_type] = node_counts.get(node.node_type, 0) + 1
            
            # Verify expected node types and minimum counts
            assert node_counts.get('function', 0) >= 6  # Main, CreateMainWindow, ShowMainWindow, etc.
            assert node_counts.get('import', 0) >= 3   # Three includes
            assert node_counts.get('variable', 0) >= 3  # Global and local variables
            assert node_counts.get('gui_control', 0) >= 2  # Label and Button
            assert node_counts.get('com_object', 0) >= 1   # Excel object
            assert node_counts.get('hotkey', 0) >= 1       # ESC hotkey
            
            # Check specific function names
            function_names = [n.name for n in result.nodes.values() if n.node_type == 'function']
            expected_functions = ['Main', 'CreateMainWindow', 'ShowMainWindow', 'RunMessageLoop', 'OnButtonClick', 'ExitApp']
            for func_name in expected_functions:
                assert func_name in function_names, f"Function {func_name} not found"
            
            # Check relationships
            assert len(result.relationships) > 0
            
            # Check for imports
            import_names = [n.name for n in result.nodes.values() if n.node_type == 'import']
            expected_imports = ['GUIConstantsEx.au3', 'WindowsConstants.au3', 'ButtonConstants.au3']
            for import_name in expected_imports:
                assert import_name in import_names, f"Import {import_name} not found"
            
        finally:
            os.unlink(temp_file)
    
    def test_variable_scope_detection(self):
        """Test that parser correctly identifies variable scopes"""
        autoit_code = '''
        Global $g_GlobalVar = "global"
        
        Func TestFunction()
            Local $sLocalVar = "local"
            Global $g_AnotherGlobal = "another global"
            Return $sLocalVar
        EndFunc
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.au3', delete=False) as f:
            f.write(autoit_code)
            temp_file = f.name
        
        try:
            result = self.parser.parse_file(temp_file)
            
            variables = [n for n in result.nodes.values() if n.node_type == 'variable']
            
            # Find specific variables and check their scope
            global_vars = [v for v in variables if v.attributes.get('scope') == 'global']
            local_vars = [v for v in variables if v.attributes.get('scope') == 'local']
            
            assert len(global_vars) >= 2  # $g_GlobalVar and $g_AnotherGlobal
            assert len(local_vars) >= 1   # $sLocalVar
            
            global_names = [v.name for v in global_vars]
            local_names = [v.name for v in local_vars]
            
            assert '$g_GlobalVar' in global_names
            assert '$g_AnotherGlobal' in global_names
            assert '$sLocalVar' in local_names
            
        finally:
            os.unlink(temp_file)
    
    def test_empty_file(self):
        """Test parsing of empty AutoIt file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.au3', delete=False) as f:
            f.write("")
            temp_file = f.name
        
        try:
            result = self.parser.parse_file(temp_file)
            
            assert result.success
            assert result.language == "autoit"
            # Should have at least a file node
            assert len(result.nodes) >= 1
            file_nodes = [n for n in result.nodes.values() if n.node_type == 'file']
            assert len(file_nodes) == 1
            
        finally:
            os.unlink(temp_file)
    
    def test_malformed_autoit_file(self):
        """Test handling of malformed AutoIt syntax"""
        autoit_code = '''
        Func UnclosedFunction(
            ; This function is not properly closed
            Local $incomplete
        
        #include without proper syntax
        Global $var_without_value
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.au3', delete=False) as f:
            f.write(autoit_code)
            temp_file = f.name
        
        try:
            result = self.parser.parse_file(temp_file)
            
            # Parser should still succeed but with limited nodes
            assert result.success
            # Should still extract what it can parse
            assert len(result.nodes) > 0
            
        finally:
            os.unlink(temp_file)
    
    def test_case_insensitive_keywords(self):
        """Test that parser handles AutoIt's case-insensitive nature"""
        autoit_code = '''
        func TestFunction()
            local $var = "test"
            GLOBAL $GLOBAL_VAR = "GLOBAL"
        endfunc
        
        FUNC AnotherFunction()
            LOCAL $another = "value"
        ENDFUNC
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.au3', delete=False) as f:
            f.write(autoit_code)
            temp_file = f.name
        
        try:
            result = self.parser.parse_file(temp_file)
            
            assert result.success
            
            # Should find both functions regardless of case
            functions = [n for n in result.nodes.values() if n.node_type == 'function']
            function_names = [f.name for f in functions]
            
            assert 'TestFunction' in function_names
            assert 'AnotherFunction' in function_names
            
            # Should find variables regardless of case
            variables = [n for n in result.nodes.values() if n.node_type == 'variable']
            assert len(variables) >= 3
            
        finally:
            os.unlink(temp_file)
    
    def test_nonexistent_file(self):
        """Test handling of nonexistent file"""
        result = self.parser.parse_file("nonexistent_file.au3")
        assert not result.success
        assert result.error_message is not None
        assert "not found" in result.error_message.lower() or "no such file" in result.error_message.lower()


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])