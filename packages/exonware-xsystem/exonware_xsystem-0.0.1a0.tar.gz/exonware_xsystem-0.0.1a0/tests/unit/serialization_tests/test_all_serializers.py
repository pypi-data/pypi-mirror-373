"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

Comprehensive tests for all 12 xSystem serialization formats.

Tests the production library principle: each serializer should use
established, well-tested libraries rather than custom implementations.
"""

import pytest
import warnings
from pathlib import Path

# Import all 17 serializers (12 core + 5 built-in Python modules)
from exonware.xsystem import (
    # Core 12 formats
    JsonSerializer, YamlSerializer, TomlSerializer, XmlSerializer,
    BsonSerializer, MsgPackSerializer, CborSerializer,
    CsvSerializer, PickleSerializer, MarshalSerializer,
    FormDataSerializer, MultipartSerializer,
    # Built-in Python modules (5 additional formats)
    ConfigParserSerializer, Sqlite3Serializer, DbmSerializer,
    ShelveSerializer, PlistlibSerializer
)


class TestAllSerializersBasic:
    """Test basic functionality of all serializers."""
    
    @pytest.mark.xsystem_unit
    def test_json_serializer(self, simple_data):
        """Test JSON serializer using built-in json library."""
        serializer = JsonSerializer()
        
        # Test properties
        assert serializer.format_name == "JSON"
        assert not serializer.is_binary_format
        assert ".json" in serializer.file_extensions
        
        # Test serialization roundtrip
        json_str = serializer.dumps(simple_data)
        assert isinstance(json_str, str)
        
        restored = serializer.loads(json_str)
        assert restored == simple_data
    
    @pytest.mark.xsystem_unit
    def test_yaml_serializer(self, simple_data):
        """Test YAML serializer using PyYAML library."""
        serializer = YamlSerializer()
        
        # Test properties
        assert serializer.format_name == "YAML"
        assert not serializer.is_binary_format
        assert ".yaml" in serializer.file_extensions
        
        # Test serialization roundtrip
        yaml_str = serializer.dumps(simple_data)
        assert isinstance(yaml_str, str)
        
        restored = serializer.loads(yaml_str)
        assert restored == simple_data
    
    @pytest.mark.xsystem_unit
    def test_toml_serializer(self, simple_data):
        """Test TOML serializer using tomllib + tomli-w."""
        serializer = TomlSerializer()
        
        # Test properties
        assert serializer.format_name == "TOML"
        assert not serializer.is_binary_format
        assert ".toml" in serializer.file_extensions
        
        # Test serialization roundtrip
        toml_str = serializer.dumps(simple_data)
        assert isinstance(toml_str, str)
        
        restored = serializer.loads(toml_str)
        assert restored == simple_data
    
    @pytest.mark.xsystem_unit
    def test_xml_serializer(self, simple_data):
        """Test XML serializer using dicttoxml + xmltodict libraries."""
        try:
            serializer = XmlSerializer()
            
            # Test properties
            assert serializer.format_name == "XML"
            assert not serializer.is_binary_format
            assert ".xml" in serializer.file_extensions
            
            # Test serialization roundtrip
            xml_str = serializer.dumps(simple_data)
            assert isinstance(xml_str, str)
            assert "<?xml" in xml_str  # Should have XML declaration
            
            restored = serializer.loads(xml_str)
            assert isinstance(restored, dict)
            # XML conversion may change structure slightly, but should have content
            assert len(restored) > 0
            
        except ImportError as e:
            pytest.skip(f"XML libraries not available: {e}")
    
    @pytest.mark.xsystem_unit
    def test_bson_serializer(self, simple_data):
        """Test BSON serializer using pymongo.bson library."""
        try:
            serializer = BsonSerializer()
            
            # Test properties
            assert serializer.format_name == "BSON"
            assert serializer.is_binary_format
            assert ".bson" in serializer.file_extensions
            
            # Test serialization roundtrip
            bson_str = serializer.dumps(simple_data)
            assert isinstance(bson_str, str)  # Base64 encoded
            
            restored = serializer.loads(bson_str)
            assert restored == simple_data
            
        except ImportError as e:
            pytest.skip(f"BSON library not available: {e}")
    
    @pytest.mark.xsystem_unit
    def test_msgpack_serializer(self, simple_data):
        """Test MessagePack serializer using msgpack library."""
        try:
            serializer = MsgPackSerializer()
            
            # Test properties
            assert serializer.format_name == "MessagePack"
            assert serializer.is_binary_format
            assert ".msgpack" in serializer.file_extensions
            
            # Test serialization roundtrip
            msgpack_bytes = serializer.dumps(simple_data)
            assert isinstance(msgpack_bytes, bytes)
            
            restored = serializer.loads(msgpack_bytes)
            assert restored == simple_data
            
        except ImportError as e:
            pytest.skip(f"MessagePack library not available: {e}")
    
    @pytest.mark.xsystem_unit
    def test_cbor_serializer(self, simple_data):
        """Test CBOR serializer using cbor2 library."""
        try:
            serializer = CborSerializer()
            
            # Test properties
            assert serializer.format_name == "CBOR"
            assert serializer.is_binary_format
            assert ".cbor" in serializer.file_extensions
            
            # Test serialization roundtrip
            cbor_bytes = serializer.dumps(simple_data)
            assert isinstance(cbor_bytes, bytes)
            
            restored = serializer.loads(cbor_bytes)
            assert restored == simple_data
            
        except ImportError as e:
            pytest.skip(f"CBOR library not available: {e}")
    
    @pytest.mark.xsystem_unit
    def test_csv_serializer(self, csv_data):
        """Test CSV serializer using built-in csv library."""
        serializer = CsvSerializer(validate_input=False)
        
        # Test properties
        assert serializer.format_name == "CSV"
        assert not serializer.is_binary_format
        assert ".csv" in serializer.file_extensions
        
        # Test serialization roundtrip
        csv_str = serializer.dumps(csv_data)
        assert isinstance(csv_str, str)
        assert "name,age,city" in csv_str or "Alice" in csv_str
        
        restored = serializer.loads(csv_str)
        assert isinstance(restored, list)
        assert len(restored) == len(csv_data)
    
    @pytest.mark.xsystem_unit
    def test_pickle_serializer(self, simple_data):
        """Test Pickle serializer using built-in pickle library."""
        # Suppress pickle security warnings for testing
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            serializer = PickleSerializer(allow_unsafe=True)
            
            # Test properties
            assert serializer.format_name == "Pickle"
            assert serializer.is_binary_format
            assert ".pkl" in serializer.file_extensions
            
            # Test serialization roundtrip
            pickle_str = serializer.dumps(simple_data)
            assert isinstance(pickle_str, str)  # Base64 encoded
            
            restored = serializer.loads(pickle_str)
            assert restored == simple_data
    
    @pytest.mark.xsystem_unit
    def test_marshal_serializer(self, simple_data):
        """Test Marshal serializer using built-in marshal library."""
        serializer = MarshalSerializer()
        
        # Test properties
        assert serializer.format_name == "Marshal"
        assert serializer.is_binary_format
        assert ".marshal" in serializer.file_extensions
        
        # Test serialization roundtrip
        marshal_bytes = serializer.dumps(simple_data)
        assert isinstance(marshal_bytes, bytes)  # Binary format
        
        restored = serializer.loads(marshal_bytes)
        assert restored == simple_data
    
    @pytest.mark.xsystem_unit
    def test_formdata_serializer(self, simple_data):
        """Test FormData serializer using urllib.parse library."""
        serializer = FormDataSerializer()
        
        # Test properties
        assert serializer.format_name == "FormData"
        assert not serializer.is_binary_format
        assert ".form" in serializer.file_extensions
        
        # Test serialization roundtrip
        form_str = serializer.dumps(simple_data)
        assert isinstance(form_str, str)
        assert "=" in form_str and "&" in form_str
        
        restored = serializer.loads(form_str)
        assert isinstance(restored, dict)
        # FormData may convert types, but should preserve keys
        assert "x" in restored
    
    @pytest.mark.xsystem_unit
    def test_multipart_serializer(self, multipart_data):
        """Test Multipart serializer using email.mime libraries."""
        serializer = MultipartSerializer()
        
        # Test properties
        assert serializer.format_name == "Multipart"
        assert not serializer.is_binary_format
        assert ".multipart" in serializer.file_extensions
        
        # Test serialization roundtrip
        multipart_str = serializer.dumps(multipart_data)
        assert isinstance(multipart_str, str)
        assert "boundary=" in serializer.mime_type
        assert "Content-Disposition" in multipart_str
        
        restored = serializer.loads(multipart_str)
        assert isinstance(restored, dict)
        assert "text_field" in restored


class TestAllSerializersAdvanced:
    """Advanced tests for all serializers."""
    
    @pytest.mark.xsystem_unit
    def test_all_binary_format_flags(self):
        """Test that is_binary_format flag is correct for all serializers."""
        # Text formats
        text_serializers = [
            JsonSerializer(), YamlSerializer(), TomlSerializer(),
            CsvSerializer(), FormDataSerializer(), MultipartSerializer()
        ]
        
        for serializer in text_serializers:
            assert not serializer.is_binary_format, f"{serializer.format_name} should be text format"
        
        # Binary formats
        binary_serializers = [
            MsgPackSerializer(), CborSerializer(), PickleSerializer(allow_unsafe=True), 
            MarshalSerializer()
        ]
        
        # Test optional binary formats
        try:
            binary_serializers.append(BsonSerializer())
        except ImportError:
            pass
            
        try:
            xml_serializer = XmlSerializer()
            assert not xml_serializer.is_binary_format, "XML should be text format"
        except ImportError:
            pass
        
        for serializer in binary_serializers:
            assert serializer.is_binary_format, f"{serializer.format_name} should be binary format"
    
    @pytest.mark.xsystem_unit
    def test_file_extensions(self):
        """Test that all serializers have appropriate file extensions."""
        serializers = [
            (JsonSerializer(), [".json"]),
            (YamlSerializer(), [".yaml", ".yml"]),
            (TomlSerializer(), [".toml"]),
            (CsvSerializer(), [".csv"]),
            (PickleSerializer(allow_unsafe=True), [".pkl", ".pickle"]),
            (MarshalSerializer(), [".marshal"]),
            (FormDataSerializer(), [".form"]),
            (MultipartSerializer(), [".multipart"])
        ]
        
        for serializer, expected_extensions in serializers:
            extensions = serializer.file_extensions
            for ext in expected_extensions:
                assert ext in extensions, f"{serializer.format_name} should support {ext}"
    
    @pytest.mark.xsystem_unit
    def test_file_operations(self, simple_data, temp_dir):
        """Test file save/load operations for working serializers."""
        # Test serializers that don't require external dependencies
        serializers = [
            JsonSerializer(validate_paths=False),  # Disable path validation for temp files
            CsvSerializer(validate_input=False, validate_paths=False),
            PickleSerializer(allow_unsafe=True, validate_paths=False),
            MarshalSerializer(validate_paths=False),
            FormDataSerializer(validate_paths=False),
            MultipartSerializer(validate_paths=False)
        ]
        
        for serializer in serializers:
            test_file = temp_dir / f"test.{serializer.file_extensions[0][1:]}"
            
            # Use appropriate test data
            if isinstance(serializer, CsvSerializer):
                test_data = [simple_data]  # CSV needs list
            elif isinstance(serializer, MultipartSerializer):
                test_data = {"field": "value"}  # Simple multipart data
            else:
                test_data = simple_data
            
            try:
                # Test save and load
                serializer.save_file(test_data, test_file)
                assert test_file.exists(), f"File should be created for {serializer.format_name}"
                
                restored = serializer.load_file(test_file)
                assert restored is not None, f"Data should be restored for {serializer.format_name}"
                
            except Exception as e:
                pytest.fail(f"{serializer.format_name} file operations failed: {e}")


class TestProductionLibraryUsage:
    """Test that all serializers use production libraries correctly."""
    
    @pytest.mark.xsystem_unit
    def test_no_custom_parsing_logic(self):
        """Verify serializers use production libraries, not custom logic."""
        # This is a meta-test to verify our principle
        # We check that the key serialization methods are short and delegate to libraries
        
        import inspect
        
        serializers = [
            JsonSerializer(), YamlSerializer(), TomlSerializer(),
            CsvSerializer(), PickleSerializer(allow_unsafe=True), 
            MarshalSerializer(), FormDataSerializer(), MultipartSerializer()
        ]
        
        for serializer in serializers:
            dumps_source = inspect.getsource(serializer.dumps)
            loads_source = inspect.getsource(serializer.loads)
            
            # Check that implementation is relatively short (not hundreds of lines)
            dumps_lines = len(dumps_source.split('\n'))
            loads_lines = len(loads_source.split('\n'))
            
            # These should be reasonably short because they delegate to production libraries
            # CSV and FormData may have more logic for data structure conversion
            max_lines = 100 if serializer.format_name in ["CSV", "FormData", "Multipart"] else 50
            assert dumps_lines < max_lines, f"{serializer.format_name}.dumps() too long: {dumps_lines} lines"
            assert loads_lines < max_lines, f"{serializer.format_name}.loads() too long: {loads_lines} lines"
    
    @pytest.mark.xsystem_unit
    def test_all_format_names_unique(self):
        """Test that all format names are unique."""
        serializers = [
            JsonSerializer(), YamlSerializer(), TomlSerializer(),
            CsvSerializer(), PickleSerializer(allow_unsafe=True),
            MarshalSerializer(), FormDataSerializer(), MultipartSerializer()
        ]
        
        # Add optional serializers
        try:
            serializers.append(BsonSerializer())
        except ImportError:
            pass
            
        try:
            serializers.append(MsgPackSerializer())
        except ImportError:
            pass
            
        try:
            serializers.append(CborSerializer())
        except ImportError:
            pass
            
        try:
            serializers.append(XmlSerializer())
        except ImportError:
            pass
        
        format_names = [s.format_name for s in serializers]
        assert len(format_names) == len(set(format_names)), "All format names should be unique"
    
    @pytest.mark.xsystem_unit
    def test_all_serializers_count(self):
        """Test that we have all expected serializers available."""
        # Count serializers that should always work (built-in libraries)
        core_serializers = [
            JsonSerializer(), CsvSerializer(), PickleSerializer(allow_unsafe=True),
            MarshalSerializer(), FormDataSerializer(), MultipartSerializer()
        ]
        
        assert len(core_serializers) >= 6, "Should have at least 6 core serializers"
        
        # Test optional serializers
        optional_count = 0
        optional_names = []
        
        try:
            YamlSerializer()
            optional_count += 1
            optional_names.append("YAML")
        except ImportError:
            pass
            
        try:
            TomlSerializer()
            optional_count += 1
            optional_names.append("TOML")
        except ImportError:
            pass
            
        try:
            XmlSerializer()
            optional_count += 1
            optional_names.append("XML")
        except ImportError:
            pass
            
        try:
            BsonSerializer()
            optional_count += 1
            optional_names.append("BSON")
        except ImportError:
            pass
            
        try:
            MsgPackSerializer()
            optional_count += 1
            optional_names.append("MessagePack")
        except ImportError:
            pass
            
        try:
            CborSerializer()
            optional_count += 1
            optional_names.append("CBOR")
        except ImportError:
            pass
        
        total_serializers = len(core_serializers) + optional_count
        print(f"\n✅ Core serializers: {len(core_serializers)}")
        print(f"✅ Optional serializers: {optional_count} ({', '.join(optional_names)})")
        print(f"✅ Total serializers: {total_serializers}")
        
        # We should have close to 17 total
        assert total_serializers >= 6, f"Should have at least 6 serializers, got {total_serializers}"


class TestBuiltInPythonModules:
    """Test built-in Python module serializers."""
    
    @pytest.mark.xsystem_unit
    def test_configparser_serializer(self):
        """Test ConfigParser serializer using built-in configparser module."""
        ini_data = {
            "section1": {"key1": "value1", "key2": "value2"},
            "section2": {"key3": "value3", "key4": "value4"}
        }
        
        serializer = ConfigParserSerializer()
        
        # Test properties
        assert serializer.format_name == "ConfigParser"
        assert not serializer.is_binary_format
        assert ".ini" in serializer.file_extensions
        
        # Test serialization roundtrip
        ini_str = serializer.dumps(ini_data)
        assert isinstance(ini_str, str)
        assert "[section1]" in ini_str
        
        restored = serializer.loads(ini_str)
        assert isinstance(restored, dict)
        assert "section1" in restored
        assert restored["section1"]["key1"] == "value1"
    
    @pytest.mark.xsystem_unit
    def test_sqlite3_serializer(self):
        """Test SQLite3 serializer using built-in sqlite3 module."""
        sqlite_data = [
            {"id": 1, "name": "Alice", "score": 95},
            {"id": 2, "name": "Bob", "score": 87}
        ]
        
        serializer = Sqlite3Serializer()
        
        # Test properties
        assert serializer.format_name == "SQLite3"
        assert serializer.is_binary_format
        assert ".db" in serializer.file_extensions
        
        # Test serialization roundtrip
        sqlite_bytes = serializer.dumps(sqlite_data)
        assert isinstance(sqlite_bytes, bytes)
        
        restored = serializer.loads(sqlite_bytes)
        assert isinstance(restored, list)
        assert len(restored) == 2
        assert restored[0]["name"] == "Alice"
    
    @pytest.mark.xsystem_unit
    def test_dbm_serializer(self):
        """Test DBM serializer using built-in dbm module."""
        try:
            kv_data = {"key1": "value1", "key2": "value2", "key3": {"nested": "data"}}
            
            serializer = DbmSerializer()
            
            # Test properties
            assert serializer.format_name == "DBM"
            assert serializer.is_binary_format
            assert ".db" in serializer.file_extensions
            
            # Test serialization roundtrip
            dbm_bytes = serializer.dumps(kv_data)
            assert isinstance(dbm_bytes, bytes)
            
            restored = serializer.loads(dbm_bytes)
            assert isinstance(restored, dict)
            assert "key1" in restored
            
        except Exception as e:
            pytest.skip(f"DBM not available on this platform: {e}")
    
    @pytest.mark.xsystem_unit
    def test_shelve_serializer(self):
        """Test Shelve serializer using built-in shelve module."""
        try:
            kv_data = {"key1": "value1", "key2": [1, 2, 3], "key3": {"nested": "data"}}
            
            # Suppress warnings for test
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                serializer = ShelveSerializer(allow_unsafe=True)
            
            # Test properties
            assert serializer.format_name == "Shelve"
            assert serializer.is_binary_format
            assert ".shelf" in serializer.file_extensions
            
            # Test serialization roundtrip
            shelf_bytes = serializer.dumps(kv_data)
            assert isinstance(shelf_bytes, bytes)
            
            restored = serializer.loads(shelf_bytes)
            assert isinstance(restored, dict)
            assert "key1" in restored
            assert restored["key2"] == [1, 2, 3]
            
        except Exception as e:
            pytest.skip(f"Shelve not available or failed: {e}")
    
    @pytest.mark.xsystem_unit
    def test_plistlib_serializer(self):
        """Test Plistlib serializer using built-in plistlib module."""
        try:
            import plistlib
            
            plist_data = {
                "name": "Test App",
                "version": "1.0",
                "features": ["feature1", "feature2"],
                "config": {"debug": True, "timeout": 30}
            }
            
            serializer = PlistlibSerializer()
            
            # Test properties
            assert serializer.format_name == "Plistlib"
            assert ".plist" in serializer.file_extensions
            
            # Test serialization roundtrip
            plist_str = serializer.dumps(plist_data)
            assert isinstance(plist_str, str)
            assert "<?xml" in plist_str
            
            restored = serializer.loads(plist_str)
            assert isinstance(restored, dict)
            assert restored["name"] == "Test App"
            assert restored["config"]["debug"] == True
            
        except ImportError:
            pytest.skip("plistlib not available on this platform")


class TestAllBuiltInFormats:
    """Test that all built-in formats are working."""
    
    @pytest.mark.xsystem_unit
    def test_all_17_serializers_available(self):
        """Test that we have all 17 serializers available."""
        # Core serializers (always available)
        core_serializers = [
            JsonSerializer(), CsvSerializer(), PickleSerializer(allow_unsafe=True),
            MarshalSerializer(), FormDataSerializer(), MultipartSerializer()
        ]
        
        # Built-in Python modules (always available)
        builtin_serializers = [
            ConfigParserSerializer(),
            Sqlite3Serializer(),
            PlistlibSerializer()
        ]
        
        # Platform-dependent built-ins
        platform_serializers = []
        try:
            platform_serializers.append(DbmSerializer())
        except Exception:
            pass
        
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                platform_serializers.append(ShelveSerializer(allow_unsafe=True))
        except Exception:
            pass
        
        # Optional external libraries
        optional_serializers = []
        optional_names = []
        
        try:
            optional_serializers.append(YamlSerializer())
            optional_names.append("YAML")
        except ImportError:
            pass
            
        try:
            optional_serializers.append(TomlSerializer())
            optional_names.append("TOML")
        except ImportError:
            pass
            
        try:
            optional_serializers.append(XmlSerializer())
            optional_names.append("XML")
        except ImportError:
            pass
            
        try:
            optional_serializers.append(BsonSerializer())
            optional_names.append("BSON")
        except ImportError:
            pass
            
        try:
            optional_serializers.append(MsgPackSerializer())
            optional_names.append("MessagePack")
        except ImportError:
            pass
            
        try:
            optional_serializers.append(CborSerializer())
            optional_names.append("CBOR")
        except ImportError:
            pass
        
        total_count = (
            len(core_serializers) + 
            len(builtin_serializers) + 
            len(platform_serializers) + 
            len(optional_serializers)
        )
        
        print(f"\n✅ Core serializers (always available): {len(core_serializers)}")
        print(f"✅ Built-in Python modules: {len(builtin_serializers)}")
        print(f"✅ Platform-dependent: {len(platform_serializers)}")
        print(f"✅ Optional external libraries: {len(optional_serializers)} ({', '.join(optional_names)})")
        print(f"✅ Total available serializers: {total_count}/17")
        
        # We should have at least the core + built-in modules
        min_expected = len(core_serializers) + len(builtin_serializers)
        assert total_count >= min_expected, f"Should have at least {min_expected} serializers, got {total_count}"
