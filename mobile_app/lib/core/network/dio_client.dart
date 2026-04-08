import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'package:mobile_app/core/network/network_security.dart';
import 'package:mobile_app/core/services/device_fingerprint_service.dart';

import 'package:firebase_app_check/firebase_app_check.dart';

class DioClient {
  static final DioClient _instance = DioClient._internal();
  late final Dio dio;

  // Use a secure storage instance to retrieve auth tokens
  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  
  // Stream to notify the app router about 401 Unauthorized errors
  final _unauthorizedStreamController = StreamController<bool>.broadcast();
  Stream<bool> get onUnauthorized => _unauthorizedStreamController.stream;

  factory DioClient() {
    return _instance;
  }

  DioClient._internal() {
    // Read the API base URL from the loaded dotenv
    final String baseUrl = dotenv.env['API_URL'] ?? 'http://localhost:8000';

    dio = Dio(
      BaseOptions(
        baseUrl: baseUrl,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 10),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    _attachInterceptors();
    NetworkSecurity.setupPinning(dio);
  }

  void _attachInterceptors() {
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          // Add Firebase App Check header
          try {
            final appCheckToken = await FirebaseAppCheck.instance.getToken();
            if (appCheckToken != null) {
              options.headers['X-Firebase-AppCheck'] = appCheckToken;
            }
          } catch (e) {
             // Ignore if Firebase failed to initialize
          }
          
          // Add Device Fingerprint for Free Tier Rate Limiting
          try {
            final fingerprint = await deviceFingerprintService.getFingerprint();
            options.headers['X-Device-Fingerprint'] = fingerprint;
          } catch (e) {
            // Ignore if fingerprint fails, backend should rate limit IP fallback or reject
          }

          // Attempt to retrieve a saved JWT
          final token = await _storage.read(key: 'jwt_token');
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          
          if (kDebugMode) {
            debugPrint('--> ${options.method.toUpperCase()} ${options.baseUrl}${options.path}');
          }
          return handler.next(options);
        },
        onResponse: (response, handler) {
          if (kDebugMode) {
            debugPrint('<-- ${response.statusCode} ${response.requestOptions.path}');
          }
          return handler.next(response);
        },
        onError: (DioException e, handler) async {
          if (kDebugMode) {
            debugPrint('<-- ERROR ${e.response?.statusCode} ${e.requestOptions.path}');
            debugPrint(e.message);
          }
          
          // Global 401 Unauthorized handling (trigger logout)
          if (e.response?.statusCode == 401) {
            await _storage.delete(key: 'jwt_token');
            _unauthorizedStreamController.add(true);
          }

          return handler.next(e);
        },
      ),
    );
  }
}

// Global provider for the HTTP client
final dioClient = DioClient();
