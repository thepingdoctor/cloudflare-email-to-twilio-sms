/**
 * Content Processor
 * Extracts and sanitizes email content for SMS delivery
 */

import type { ParsedEmail } from '../types';

/**
 * SMS length limits
 */
const SMS_LIMITS = {
  STANDARD: 160, // GSM-7 encoding
  UNICODE: 70,   // UCS-2 encoding (Unicode)
  EXTENDED: 1600, // Multi-part SMS (10 segments)
};

/**
 * Process email content for SMS delivery
 */
export function processEmailContent(email: ParsedEmail, maxLength = SMS_LIMITS.STANDARD): string {
  // Get text content (prefer plain text over HTML)
  let content = email.text || convertHtmlToText(email.html || '');

  // Remove email signatures
  content = removeEmailSignature(content);

  // Strip excessive whitespace
  content = normalizeWhitespace(content);

  // Add sender info if space permits
  const senderInfo = `From: ${extractSenderName(email.from)}\n`;
  const subjectInfo = email.subject ? `Re: ${email.subject}\n` : '';
  const prefix = senderInfo + subjectInfo;

  // Calculate available space for message
  const availableLength = maxLength - prefix.length - 3; // Reserve 3 chars for ellipsis

  if (content.length > availableLength) {
    content = smartTruncate(content, availableLength);
  }

  // Combine prefix and content
  let finalContent = prefix + content;

  // Final length check
  if (finalContent.length > maxLength) {
    finalContent = finalContent.substring(0, maxLength - 3) + '...';
  }

  return finalContent.trim();
}

/**
 * Convert HTML to plain text
 */
export function convertHtmlToText(html: string): string {
  if (!html) return '';

  // Remove script and style tags
  let text = html.replace(/<script[^>]*>.*?<\/script>/gi, '');
  text = text.replace(/<style[^>]*>.*?<\/style>/gi, '');

  // Convert <br> to newlines
  text = text.replace(/<br\s*\/?>/gi, '\n');

  // Convert </p> and </div> to double newlines
  text = text.replace(/<\/(p|div)>/gi, '\n\n');

  // Remove all remaining HTML tags
  text = text.replace(/<[^>]+>/g, '');

  // Decode HTML entities safely (prevent nested/double decoding)
  text = decodeHtmlEntitiesSafely(text);

  // CRITICAL SECURITY: Strip ALL HTML tags after entity decoding
  // This prevents nested encoding attacks like &lt;script&gt; becoming <script>
  text = text.replace(/<[^>]*>/g, '');

  // Remove javascript: protocol (case-insensitive)
  text = text.replace(/javascript:/gi, '');

  // Remove event handlers (case-insensitive)
  text = removeEventHandlers(text);

  // Trim only newlines from start/end, preserve meaningful spaces from entities
  text = text.replace(/^\n+|\n+$/g, '');

  // If result is only whitespace (after newline trim), return empty string
  if (/^\s*$/.test(text)) {
    return '';
  }

  return text;
}

/**
 * Remove email signature
 */
export function removeEmailSignature(text: string): string {
  // Common signature delimiters
  const signaturePatterns = [
    /--\s*$/m,           // Standard "--" delimiter
    /_{2,}/,             // Multiple underscores
    /^Best regards,/mi,  // Common sign-offs
    /^Sincerely,/mi,
    /^Thanks,/mi,
    /^Sent from my/mi,   // Mobile signatures
  ];

  for (const pattern of signaturePatterns) {
    const match = text.search(pattern);
    if (match !== -1) {
      return text.substring(0, match).trim();
    }
  }

  return text;
}

/**
 * Normalize whitespace
 */
export function normalizeWhitespace(text: string): string {
  // Replace multiple spaces with single space
  text = text.replace(/ {2,}/g, ' ');

  // Replace multiple newlines with max 2 newlines
  text = text.replace(/\n{3,}/g, '\n\n');

  // Trim leading/trailing whitespace from each line
  text = text.split('\n').map(line => line.trim()).join('\n');

  return text.trim();
}

/**
 * Smart truncate - try to break at sentence/word boundaries
 */
export function smartTruncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text;
  }

  // Try to break at sentence boundary
  const sentences = text.match(/[^.!?]+[.!?]+/g) || [text];
  let result = '';

  for (const sentence of sentences) {
    if ((result + sentence).length > maxLength - 3) {
      break;
    }
    result += sentence;
  }

  if (result.length > 0) {
    return result.trim() + '...';
  }

  // If no sentence break found, break at word boundary
  const words = text.split(' ');
  result = '';

  for (const word of words) {
    if ((result + word).length > maxLength - 3) {
      break;
    }
    result += word + ' ';
  }

  if (result.length > 0) {
    return result.trim() + '...';
  }

  // Last resort: hard truncate
  return text.substring(0, maxLength - 3) + '...';
}

/**
 * Extract sender name from email address
 */
