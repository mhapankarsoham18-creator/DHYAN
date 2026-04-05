import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Dhyan Premium Design System
/// Inspired by: Calm authority, Swiss-watch precision, minimal luxury.
/// 
/// Color philosophy: Deep obsidian base with teal authority + gold warmth.
/// Typography: Space Grotesk headlines, Inter body — clean & modern.

class AppTheme {
  // ─── Brand Colors ──────────────────────────────────────
  static const Color primary = Color(0xFF0A7A6E);       // Deep teal
  static const Color primaryLight = Color(0xFF12A594);   // Lighter teal
  static const Color background = Color(0xFF0D1117);     // Near-black
  static const Color accent = Color(0xFFC9A84C);         // Soft gold
  static const Color success = Color(0xFF2ECC71);        // Muted green
  static const Color danger = Color(0xFFE74C3C);         // Muted red
  static const Color info = Color(0xFF3498DB);           // Cool blue

  // ─── Surface Colors ────────────────────────────────────
  static const Color surface = Color(0xFF161B22);
  static const Color surfaceVariant = Color(0xFF21262D);
  static const Color surfaceElevated = Color(0xFF1C2330);

  // ─── Text Colors ───────────────────────────────────────
  static const Color textPrimary = Color(0xFFF0F6FC);
  static const Color textSecondary = Color(0xFF8B949E);
  static const Color textTertiary = Color(0xFF6E7681);

  // ─── Gradients ─────────────────────────────────────────
  static const LinearGradient primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFF0A7A6E), Color(0xFF12A594)],
  );

  static const LinearGradient cardGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFF1A2232), Color(0xFF161B22)],
  );

  static const LinearGradient goldGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFFC9A84C), Color(0xFFE8C96A)],
  );

  // ─── Spacing & Radius ──────────────────────────────────
  static const double radiusSm = 8.0;
  static const double radiusMd = 12.0;
  static const double radiusLg = 16.0;
  static const double radiusXl = 24.0;

  // ─── Text Styles (Premium Typography) ──────────────────
  static const String fontHeadline = 'SpaceGrotesk';
  static const String fontBody = 'Inter';

  static const TextStyle headlineLarge = TextStyle(
    fontFamily: fontHeadline,
    fontSize: 32,
    fontWeight: FontWeight.w700,
    color: textPrimary,
    letterSpacing: -0.5,
    height: 1.2,
  );

  static const TextStyle headlineMedium = TextStyle(
    fontFamily: fontHeadline,
    fontSize: 24,
    fontWeight: FontWeight.w600,
    color: textPrimary,
    letterSpacing: -0.3,
  );

  static const TextStyle headlineSmall = TextStyle(
    fontFamily: fontHeadline,
    fontSize: 18,
    fontWeight: FontWeight.w600,
    color: textPrimary,
  );

  static const TextStyle bodyLarge = TextStyle(
    fontFamily: fontBody,
    fontSize: 16,
    fontWeight: FontWeight.w400,
    color: textPrimary,
  );

  static const TextStyle bodyMedium = TextStyle(
    fontFamily: fontBody,
    fontSize: 14,
    fontWeight: FontWeight.w400,
    color: textSecondary,
  );

  static const TextStyle bodySmall = TextStyle(
    fontFamily: fontBody,
    fontSize: 12,
    fontWeight: FontWeight.w400,
    color: textTertiary,
  );

  static const TextStyle labelMedium = TextStyle(
    fontFamily: fontBody,
    fontSize: 12,
    fontWeight: FontWeight.w600,
    color: textSecondary,
    letterSpacing: 0.8,
  );

  static const TextStyle numberLarge = TextStyle(
    fontFamily: fontHeadline,
    fontSize: 36,
    fontWeight: FontWeight.w800,
    color: textPrimary,
    letterSpacing: -0.5,
  );

  static const TextStyle numberMedium = TextStyle(
    fontFamily: fontHeadline,
    fontSize: 22,
    fontWeight: FontWeight.w700,
    color: textPrimary,
  );

  // ─── ThemeData ─────────────────────────────────────────
  static final ThemeData darkTheme = ThemeData(
    brightness: Brightness.dark,
    primaryColor: primary,
    scaffoldBackgroundColor: background,
    fontFamily: fontBody,
    colorScheme: const ColorScheme.dark(
      primary: primary,
      secondary: accent,
      surface: surface,
      error: danger,
      onPrimary: Colors.white,
      onSecondary: background,
      onSurface: textPrimary,
      onError: Colors.white,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: background,
      elevation: 0,
      scrolledUnderElevation: 0,
      surfaceTintColor: Colors.transparent,
      systemOverlayStyle: SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.light,
      ),
      iconTheme: IconThemeData(color: textPrimary),
      titleTextStyle: TextStyle(
        fontFamily: fontHeadline,
        color: textPrimary,
        fontSize: 20,
        fontWeight: FontWeight.w600,
        letterSpacing: -0.3,
      ),
    ),
    cardTheme: CardThemeData(
      color: surface,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(radiusLg),
        side: BorderSide(color: surfaceVariant.withValues(alpha: 0.5), width: 0.5),
      ),
    ),
    drawerTheme: const DrawerThemeData(
      backgroundColor: surface,
      surfaceTintColor: Colors.transparent,
    ),
    switchTheme: SwitchThemeData(
      thumbColor: WidgetStateProperty.resolveWith((states) =>
          states.contains(WidgetState.selected) ? primary : textTertiary),
      trackColor: WidgetStateProperty.resolveWith((states) =>
          states.contains(WidgetState.selected) ? primary.withValues(alpha: 0.3) : surfaceVariant),
    ),
    dividerTheme: const DividerThemeData(
      color: surfaceVariant,
      thickness: 0.5,
      space: 0,
    ),
    bottomSheetTheme: BottomSheetThemeData(
      backgroundColor: surface,
      surfaceTintColor: Colors.transparent,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(radiusXl)),
      ),
    ),
    snackBarTheme: SnackBarThemeData(
      backgroundColor: surfaceElevated,
      contentTextStyle: bodyMedium.copyWith(color: textPrimary),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(radiusMd)),
      behavior: SnackBarBehavior.floating,
    ),
  );

  // ─── Helper: Premium Card Decoration ───────────────────
  static BoxDecoration premiumCard({bool elevated = false}) {
    return BoxDecoration(
      gradient: cardGradient,
      borderRadius: BorderRadius.circular(radiusLg),
      border: Border.all(
        color: surfaceVariant.withValues(alpha: elevated ? 0.8 : 0.4),
        width: 0.5,
      ),
      boxShadow: elevated
          ? [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.3),
                blurRadius: 24,
                offset: const Offset(0, 8),
              ),
            ]
          : null,
    );
  }

  // ─── Glassmorphism Card ────────────────────────────────
  static BoxDecoration glassCard() {
    return BoxDecoration(
      color: surface.withValues(alpha: 0.7),
      borderRadius: BorderRadius.circular(radiusLg),
      border: Border.all(
        color: surfaceVariant.withValues(alpha: 0.3),
        width: 0.5,
      ),
    );
  }
}
