import 'dart:io';
import 'package:dio/dio.dart';
import 'package:dio/io.dart';
import 'package:crypto/crypto.dart';

class NetworkSecurity {
  // Pinned fingerprints for api.dhyan.app (Example SHA-256 fingerprints)
  // Always include at least 2 for rotation safety
  static const List<String> _allowedFingerprints = [
    "A3:4F:9E:0D:3C:8A:2F:B1:0E:5D:6C:7B:8A:9B:0C:1D:2E:3F:40:51:62:73:84:95:06:17:28:39:40:51", // Primary
    "B2:1E:8D:0C:2B:7A:1F:A0:0D:4C:5B:6A:7B:8C:9D:0E:1F:2A:3B:4C:5D:6E:7F:80:91:02:13:24:35", // Backup
  ];

  static void setupPinning(Dio dio) {
    dio.httpClientAdapter = IOHttpClientAdapter(
      createHttpClient: () {
        final client = HttpClient();
        client.badCertificateCallback =
            (X509Certificate cert, String host, int port) {
              // 1. Check if the host is our API
              if (host == "api.dhyan.app") {
                // 2. Calculate the SHA-256 fingerprint of the certificate
                final certFingerprint = sha256
                    .convert(cert.der)
                    .toString()
                    .toUpperCase();

                // 3. Verify if it matches any of our pinned fingerprints
                final isPinned = _allowedFingerprints.any(
                  (pinned) =>
                      pinned.replaceAll(":", "") ==
                      certFingerprint.replaceAll(":", ""),
                );

                if (isPinned) {
                  return true; // Allow connection
                } else {
                  // Log security event (Sentry/Local)
                  return false; // Reject connection (MITM suspected)
                }
              }
              
              // Allow localhost emulators for rapid development
              if (host == "10.0.2.2" || host == "localhost" || host == "127.0.0.1") {
                return true;
              }
              
              return false; // Default: Reject others for strictness
            };
        return client;
      },
    );
  }
}
