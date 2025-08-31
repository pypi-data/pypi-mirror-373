import pytest
from datetime import datetime, timedelta
from geek_cafe_saas_models.core.security.entity_access import EntityAccess


class TestEntityAccess:
    def test_entity_access_creation(self):
        """Test basic entity access creation with new fields"""
        access = EntityAccess()
        
        # Test basic access setup
        access.access_levels = ["read", "write"]
        access.xref_type = "property"
        access.xref_pk = "prop_123"
        access.user_id = "user456"
        access.role = "realtor"
        access.shared_by_user_id = "owner789"
        access.notes = "Access granted for property evaluation"
        
        assert access.access_levels == ["read", "write"]
        assert access.xref_type == "property"
        assert access.xref_pk == "prop_123"
        assert access.role == "realtor"
        assert access.shared_by_user_id == "owner789"
        assert access.notes == "Access granted for property evaluation"

    def test_access_levels_string_parsing(self):
        """Test access levels string parsing"""
        access = EntityAccess()
        
        # Test string input
        access.access_levels = "read,write,delete"
        assert access.access_levels == ["read", "write", "delete"]
        
        # Test list input
        access.access_levels = ["read", "comment"]
        assert access.access_levels == ["read", "comment"]

    def test_access_levels_validation(self):
        """Test access levels validation"""
        access = EntityAccess()
        
        # Test None value raises error
        with pytest.raises(ValueError, match="Action cannot be None"):
            access.access_levels = None

    def test_expiring_access(self):
        """Test access with expiration"""
        access = EntityAccess()
        
        future_date = datetime.now() + timedelta(days=30)
        access.expires_at = future_date
        access.access_levels = ["read"]
        access.xref_type = "property"
        access.xref_pk = "prop_123"
        
        assert access.expires_at == future_date

    def test_role_based_access(self):
        """Test different role types"""
        family_access = EntityAccess()
        family_access.role = "family"
        family_access.access_levels = ["read", "write", "comment"]
        
        realtor_access = EntityAccess()
        realtor_access.role = "realtor"
        realtor_access.access_levels = ["read", "comment"]
        
        contractor_access = EntityAccess()
        contractor_access.role = "contractor"
        contractor_access.access_levels = ["read", "comment"]
        
        inspector_access = EntityAccess()
        inspector_access.role = "inspector"
        inspector_access.access_levels = ["read", "write"]
        
        assert family_access.role == "family"
        assert realtor_access.role == "realtor"
        assert contractor_access.role == "contractor"
        assert inspector_access.role == "inspector"

    def test_wildcard_access(self):
        """Test wildcard access patterns"""
        access = EntityAccess()
        
        # Test wildcard xref_type (default behavior)
        assert access.xref_type == "*"
        
        # Test wildcard xref_pk (default behavior)
        assert access.xref_pk == "*"
        
        # Test specific access
        access.xref_type = "property"
        access.xref_pk = "prop_123"
        
        assert access.xref_type == "property"
        assert access.xref_pk == "prop_123"

    def test_property_sharing_scenario(self):
        """Test a complete property sharing scenario"""
        # Owner shares property with family member
        family_access = EntityAccess()
        family_access.user_id = "family_member_123"
        family_access.shared_by_user_id = "property_owner_456"
        family_access.xref_type = "property"
        family_access.xref_pk = "prop_789"
        family_access.access_levels = ["read", "write", "comment"]
        family_access.role = "family"
        family_access.notes = "Spouse access for house hunting"
        
        # Owner shares property with realtor
        realtor_access = EntityAccess()
        realtor_access.user_id = "realtor_abc"
        realtor_access.shared_by_user_id = "property_owner_456"
        realtor_access.xref_type = "property"
        realtor_access.xref_pk = "prop_789"
        realtor_access.access_levels = ["read", "comment"]
        realtor_access.role = "realtor"
        realtor_access.expires_at = datetime.now() + timedelta(days=90)
        realtor_access.notes = "Realtor access for market analysis"
        
        # Verify family access
        assert family_access.role == "family"
        assert "write" in family_access.access_levels
        assert family_access.expires_at is None  # No expiration for family
        
        # Verify realtor access
        assert realtor_access.role == "realtor"
        assert "write" not in realtor_access.access_levels
        assert realtor_access.expires_at is not None  # Has expiration