export function extractSenderName(email: string): string {
  // Try to extract display name from "Name <email@domain.com>" format
  const nameMatch = email.match(/^(.+?)\s*<.+>$/);
  if (nameMatch) {
    return nameMatch[1].replace(/['"]/g, '').trim();
  }

  // If no display name, use email prefix
  const emailMatch = email.match(/^([^@]+)@/);
  if (emailMatch) {
    return emailMatch[1].replace(/[._-]/g, ' ').trim();
  }

  return email;
}

/**
 * Decode HTML entities safely (prevents nested/double decoding attacks)
 */
function decodeHtmlEntitiesSafely(text: string): string {
  let decoded = text;

  // Decode entities in safe order: specific entities first, &amp; LAST
  // This prevents double-decoding of entities like &amp;nbsp;
  decoded = decoded.replace(/&nbsp;/g, ' ');
  decoded = decoded.replace(/&quot;/g, '"');
  decoded = decoded.replace(/&lt;/g, '<');
  decoded = decoded.replace(/&gt;/g, '>');
  decoded = decoded.replace(/&apos;/g, "'");
  decoded = decoded.replace(/&lsquo;/g, "'");
  decoded = decoded.replace(/&rsquo;/g, "'");
  decoded = decoded.replace(/&ldquo;/g, '"');
  decoded = decoded.replace(/&rdquo;/g, '"');
  decoded = decoded.replace(/&mdash;/g, '—');
  decoded = decoded.replace(/&ndash;/g, '–');
  decoded = decoded.replace(/&hellip;/g, '...');

  // Decode &amp; LAST to prevent double-decoding
  decoded = decoded.replace(/&amp;/g, '&');

  // Decode numeric entities
  decoded = decoded.replace(/&#(\d+);/g, (_, code) => String.fromCharCode(parseInt(code, 10)));
  decoded = decoded.replace(/&#x([0-9a-f]+);/gi, (_, code) => String.fromCharCode(parseInt(code, 16)));

  return decoded;
}

/**
 * Remove event handlers from text (case-insensitive)
 */
function removeEventHandlers(text: string): string {
  // List of common event handlers
  const eventHandlers = [
    'onclick', 'ondblclick', 'onmousedown', 'onmouseup', 'onmouseover', 'onmousemove', 'onmouseout',
    'onload', 'onunload', 'onchange', 'onsubmit', 'onreset', 'onselect', 'onblur', 'onfocus',
    'onkeydown', 'onkeypress', 'onkeyup', 'onerror', 'onabort', 'onbeforeunload', 'onhashchange',
    'onmessage', 'ononline', 'onoffline', 'onpopstate', 'onresize', 'onstorage', 'oncontextmenu',
    'oninput', 'oninvalid', 'onsearch', 'ondrag', 'ondragend', 'ondragenter', 'ondragleave',
    'ondragover', 'ondragstart', 'ondrop', 'onscroll', 'oncopy', 'oncut', 'onpaste'
  ];

  let sanitized = text;

  // Remove each event handler (case-insensitive)
  for (const handler of eventHandlers) {
    const regex = new RegExp(handler, 'gi');
    sanitized = sanitized.replace(regex, '');
  }

  return sanitized;
}

/**
 * Sanitize content - remove potentially dangerous content
 */
export function sanitizeContent(text: string): string {
  // Remove URLs (optional - may want to keep them)
  // text = text.replace(/https?:\/\/[^\s]+/g, '[link]');

  // Remove email addresses (to prevent spam loops)
  text = text.replace(/[\w.-]+@[\w.-]+\.\w+/g, '[email]');

  // Remove special characters that might cause SMS issues
  text = text.replace(/[\x00-\x1F\x7F]/g, ''); // Control characters

  // Trim and return empty string if only whitespace
  text = text.trim();

  // Check if result is only whitespace characters (spaces, tabs, etc.)
  if (/^\s*$/.test(text)) {
    return '';
  }

  return text;
}

/**
 * Check if content contains Unicode characters (affects SMS pricing)
 */
export function containsUnicode(text: string): boolean {
  // Check if any character is outside GSM-7 charset
  const gsmCharset = /^[\x00-\x7F]*$/;
  return !gsmCharset.test(text);
}

/**
 * Calculate SMS segment count
 */
export function calculateSMSSegments(text: string): number {
  const isUnicode = containsUnicode(text);

  // For SMS, we count actual Unicode characters (code points), not string length
  // Emojis and some special chars are surrogate pairs in JS but count as 1 char in SMS
  const charCount = isUnicode ? Array.from(text).length : text.length;

  const limit = isUnicode ? SMS_LIMITS.UNICODE : SMS_LIMITS.STANDARD;

  if (charCount <= limit) {
    return 1;
  }

  // Multi-part SMS has slightly different limits
  const multiPartLimit = isUnicode ? 67 : 153;
  return Math.ceil(charCount / multiPartLimit);
}
