# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible
for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take the security of `gspace` seriously. If you believe you have found a
security vulnerability, please report it to us as described below.

### Please do NOT:

- Open a public GitHub issue for the security vulnerability
- Discuss the security issue publicly until it has been resolved

### Please DO:

1. **Email us directly** at `dev@sentivs.com` with the subject line:
   ```
   [SECURITY] Brief description of the issue
   ```

2. **Include the following information** in your report:
   - Type of issue (e.g., authentication bypass, information disclosure, etc.)
   - Full paths of source file(s) related to the manifestation of the issue
   - The location of the affected source code (tag/branch/commit or direct URL)
   - Step-by-step instructions to reproduce the issue
   - Proof-of-concept or exploit code (if possible)
   - Impact of the issue, including how an attacker might exploit the issue

3. **Expect a response within 48 hours**. We'll acknowledge receipt of your report and provide an initial assessment.

4. **Allow time for us to fix the issue** before disclosing it publicly. We'll keep you informed of our progress.

### Our Commitment

- We will respond to your report within **48 hours**
- We will provide a more detailed assessment within **7 days**
- We will keep you informed of our progress toward resolving the issue
- We will credit you for the discovery (unless you prefer to remain anonymous)

### Security Best Practices

When using `gspace`, please follow these security best practices:

1. **Protect Your Credentials**
   - Never commit credentials files (`credentials.json`, `token.json`) to version control
   - Use environment variables or secure credential storage
   - Add credential files to `.gitignore`

2. **Use Encrypted Token Storage**
   ```python
   from gspace import GSpace
   from gspace.auth.token_manager import EncryptedTokenBackend

   # Use encrypted token storage
   token_backend = EncryptedTokenBackend(
       storage_path="tokens.encrypted",
       encryption_key="your-secret-key"  # Store securely!
   )
   ```

3. **Limit API Scopes**
   - Only request the minimum scopes needed for your application
   - Regularly review and audit granted permissions

4. **Keep Dependencies Updated**
   ```bash
   pip install --upgrade gspace
   ```

5. **Use Environment Variables for Sensitive Data**
   ```python
   import os

   credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
   ```

6. **Monitor Token Expiration**
   - Implement proper token refresh mechanisms
   - Handle authentication errors gracefully

7. **Secure Your Application**
   - Use HTTPS in production
   - Implement proper access controls
   - Log security-relevant events

### Known Security Considerations

- **Token Storage**: Tokens are stored locally by default. Consider using `EncryptedTokenBackend` for additional security.
- **Credential Files**: Always keep your Google OAuth2 credentials and service account keys secure and never commit them to version control.
- **OAuth2 Flow**: The OAuth2 flow uses a local server on port 8080. Ensure this port is not exposed to untrusted networks.

### Security Updates

Security updates will be released as:
- Patch versions (e.g., `0.1.0` → `0.1.1`) for critical security fixes
- Minor versions (e.g., `0.1.0` → `0.2.0`) for security improvements

We recommend keeping `gspace` updated to the latest version.

### Security Hall of Fame

We would like to thank the following people for responsibly disclosing security issues:

- (To be added)

Thank you for helping keep `gspace` and our users safe!
