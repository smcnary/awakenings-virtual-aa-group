# Trusted Servants User Management with Maximum Privacy and Anonymity

This document describes the new trusted servants user management functionality that has been added to the AA Virtual platform, designed with maximum privacy and anonymity in mind.

## Overview

The system now provides trusted servants (Admins and Secretaries) with comprehensive user management capabilities while maintaining the highest standards of privacy and anonymity required for AA virtual groups.

## Key Features

### 🔒 Maximum Privacy Controls
- **Anonymous User Creation**: Create users with no personal identifying information
- **Data Minimization**: Only collect and store necessary data
- **Privacy Settings**: Granular control over what information is shared
- **Data Anonymization**: Complete anonymization of user data when needed

### 👥 User Management
- **Create Users**: Admins and Secretaries can create new users
- **Update Users**: Modify user profiles with privacy controls
- **Delete Users**: Soft delete (deactivate) or hard delete (with anonymization)
- **Privacy Audits**: Comprehensive privacy compliance checking

### 🛡️ Anonymity Features
- **Anonymous Service Positions**: Create service positions without revealing identity
- **Data Hashing**: Sensitive data is hashed for privacy
- **Audit Trail Protection**: Maintain system integrity while protecting privacy
- **Compliance Monitoring**: Track and ensure privacy compliance

## API Endpoints

### Admin Endpoints (`/api/admin/`)

#### Create User
```http
POST /api/admin/users
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "preferred_name": "Optional Name",
  "email": "optional@example.com",
  "phone": "+1234567890",
  "timezone": "America/Chicago",
  "language": "en",
  "show_sobriety_date": false,
  "show_in_directory": false,
  "allow_contact": false,
  "notification_preferences": {
    "email_notifications": false,
    "meeting_reminders": true,
    "service_updates": false,
    "marketing": false
  }
}
```

#### Update User
```http
PUT /api/admin/users/{user_id}
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "preferred_name": "Updated Name",
  "show_sobriety_date": false,
  "allow_contact": false
}
```

#### Delete User
```http
DELETE /api/admin/users/{user_id}?permanent=false
Authorization: Bearer {admin_token}
```

### Trusted Servants Endpoints (`/api/trusted-servants/`)

#### Create User for Service
```http
POST /api/trusted-servants/users
Authorization: Bearer {secretary_token}
Content-Type: application/json

{
  "preferred_name": "Service Member",
  "timezone": "America/Chicago",
  "show_in_directory": false,
  "allow_contact": false
}
```

#### Create Anonymous Service User
```http
POST /api/trusted-servants/anonymous-user?service_position=secretary
Authorization: Bearer {secretary_token}
```

#### Update User for Service
```http
PUT /api/trusted-servants/users/{user_id}
Authorization: Bearer {secretary_token}
Content-Type: application/json

{
  "preferred_name": "Updated Service Member",
  "show_in_directory": false
}
```

#### Delete User for Service
```http
DELETE /api/trusted-servants/users/{user_id}?permanent=false
Authorization: Bearer {admin_token}
```

#### Get Privacy Compliant Users
```http
GET /api/trusted-servants/privacy-compliant-users
Authorization: Bearer {secretary_token}
```

#### Privacy Audit
```http
GET /api/trusted-servants/users/{user_id}/privacy-audit
Authorization: Bearer {secretary_token}
```

#### Anonymize User Data
```http
POST /api/trusted-servants/users/{user_id}/anonymize?preserve_audit=true
Authorization: Bearer {admin_token}
```

## Privacy and Anonymity Features

### 1. Anonymous User Creation
- Creates users with no personal identifying information
- Generates anonymous identifiers
- Sets maximum privacy defaults
- Maintains system functionality without compromising anonymity

### 2. Data Anonymization
- **Complete Anonymization**: Removes all PII while preserving system integrity
- **Selective Anonymization**: Can preserve audit trails for compliance
- **Data Hashing**: Sensitive data is hashed using SHA-256
- **Anonymous Identifiers**: Generates secure anonymous IDs

### 3. Privacy Controls
- **Directory Visibility**: Users can opt out of member directory
- **Contact Permissions**: Users can disable contact features
- **Sobriety Date Sharing**: Users can hide sobriety information
- **Notification Preferences**: Granular control over communications

### 4. Privacy Auditing
- **Compliance Scoring**: Rates privacy compliance from Low to Maximum
- **Data Retention Analysis**: Shows what data is stored
- **Recommendations**: Provides suggestions for improving privacy
- **Regular Monitoring**: Tracks privacy compliance over time

