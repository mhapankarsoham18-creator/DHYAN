import 'dart:async';
import 'package:sentry_flutter/sentry_flutter.dart';

/// Scrubs sensitive PII and tokens from Sentry events before they leave the device.
FutureOr<SentryEvent?> maskSensitiveData(SentryEvent event, Hint hint) {
  // Regex patterns to match PAN and Tokens
  final panRegex = RegExp(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b', caseSensitive: false);
  final tokenRegex = RegExp(r'(?:bearer\s+|token[\s=:]+|authorization[\s=:]+)([a-zA-Z0-9_\-\.]+)', caseSensitive: false);
  final pwdRegex = RegExp(r'(?:password|passwd|pwd)[\s=:]+([^\s,;]+)', caseSensitive: false);

  String scrubString(String text) {
    var scrubbed = text;
    scrubbed = scrubbed.replaceAllMapped(panRegex, (_) => '[REDACTED_PAN]');
    scrubbed = scrubbed.replaceAllMapped(tokenRegex, (match) {
      return match.group(0)!.replaceFirst(match.group(1)!, '[REDACTED_TOKEN]');
    });
    scrubbed = scrubbed.replaceAllMapped(pwdRegex, (match) {
      return match.group(0)!.replaceFirst(match.group(1)!, '[REDACTED_PASSWORD]');
    });
    return scrubbed;
  }

  // Scrub exception values
  final exceptions = event.exceptions?.map((e) {
    if (e.value != null) {
      e.value = scrubString(e.value!);
    }
    return e;
  }).toList();
  event.exceptions = exceptions;

  // Scrub message
  if (event.message != null) {
    event.message = SentryMessage(scrubString(event.message!.formatted));
  }

  // Scrub request headers and body if attached
  final request = event.request;
  if (request != null) {
    final headers = Map<String, String>.from(request.headers);
    if (headers.containsKey('Authorization') || headers.containsKey('authorization')) {
      headers['Authorization'] = '[REDACTED]';
      headers['authorization'] = '[REDACTED]';
    }

    dynamic data = request.data;
    if (data is String) {
      data = scrubString(data);
    } else if (data is Map) {
      final scrubbedData = Map<String, dynamic>.from(data);
      for (final key in ['password', 'token', 'access_token', 'refresh_token', 'pan']) {
        if (scrubbedData.containsKey(key)) {
          scrubbedData[key] = '[REDACTED]';
        }
      }
      data = scrubbedData;
    }

    event.request = SentryRequest(
      url: request.url,
      method: request.method,
      queryString: request.queryString,
      cookies: request.cookies,
      headers: headers,
      env: request.env,
      fragment: request.fragment,
      data: data,
    );
  }

  return event;
}
