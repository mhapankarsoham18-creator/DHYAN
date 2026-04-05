import 'package:flutter_riverpod/flutter_riverpod.dart';

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository();
});

// Mock user model to replace firebase User dependency locally
class AppUser {
  final String uid;
  final String phoneNumber;
  AppUser({required this.uid, required this.phoneNumber});
}

final authStateChangesProvider = StreamProvider<AppUser?>((ref) {
  final authRepository = ref.watch(authRepositoryProvider);
  return authRepository.authStateChanges;
});

class AuthRepository {
  AuthRepository();

  Stream<AppUser?> get authStateChanges => const Stream.empty();
  AppUser? get currentUser => null;

  Future<void> signOut() async {
    // Handled by clearing secure storage locally
  }
}
