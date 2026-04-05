import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile_app/core/theme/app_theme.dart';
import 'package:mobile_app/core/providers/app_settings_provider.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(appSettingsProvider);
    final notifier = ref.read(appSettingsProvider.notifier);

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        leading: IconButton(
          onPressed: () => Scaffold.of(context).openDrawer(),
          icon: const Icon(Icons.menu_rounded, size: 22),
        ),
        title: const Text('Settings'),
      ),
      body: ListView(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        physics: const BouncingScrollPhysics(),
        children: [
          // ── App Preferences ─────────────────────
          _buildSectionHeader('APP PREFERENCES'),
          _buildToggleTile(
            icon: Icons.dark_mode_rounded,
            title: 'Dark Mode',
            subtitle: 'Always on for Dhyan',
            value: true,
            onChanged: (_) {},
          ),
          _buildToggleTile(
            icon: Icons.bolt_rounded,
            title: 'Simple Mode',
            subtitle: 'Simplify trading jargon',
            value: settings.isSimpleMode,
            onChanged: (_) => notifier.toggleSimpleMode(),
          ),
          _buildNavTile(
            icon: Icons.language_rounded,
            title: 'Language',
            trailing: settings.language,
            onTap: () {
              final newLang = settings.language == 'English' ? 'Hindi' : 'English';
              notifier.setLanguage(newLang);
            },
          ),
          const SizedBox(height: 24),

          // ── Notifications ───────────────────────
          _buildSectionHeader('NOTIFICATIONS'),
          _buildToggleTile(
            icon: Icons.notifications_active_rounded,
            title: 'Push Notifications',
            subtitle: 'Price alerts & order updates',
            value: true,
            onChanged: (_) {},
          ),
          _buildToggleTile(
            icon: Icons.volume_up_rounded,
            title: 'Alert Sounds',
            subtitle: 'Audible notification feedback',
            value: true,
            onChanged: (_) {},
          ),
          _buildToggleTile(
            icon: Icons.email_rounded,
            title: 'Email Reports',
            subtitle: 'Weekly portfolio summaries',
            value: false,
            onChanged: (_) {},
          ),
          const SizedBox(height: 24),

          // ── Security ────────────────────────────
          _buildSectionHeader('SECURITY'),
          _buildToggleTile(
            icon: Icons.fingerprint_rounded,
            title: 'Biometric Lock',
            subtitle: 'Secure app with fingerprint or face',
            value: false,
            onChanged: (_) {},
          ),
          _buildNavTile(
            icon: Icons.pin_rounded,
            title: 'Change PIN',
            trailing: '••••',
            onTap: () {},
          ),
          const SizedBox(height: 24),

          // ── About ───────────────────────────────
          _buildSectionHeader('ABOUT'),
          _buildNavTile(icon: Icons.info_outline_rounded, title: 'Version', trailing: '1.0.0', onTap: () {}),
          _buildNavTile(icon: Icons.description_outlined, title: 'Terms of Service', onTap: () {}),
          _buildNavTile(icon: Icons.privacy_tip_outlined, title: 'Privacy Policy', onTap: () {}),
          _buildNavTile(icon: Icons.favorite_rounded, title: 'Open Source Licenses', onTap: () {}),
          const SizedBox(height: 40),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12, left: 4),
      child: Text(
        title,
        style: AppTheme.labelMedium.copyWith(
          fontSize: 11,
          letterSpacing: 1.5,
          color: AppTheme.primary,
        ),
      ),
    );
  }

  Widget _buildToggleTile({
    required IconData icon,
    required String title,
    String? subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: AppTheme.premiumCard(),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: AppTheme.primary.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: AppTheme.textSecondary, size: 20),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(color: AppTheme.textPrimary, fontWeight: FontWeight.w500, fontSize: 14)),
                if (subtitle != null)
                  Text(subtitle, style: AppTheme.bodySmall.copyWith(fontSize: 11)),
              ],
            ),
          ),
          Switch(value: value, onChanged: onChanged),
        ],
      ),
    );
  }

  Widget _buildNavTile({
    required IconData icon,
    required String title,
    String? trailing,
    VoidCallback? onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        decoration: AppTheme.premiumCard(),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: AppTheme.primary.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(icon, color: AppTheme.textSecondary, size: 20),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Text(title, style: const TextStyle(color: AppTheme.textPrimary, fontWeight: FontWeight.w500, fontSize: 14)),
            ),
            if (trailing != null)
              Text(trailing, style: AppTheme.bodySmall),
            const SizedBox(width: 4),
            const Icon(Icons.chevron_right_rounded, color: AppTheme.textTertiary, size: 18),
          ],
        ),
      ),
    );
  }
}
