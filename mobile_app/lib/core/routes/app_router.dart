import 'package:go_router/go_router.dart';
import 'package:sentry_flutter/sentry_flutter.dart';
import 'package:mobile_app/features/onboarding/presentation/screens/splash_screen.dart';
import 'package:mobile_app/features/onboarding/presentation/screens/welcome_screen.dart';
import 'package:mobile_app/features/onboarding/presentation/screens/profile_quiz_screen.dart';
import 'package:mobile_app/features/auth/presentation/screens/login_screen.dart';
import 'package:mobile_app/features/auth/presentation/screens/otp_screen.dart';
import 'package:mobile_app/features/main/presentation/screens/main_navigation_screen.dart';

/// Central route configuration for the Dhyan app.
///
/// Uses [GoRouter] for declarative, URL-based navigation.
/// Guard redirects can be added here later for auth state.
final GoRouter appRouter = GoRouter(
  initialLocation: '/',
  observers: [SentryNavigatorObserver()],
  routes: [
    GoRoute(
      path: '/',
      name: 'splash',
      builder: (context, state) => const SplashScreen(),
    ),
    GoRoute(
      path: '/welcome',
      name: 'welcome',
      builder: (context, state) => const WelcomeScreen(),
    ),
    GoRoute(
      path: '/login',
      name: 'login',
      builder: (context, state) => const LoginScreen(),
    ),
    GoRoute(
      path: '/otp',
      name: 'otp',
      builder: (context, state) {
        final extras = state.extra as Map<String, dynamic>? ?? {};
        final phoneNumber = extras['phoneNumber'] as String? ?? '';
        final verificationId = extras['verificationId'] as String? ?? '';
        return OtpScreen(
          phoneNumber: phoneNumber,
          verificationId: verificationId,
        );
      },
    ),
    GoRoute(
      path: '/quiz',
      name: 'quiz',
      builder: (context, state) => const ProfileQuizScreen(),
    ),
    GoRoute(
      path: '/home',
      name: 'home',
      builder: (context, state) => const MainNavigationScreen(),
    ),
  ],
);