## User Roles and Permissions

### Admin
- Can create, update, and delete any user
- Can perform hard deletes with data anonymization
- Can anonymize user data
- Can access all privacy audit information
- Can create anonymous service users

### Secretary
- Can create and update users for service purposes
- Can perform soft deletes (deactivation)
- Can access privacy compliant user lists
- Can view privacy audit information
- Can create anonymous service users

### Member
- Can update their own profile
- Can control their own privacy settings
- Can delete their own account (soft delete)

## Privacy Compliance Features

### Data Minimization
- Only collects necessary information
- Provides options for minimal data collection
- Supports completely anonymous participation

### Data Protection
- All sensitive data is hashed
- IP addresses and user agents are anonymized
- Personal information can be completely removed

### Audit Trail
- All actions are logged for accountability
- Privacy-preserving audit logs
- Compliance monitoring and reporting

### User Control
- Users control their own data visibility
- Granular privacy settings
- Easy account deletion and data removal

## Security Considerations

### Authentication
- Magic link authentication (no passwords)
- JWT tokens with expiration
- Role-based access control
- Session management

### Data Security
- All data transmission is encrypted (HTTPS)
- Sensitive data is hashed in the database
- Regular security audits
- Privacy compliance monitoring

### Access Control
- Role-based permissions
- API endpoint protection
- Admin-only sensitive operations
- Audit logging for all actions

## Usage Examples

### Creating an Anonymous Service Position
```python
# Create anonymous user for secretary position
response = requests.post(
    "/api/trusted-servants/anonymous-user",
    params={"service_position": "secretary"},
    headers={"Authorization": "Bearer {secretary_token}"}
)

# Response includes anonymous user ID and privacy level
{
  "message": "Anonymous service user created successfully",
  "user_id": "uuid-here",
  "anonymous_name": "Anonymous_abc12345",
  "service_position": "secretary",
  "privacy_level": "Maximum",
  "data_retention": "Minimal"
}
```

### Privacy Audit
```python
# Get privacy compliance audit
response = requests.get(
    f"/api/trusted-servants/users/{user_id}/privacy-audit",
    headers={"Authorization": "Bearer {secretary_token}"}
)

# Response includes privacy score and recommendations
{
  "user_id": "uuid-here",
  "privacy_score": 7,
  "max_score": 8,
  "privacy_percentage": 87.5,
  "privacy_level": "Maximum",
  "data_retention": {
    "audit_logs": 5,
    "login_sessions": 2,
    "meeting_attendance": 10,
    "service_assignments": 1
  },
  "recommendations": [
    "Consider using anonymous role for maximum privacy"
  ]
}
```

### Data Anonymization
```python
# Anonymize user data while preserving audit trail
response = requests.post(
    f"/api/trusted-servants/users/{user_id}/anonymize",
    params={"preserve_audit": True},
    headers={"Authorization": "Bearer {admin_token}"}
)

# Response confirms anonymization
{
  "message": "User data anonymized successfully",
  "user_id": "uuid-here",
  "preserve_audit": True,
  "privacy_compliant": True
}
```

## Testing

A comprehensive test suite is included (`test_trusted_servants_user_management.py`) that tests:

- User creation (basic and anonymous)
- Privacy settings updates
- Privacy compliance auditing
- Data anonymization
- User deletion (soft and hard)
- Privacy compliant user retrieval

Run the tests with:
```bash
python test_trusted_servants_user_management.py
```

## Compliance and Privacy

This implementation follows AA's tradition of anonymity and privacy:

- **Tradition of Anonymity**: Supports completely anonymous participation
- **Data Minimization**: Only collects necessary information
- **User Control**: Users control their own data and privacy
- **Secure Deletion**: Complete data removal when requested
- **Audit Trail**: Maintains accountability while protecting privacy

## Future Enhancements

Potential future improvements include:

- **Advanced Anonymization**: More sophisticated anonymization techniques
- **Privacy Dashboard**: User-facing privacy management interface
- **Compliance Reporting**: Automated privacy compliance reports
- **Data Export**: Privacy-compliant data export features
- **Consent Management**: Granular consent tracking and management

## Support

For questions or issues with the trusted servants user management functionality, please refer to:

- API documentation in the codebase
- Test suite for usage examples
- Privacy service documentation
- Admin service documentation

---

*This functionality ensures that AA Virtual maintains the highest standards of privacy and anonymity while providing necessary administrative capabilities for trusted servants.*
