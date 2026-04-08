import 'dart:convert';
import 'dart:io';
import 'package:crypto/crypto.dart';
import 'package:device_info_plus/device_info_plus.dart';

class DeviceFingerprintService {
  String? _cachedFingerprint;

  /// Fetch and securely hash a unique device identifier.
  /// Uses SHA-256 so the raw identifier never leaves the device,
  /// preserving user privacy while allowing rate-limiting capabilities.
  Future<String> getFingerprint() async {
    if (_cachedFingerprint != null) return _cachedFingerprint!;

    final deviceInfo = DeviceInfoPlugin();
    String identifier = 'unknown-device';

    try {
      if (Platform.isAndroid) {
        final androidInfo = await deviceInfo.androidInfo;
        identifier = androidInfo.id; // Unique ID for Android devices
      } else if (Platform.isIOS) {
        final iosInfo = await deviceInfo.iosInfo;
        identifier = iosInfo.identifierForVendor ?? 'unknown-ios-device';
      }
    } catch (e) {
      // Fallback in case of failure, usually means physical ID couldn't be read
      identifier = 'fallback-device-id-${DateTime.now().millisecondsSinceEpoch}';
    }

    // Add a salt strictly for DHYAN so the hash isn't globally reversible
    final saltedKey = 'DHYAN-SALT-9092-$identifier';
    final bytes = utf8.encode(saltedKey);
    final digest = sha256.convert(bytes);
    
    _cachedFingerprint = digest.toString();
    return _cachedFingerprint!;
  }
}

// Global instance for easy access inside non-Riverpod classes like DioClient
final deviceFingerprintService = DeviceFingerprintService();
