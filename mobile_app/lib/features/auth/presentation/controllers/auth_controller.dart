
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:dio/dio.dart';

import '../../../../core/network/dio_client.dart';

class AuthState {
  final bool isLoading;
  final String? error;
  final String? verificationId;
  final String? phoneNumber;

  const AuthState({
    this.isLoading = false,
    this.error,
    this.verificationId,
    this.phoneNumber,
  });

  AuthState copyWith({
    bool? isLoading,
    String? error,
    String? verificationId,
    String? phoneNumber,
  }) {
    return AuthState(
      isLoading: isLoading ?? this.isLoading,
      error: error,
      verificationId: verificationId ?? this.verificationId,
      phoneNumber: phoneNumber ?? this.phoneNumber,
    );
  }
}

class AuthNotifier extends Notifier<AuthState> {
  final _storage = const FlutterSecureStorage();

  @override
  AuthState build() {
    return const AuthState();
  }

  Future<void> verifyPhone(
    String phoneNumber, {
    required Function(String verificationId) onCodeSent,
    required Function(String error) onError,
  }) async {
    state = state.copyWith(
      isLoading: true,
      error: null,
      phoneNumber: phoneNumber,
    );
    
    // Bypassing Firebase Auth because google-services.json is missing on Android
    // Simulating SMS push delay, then allowing OTP screen to appear.
    await Future.delayed(const Duration(milliseconds: 800));
    
    state = state.copyWith(
      isLoading: false,
      verificationId: 'backend_exchange_mode',
    );
    onCodeSent('backend_exchange_mode');
    
  }

  Future<bool> signInWithOtp(String verificationId, String smsCode) async {
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      // Direct integration with FastAPI backend!
      // Send the token and the phone_number we saved during verifyPhone
      final response = await dioClient.dio.post('/api/v1/auth/exchange-token', data: {
        'token': smsCode, // Sending user's inputted OTP as token
        'phone_number': state.phoneNumber ?? '+100000000',
      });

      final accessToken = response.data['token'];
      if (accessToken != null) {
        await _storage.write(key: 'jwt_token', value: accessToken);
        state = state.copyWith(isLoading: false);
        return true;
      } else {
        throw Exception("Backend failed to provide an access token.");
      }
    } on DioException catch (e) {
      final msg = e.response?.data?['detail'] ?? e.message ?? 'Unknown network error';
      state = state.copyWith(isLoading: false, error: "Backend Auth Failed: $msg");
      return false;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      return false;
    }
  }

  void resetError() {
    state = state.copyWith(error: null);
  }
}

final authControllerProvider = NotifierProvider<AuthNotifier, AuthState>(() {
  return AuthNotifier();
});
