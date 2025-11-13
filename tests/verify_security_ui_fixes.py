#!/usr/bin/env python3
"""
Verification Script: Frontend Security UX Fixes (FIX 2)

This script verifies that security warnings and password masking
have been correctly implemented in the Streamlit UI.
"""

import re
import sys
from pathlib import Path

def verify_input_form():
    """Verify input_form.py contains all security enhancements."""

    input_form_path = Path('streamlit-app/components/input_form.py')

    if not input_form_path.exists():
        print(f"❌ File not found: {input_form_path}")
        return False

    content = input_form_path.read_text()

    checks = []

    # Check 1: Security warning box exists
    if 'st.warning' in content and 'Security Best Practices' in content:
        checks.append(('✅', 'Security warning box added'))
    else:
        checks.append(('❌', 'Security warning box missing'))

    # Check 2: Security warning mentions version control
    if 'Never commit credentials to version control' in content:
        checks.append(('✅', 'Version control warning present'))
    else:
        checks.append(('❌', 'Version control warning missing'))

    # Check 3: Security warning mentions Cloudflare Secrets
    if 'Cloudflare Secrets' in content or 'environment variables' in content:
        checks.append(('✅', 'Production best practices mentioned'))
    else:
        checks.append(('❌', 'Production best practices missing'))

    # Check 4: Security warning about browser cache
    if 'Clear browser cache' in content or 'browser cache' in content:
        checks.append(('✅', 'Browser cache warning present'))
    else:
        checks.append(('❌', 'Browser cache warning missing'))

    # Check 5: Twilio Account SID uses password type
    account_sid_pattern = r'st\.text_input\(\s*["\']Twilio Account SID["\'].*?type=["\']password["\']'
    if re.search(account_sid_pattern, content, re.DOTALL):
        checks.append(('✅', 'Twilio Account SID masked (type="password")'))
    else:
        checks.append(('❌', 'Twilio Account SID NOT masked'))

    # Check 6: Twilio Auth Token uses password type
    auth_token_pattern = r'st\.text_input\(\s*["\']Twilio Auth Token["\'].*?type=["\']password["\']'
    if re.search(auth_token_pattern, content, re.DOTALL):
        checks.append(('✅', 'Twilio Auth Token masked (type="password")'))
    else:
        checks.append(('❌', 'Twilio Auth Token NOT masked'))

    # Check 7: Account SID has helpful placeholder
    if 'placeholder="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"' in content:
        checks.append(('✅', 'Account SID placeholder present'))
    else:
        checks.append(('❌', 'Account SID placeholder missing'))

    # Check 8: Auth Token has helpful placeholder
    if 'placeholder="••••••••••••••••••••••••••••••••"' in content:
        checks.append(('✅', 'Auth Token placeholder present'))
    else:
        checks.append(('❌', 'Auth Token placeholder missing'))

    # Check 9: Account SID help text mentions masking
    if 'This will be masked for security' in content:
        checks.append(('✅', 'Help text mentions security masking'))
    else:
        checks.append(('❌', 'Help text missing security mention'))

    # Print results
    print("\n" + "="*80)
    print("FIX 2: Security Warnings & Password Masking Verification")
    print("="*80)
    print(f"\nFile: {input_form_path}")
    print()

    all_passed = True
    for status, message in checks:
        print(f"{status} {message}")
        if status == '❌':
            all_passed = False

    print()
    print("="*80)
    if all_passed:
        print("✅ All security UI checks passed!")
    else:
        print("❌ Some security UI checks failed!")
    print("="*80)

    return all_passed


def verify_phone_regex():
    """Verify phone validation regex in email-worker template."""

    template_path = Path('streamlit-app/templates/email-worker/index.ts.j2')

    if not template_path.exists():
        print(f"❌ File not found: {template_path}")
        return False

    content = template_path.read_text()

    checks = []

    # Check 1: Correct regex pattern exists
    # Looking for: /^\+[1-9]\d{10,14}$/
    if r'^\+[1-9]\d{10,14}$' in content:
        checks.append(('✅', 'Correct regex pattern: /^\\+[1-9]\\d{10,14}$/'))
    else:
        checks.append(('❌', 'Incorrect or missing regex pattern'))

    # Check 2: Old buggy regex is NOT present
    # Looking for: /^\+[1-9]\d{1,14}$/
    if r'^\+[1-9]\d{1,14}$' not in content:
        checks.append(('✅', 'Old buggy regex removed'))
    else:
        checks.append(('❌', 'Old buggy regex still present!'))

    # Check 3: Comment explaining E.164 format exists
    if 'E.164' in content and ('minimum 11 digits' in content or 'Example:' in content):
        checks.append(('✅', 'E.164 format documentation present'))
    else:
        checks.append(('❌', 'E.164 format documentation missing'))

    # Check 4: Comment shows valid examples
    if '+14155552671' in content or '+442071234567' in content:
        checks.append(('✅', 'Valid phone number examples in comments'))
    else:
        checks.append(('❌', 'Missing example phone numbers'))

    # Print results
    print("\n" + "="*80)
    print("FIX 5: Phone Number Validation Regex Verification")
    print("="*80)
    print(f"\nFile: {template_path}")
    print()

    all_passed = True
    for status, message in checks:
        print(f"{status} {message}")
        if status == '❌':
            all_passed = False

    print()
    print("="*80)
    if all_passed:
        print("✅ All phone regex checks passed!")
    else:
        print("❌ Some phone regex checks failed!")
    print("="*80)

    return all_passed


def main():
    """Run all verification checks."""
    print("\n" + "🔒" * 40)
    print("WAVE 1 SECURITY & UX FIXES VERIFICATION")
    print("🔒" * 40)

    ui_passed = verify_input_form()
    print()
    regex_passed = verify_phone_regex()

    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)

    if ui_passed and regex_passed:
        print("✅ ALL VERIFICATION CHECKS PASSED!")
        print("\nFixes Verified:")
        print("  • FIX 2: Security warnings added to Streamlit UI")
        print("  • FIX 2: Password masking for Twilio credentials")
        print("  • FIX 5: Phone validation regex corrected (E.164 compliance)")
        print("\nReady to report to Hive Mind collective.")
        return 0
    else:
        print("❌ SOME VERIFICATION CHECKS FAILED!")
        print("\nPlease review the failures above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
