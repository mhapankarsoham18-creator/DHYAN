import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:sentry_flutter/sentry_flutter.dart';
import 'core/routes/app_router.dart';
import 'core/theme/app_theme.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_app_check/firebase_app_check.dart';

final class DhyanProviderObserver extends ProviderObserver {
  @override
  void didUpdateProvider(
    ProviderBase<Object?> provider,
    Object? previousValue,
    Object? newValue,
    ProviderContainer container,
  ) {
    debugPrint('Provider[${provider.name ?? provider.runtimeType}] updated');
  }
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Load environment variables based on release mode
  const envFileName = kReleaseMode ? '.env.production' : '.env.development';
  try {
    await dotenv.load(fileName: envFileName);
  } catch (e) {
    debugPrint('Warning: Could not load .env file ($envFileName) - $e');
  }

  // Read Sentry DSN from env (falls back to empty string = disabled)
  final sentryDsn = dotenv.env['SENTRY_DSN'] ?? '';

  // Initialize Sentry — wraps the entire app to capture errors automatically
  await SentryFlutter.init(
    (options) {
      options.dsn = sentryDsn;
      options.environment = kReleaseMode ? 'production' : 'development';
      options.tracesSampleRate = 0.3;
      options.profilesSampleRate = 0.1;
      // Only send events in release mode, or if DSN is explicitly set in dev
    },
    appRunner: () async {
      // 1. Global Error Boundary for UI Rendering Exceptions
      FlutterError.onError = (FlutterErrorDetails details) {
        debugPrint('=================== FLUTTER ERROR ===================');
        debugPrint(details.exceptionAsString());
        debugPrint(details.stack?.toString() ?? '');
        // Forward to Sentry
        Sentry.captureException(details.exception, stackTrace: details.stack);
      };

      // 2. Global Error Boundary for Async Dart Exceptions
      PlatformDispatcher.instance.onError = (error, stack) {
        debugPrint('=================== ASYNC ERROR ===================');
        debugPrint(error.toString());
        debugPrint(stack.toString());
        // Forward to Sentry
        Sentry.captureException(error, stackTrace: stack);
        return true; // Prevents the app from crashing entirely
      };

      try {
        await Firebase.initializeApp();
        
        // Enable App Check
        await FirebaseAppCheck.instance.activate(
          androidProvider: AndroidProvider.playIntegrity,
          appleProvider: AppleProvider.deviceCheck,
        );
        
      } catch (e, stack) {
        debugPrint('Critical: Firebase init failed. App may run in degraded mode: $e');
        debugPrint(stack.toString());
        Sentry.captureException(e, stackTrace: stack);
      }

      runApp(
        ProviderScope(
          observers: [DhyanProviderObserver()],
          child: const DhyanApp(),
        ),
      );
    },
  );
}

class DhyanApp extends ConsumerWidget {
  const DhyanApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp.router(
      title: 'Dhyan',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      routerConfig: appRouter,
    );
  }
}
